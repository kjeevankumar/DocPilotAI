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
from backend.config import HOST, PORT

app = FastAPI(
    title="DocPilot AI API",
    description="Autonomous Document Intelligence Agent API running on Google Gemini models.",
    version="1.0"
)

# CORS Policy configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
