"""
kosha — Fast Sanskrit Dictionary Lookup Service

Entry point for FastAPI application.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Create app
app = FastAPI(
    title=os.getenv('API_TITLE', 'kosha'),
    description=os.getenv('API_DESCRIPTION', 'Fast Sanskrit Dictionary Lookup'),
    version=os.getenv('API_VERSION', '1.0.0'),
)

# CORS middleware
cors_origins = os.getenv('CORS_ORIGINS', '["*"]')
import json
try:
    origins = json.loads(cors_origins)
except:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Routers (placeholder; to be implemented in Phase 1–2)
@app.get("/")
def root():
    """Root endpoint; redirect to search page."""
    return {
        "message": "kosha — Sanskrit Dictionary Lookup",
        "docs": "/docs",
        "ui": "/search",  # Future: link to search page
    }

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}

# TODO: Add routers
# from app.routers import lemma, scan
# app.include_router(lemma.router)
# app.include_router(scan.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
