"""Pyrogram client wrapper for Paperclip userbot."""

import asyncio
import logging
import os
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import Message

from paperclip_userbot.config import (
    API_HASH,
    API_ID,
    DATA_DIR,
    LOG_LEVEL,
    PHONE_NUMBER,
    SESSION_NAME,
    SESSION_STRING_FILE,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))


def _api_credentials() -> tuple[int, str]:
    api_id = API_ID or int(os.environ.get("API_ID", "0"))
    api_hash = API_HASH or os.environ.get("API_HASH", "")
    if not api_id or not api_hash:
        raise RuntimeError("API_ID and API_HASH must be set in .env or environment")
    return api_id, api_hash


class Userbot:
    """Shared Pyrogram client + in-memory message sink for wait operations."""

    def __init__(self) -> None:
        api_id, api_hash = _api_credentials()
        self.client = Client(
            name=str(DATA_DIR / SESSION_NAME),
            api_id=api_id,
            api_hash=api_hash,
            phone_number=PHONE_NUMBER or None,
            no_updates=False,
            workdir=str(DATA_DIR),
        )
        self._message_queue: asyncio.Queue[Message] = asyncio.Queue()
        self._lock = asyncio.Lock()
        self._ready = asyncio.Event()
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        @self.client.on(filters.private)
        async def _on_private(_client: Client, message: Message) -> None:
            logger.debug("Received private message from %s: %s", message.chat.id, message.text)
            await self._message_queue.put(message)

    async def start(self) -> None:
        await self.client.start()
        self._ready.set()
        logger.info("Userbot started as @%s", self.client.me.username if self.client.me else "unknown")

    async def stop(self) -> None:
        await self.client.stop()
        self._ready.clear()
        logger.info("Userbot stopped")

    async def wait_ready(self) -> None:
        await self._ready.wait()

    async def send_message(self, peer: str, text: str) -> Message:
        await self.wait_ready()
        logger.info("Sending message to %s", peer)
        return await self.client.send_message(chat_id=peer, text=text)

    async def get_history(self, peer: str, limit: int = 20) -> list[Message]:
        await self.wait_ready()
        logger.info("Getting history for %s (limit=%s)", peer, limit)
        messages = []
        async for message in self.client.get_chat_history(chat_id=peer, limit=limit):
            messages.append(message)
        return messages

    async def wait_for_message(
        self,
        peer: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Optional[Message]:
        await self.wait_ready()
        timeout = timeout or 60
        logger.info("Waiting for message from %s (timeout=%s)", peer, timeout)
        deadline = asyncio.get_event_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_event_loop().time()
            if remaining <= 0:
                return None
            try:
                message = await asyncio.wait_for(self._message_queue.get(), timeout=remaining)
            except asyncio.TimeoutError:
                return None
            if peer is None or self._message_matches_peer(message, peer):
                return message
            # Not our peer; put it back? Dropping is simpler; full history is available via /history.

    @staticmethod
    def _message_matches_peer(message: Message, peer: str) -> bool:
        if peer.startswith("@"):
            username = peer.lstrip("@")
            return bool(message.chat and message.chat.username and message.chat.username.lower() == username.lower())
        try:
            chat_id = int(peer)
        except ValueError:
            return False
        return message.chat.id == chat_id if message.chat else False


# Singleton instance used by the FastAPI app.
_bot: Optional[Userbot] = None


def get_userbot() -> Userbot:
    if _bot is None:
        raise RuntimeError("Userbot not initialized")
    return _bot


async def init_userbot() -> Userbot:
    global _bot
    if _bot is None:
        _bot = Userbot()
        await _bot.start()
    return _bot


async def shutdown_userbot() -> None:
    global _bot
    if _bot is not None:
        await _bot.stop()
        _bot = None
