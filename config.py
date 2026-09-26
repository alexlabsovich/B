import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("8416010350:AAHvoGxRI4mgC1GE0P7nL4r5DKDKDkc_5sM")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "8373993954"))

OPENROUTER_API_KEY = os.getenv("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")
OPENROUTER_MODEL = "inclusionai/ling-3.0-flash-fin:free"

TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "userbot_session")

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
AVATARS_DIR = os.path.join(DATA_DIR, "avatars")

CHANNELS_FILE = os.path.join(DATA_DIR, "channels.json")
TRACKED_CHANNELS_FILE = os.path.join(DATA_DIR, "tracked_channels.json")
