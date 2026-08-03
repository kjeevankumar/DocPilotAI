import sys
from pathlib import Path

# Add project root and backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import api
from backend.config import HOST, PORT, GEMINI_API_KEY

app = FastAPI(
    title="DocPilot AI API",
    description="Autonomous Document Intelligence Agent API running on Google Gemini models.",
    version="1.0"
)

# ── STARTUP API KEY VALIDATION ────────────────────────────────────────────────
_key = GEMINI_API_KEY or ""
print(f"\n{'#'*70}")
print(f"[STARTUP] DocPilot AI Backend initializing...")
if not _key:
    print(f"[STARTUP] ❌ CRITICAL: GEMINI_API_KEY is NOT set in backend/.env")
    print(f"[STARTUP]    All Gemini calls will fall back to heuristics (identical outputs).")
elif not _key.startswith("AIzaSy"):
    print(f"[STARTUP] ⚠️  WARNING: GEMINI_API_KEY does not look like a valid Gemini key.")
    print(f"[STARTUP]    Gemini keys start with 'AIzaSy...'. Current key starts with: '{_key[:10]}...'")
    print(f"[STARTUP]    All Gemini calls will likely fail with 401/403 and fall back to heuristics.")
    print(f"[STARTUP]    Get a valid key at: https://aistudio.google.com/app/apikey")
else:
    print(f"[STARTUP] ✅ GEMINI_API_KEY is configured and looks valid (starts with 'AIzaSy').")
print(f"{'#'*70}\n")
# ─────────────────────────────────────────────────────────────────────────────


# ── CORS Policy ─────────────────────────────────────────────────────────────
# IMPORTANT: `allow_origins` uses EXACT matching. A hardcoded Vercel preview
# URL breaks on every new deployment because Vercel generates a new subdomain.
# Solution: use `allow_origin_regex` to match ALL *.vercel.app subdomains plus
# localhost variants used in development.
origins = [
    # Local development
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # Regex covers ALL Vercel deployments: production alias + every preview URL
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)
# ─────────────────────────────────────────────────────────────────────────────

# Include Router
app.include_router(api.router, prefix="/api")

@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "DocPilot AI Backend",
        "version": "1.0"
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
