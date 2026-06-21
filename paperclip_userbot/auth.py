"""Authorization helper for the userbot.

Supports modes:
1. Interactive: prompts for api_id, api_hash, phone and confirmation code via stdin.
2. Non-interactive: set API_ID, API_HASH, PHONE_NUMBER env vars and PHONE_CODE env var.
3. Two-step: first run with SEND_CODE_ONLY=1 to send the code, then run with PHONE_CODE.
"""

import asyncio
import logging
import os

from pyrogram import Client

from paperclip_userbot.config import API_HASH, API_ID, DATA_DIR, PHONE_NUMBER, SESSION_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def prompt(prompt_text: str) -> str:
    try:
        import termios
        import tty
        import sys
        print(prompt_text, end="", flush=True)
        tty.setcbreak(sys.stdin.fileno())
        chars = []
        while True:
            ch = sys.stdin.read(1)
            if ch in ("\n", "\r"):
                break
            chars.append(ch)
            sys.stdout.write("*")
            sys.stdout.flush()
        print()
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, termios.tcgetattr(sys.stdin.fileno()))
        return "".join(chars)
    except Exception:
        return input(prompt_text)


async def _get_credentials() -> tuple[int, str, str]:
    api_id = API_ID
    api_hash = API_HASH
    phone_number = PHONE_NUMBER

    if not api_id:
        api_id = int(input("Enter API ID: ").strip())
    if not api_hash:
        api_hash = input("Enter API hash: ").strip()
    if not phone_number:
        phone_number = input("Enter phone number (with + and country code): ").strip()

    return api_id, api_hash, phone_number


async def send_code(phone_number: str) -> None:
    api_id, api_hash, _ = await _get_credentials()
    client = Client(
        name=str(DATA_DIR / SESSION_NAME),
        api_id=api_id,
        api_hash=api_hash,
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
    api_id, api_hash, _ = await _get_credentials()
    client = Client(
        name=str(DATA_DIR / SESSION_NAME),
        api_id=api_id,
        api_hash=api_hash,
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
    api_id, api_hash, phone_number = await _get_credentials()
    client = Client(
        name=str(DATA_DIR / SESSION_NAME),
        api_id=api_id,
        api_hash=api_hash,
        phone_number=phone_number,
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
