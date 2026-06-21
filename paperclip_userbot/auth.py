"""Authorization helper for the userbot.

Supports modes:
1. Interactive: prompts for phone and confirmation code via stdin.
2. Non-interactive: set PHONE_NUMBER env var and PHONE_CODE env var.
3. Two-step: first run with SEND_CODE_ONLY=1 to send the code, then run with PHONE_CODE.
"""

import asyncio
import logging
import os

from pyrogram import Client

from paperclip_userbot.config import API_HASH, API_ID, DATA_DIR, PHONE_NUMBER, SESSION_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_code(phone_number: str) -> None:
    client = Client(
        name=str(DATA_DIR / SESSION_NAME),
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=phone_number,
        workdir=str(DATA_DIR),
        no_updates=True,
    )
    try:
        await client.connect()
        sent = await client.send_code(phone_number)
        logger.info("Confirmation code sent to %s (phone_code_hash=%s)", phone_number, sent.phone_code_hash)
    finally:
        await client.disconnect()


async def authorize(phone_number: str, phone_code: str) -> None:
    client = Client(
        name=str(DATA_DIR / SESSION_NAME),
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=phone_number,
        phone_code=phone_code,
        workdir=str(DATA_DIR),
        no_updates=True,
    )
    await client.start()
    me = await client.get_me()
    logger.info("Authorized as @%s (id=%s)", me.username, me.id)
    await client.stop()


async def interactive() -> None:
    client = Client(
        name=str(DATA_DIR / SESSION_NAME),
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=PHONE_NUMBER or None,
        workdir=str(DATA_DIR),
    )
    await client.start()
    me = await client.get_me()
    logger.info("Authorized as @%s (id=%s)", me.username, me.id)
    await client.stop()


async def main() -> None:
    send_only = os.environ.get("SEND_CODE_ONLY", "").lower() in ("1", "true", "yes")
    phone_code = os.environ.get("PHONE_CODE")
    phone_number = PHONE_NUMBER or os.environ.get("PHONE_NUMBER")

    if send_only:
        if not phone_number:
            logger.error("Set PHONE_NUMBER env var to send the confirmation code")
            raise SystemExit(1)
        await send_code(phone_number)
        return

    if phone_code:
        if not phone_number:
            logger.error("Set PHONE_NUMBER env var together with PHONE_CODE")
            raise SystemExit(1)
        await authorize(phone_number, phone_code)
        return

    await interactive()


if __name__ == "__main__":
    asyncio.run(main())
