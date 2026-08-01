import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Application Configurations
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

# File Settings
MAX_UPLOAD_SIZE = 15 * 1024 * 1024  # 15MB
SUPPORTED_FORMATS = {".pdf", ".png", ".jpg", ".jpeg"}

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
