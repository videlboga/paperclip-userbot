"""Interactive authorization helper for the userbot."""

import asyncio
import logging

from pyrogram import Client

from paperclip_userbot.config import API_HASH, API_ID, DATA_DIR, PHONE_NUMBER, SESSION_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Starting interactive authorization for %s", PHONE_NUMBER or "unknown phone")
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


if __name__ == "__main__":
    asyncio.run(main())
