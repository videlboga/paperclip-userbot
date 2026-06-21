"""Entry point for the Paperclip userbot API server."""

import uvicorn
from paperclip_userbot.config import APP_HOST, APP_PORT, LOG_LEVEL

if __name__ == "__main__":
    uvicorn.run(
        "paperclip_userbot.api:app",
        host=APP_HOST,
        port=APP_PORT,
        log_level=LOG_LEVEL.lower(),
        reload=False,
    )
