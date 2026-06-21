"""Configuration for the userbot."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
SESSION_NAME = os.environ.get("SESSION_NAME", "paperclip_userbot")

API_ID = int(os.environ["API_ID"]) if os.environ.get("API_ID") else None
API_HASH = os.environ.get("API_HASH") or None
PHONE_NUMBER = os.environ.get("PHONE_NUMBER") or None

APP_HOST = os.environ.get("APP_HOST", "0.0.0.0")
APP_PORT = int(os.environ.get("APP_PORT", "8000"))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

WAIT_TIMEOUT_SEC = int(os.environ.get("WAIT_TIMEOUT_SEC", "60"))
DEFAULT_HISTORY_LIMIT = int(os.environ.get("DEFAULT_HISTORY_LIMIT", "20"))
MAX_HISTORY_LIMIT = int(os.environ.get("MAX_HISTORY_LIMIT", "100"))
