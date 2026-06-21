"""FastAPI app exposing userbot operations to Paperclip agents."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from paperclip_userbot.bot import get_userbot, init_userbot, shutdown_userbot
from paperclip_userbot.config import DEFAULT_HISTORY_LIMIT, MAX_HISTORY_LIMIT, WAIT_TIMEOUT_SEC

logger = logging.getLogger(__name__)


class SendRequest(BaseModel):
    peer: str = Field(..., description="Username (@bot), chat id, or phone number")
    text: str = Field(..., description="Message text")


class WaitRequest(BaseModel):
    peer: Optional[str] = Field(None, description="Username or chat id to filter on")
    timeout: Optional[float] = Field(None, description="Timeout in seconds (default from env)")


class MessageOut(BaseModel):
    id: int
    date: str
    chat_id: Optional[int] = None
    chat_username: Optional[str] = None
    chat_title: Optional[str] = None
    from_user_id: Optional[int] = None
    from_user_username: Optional[str] = None
    text: Optional[str] = None
    caption: Optional[str] = None
    media: bool = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting userbot from FastAPI lifespan")
    await init_userbot()
    yield
    logger.info("Shutting down userbot")
    await shutdown_userbot()


app = FastAPI(title="Paperclip Userbot API", lifespan=lifespan)


def _message_to_dict(message) -> dict:
    chat = message.chat
    from_user = message.from_user
    return {
        "id": message.id,
        "date": message.date.isoformat() if message.date else None,
        "chat_id": chat.id if chat else None,
        "chat_username": chat.username if chat else None,
        "chat_title": getattr(chat, "title", None) or (chat.first_name if chat else None),
        "from_user_id": from_user.id if from_user else None,
        "from_user_username": from_user.username if from_user else None,
        "text": message.text or message.caption,
        "caption": message.caption,
        "media": bool(message.media),
    }


@app.get("/health")
async def health():
    bot = get_userbot()
    try:
        await asyncio.wait_for(bot.wait_ready(), timeout=5)
        me = bot.client.me
        return {
            "status": "ok",
            "username": me.username if me else None,
            "id": me.id if me else None,
        }
    except asyncio.TimeoutError:
        raise HTTPException(status_code=503, detail="Userbot not ready")


@app.post("/send", response_model=MessageOut)
async def send_message(req: SendRequest):
    bot = get_userbot()
    try:
        sent = await bot.send_message(req.peer, req.text)
        return _message_to_dict(sent)
    except Exception as exc:
        logger.exception("Failed to send message to %s", req.peer)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/history/{peer}", response_model=list[MessageOut])
async def get_history(
    peer: str,
    limit: int = Query(DEFAULT_HISTORY_LIMIT, ge=1, le=MAX_HISTORY_LIMIT),
):
    bot = get_userbot()
    try:
        messages = await bot.get_history(peer, limit=limit)
        return [_message_to_dict(m) for m in reversed(messages)]
    except Exception as exc:
        logger.exception("Failed to get history for %s", peer)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/wait", response_model=Optional[MessageOut])
async def wait_for_message(req: WaitRequest):
    bot = get_userbot()
    timeout = req.timeout or WAIT_TIMEOUT_SEC
    try:
        message = await bot.wait_for_message(req.peer, timeout=timeout)
        if message is None:
            raise HTTPException(status_code=408, detail="Timeout waiting for message")
        return _message_to_dict(message)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed while waiting for message")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
