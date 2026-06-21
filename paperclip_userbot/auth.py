"""Authorization helper for the userbot.

Supports two modes:
1. Interactive (default): prompts for the confirmation code via stdin.
2. Non-interactive: set PHONE_CODE env var to provide the code directly.
"""

import asyncio
import logging
import os

from pyrogram import Client

from paperclip_userbot.config import API_HASH, API_ID, DATA_DIR, PHONE_NUMBER, SESSION_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    phone_code = os.environ.get("PHONE_CODE")
    logger.info(
        "Starting authorization for %s (mode=%s)",
        PHONE_NUMBER or "unknown phone",
        "non-interactive" if phone_code else "interactive",
    )
    client = Client(
        name=str(DATA_DIR / SESSION_NAME),
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=PHONE_NUMBER or None,
        phone_code=phone_code,
        workdir=str(DATA_DIR),
    )
    await client.start()
    me = await client.get_me()
    logger.info("Authorized as @%s (id=%s)", me.username, me.id)
    await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
