import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl

from services.download import DEFAULT_DOWNLOAD_ROOT, DownloadError, process_download

app = FastAPI(
    title="Indicators Backend",
    version="0.1.1",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ⚠️ In production, restrict this to your exact Firebase domain (e.g., https://your-site.web.app).
ALLOWED_ORIGINS = [
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://*.web.app",
    "https://*.firebaseapp.com",
    "*",  # <-- Development convenience only. Replace with explicit origins later.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.get("/api/weather")
def weather():
    # Example: Your Python code does the work
    import random
    from datetime import datetime
    
    # Simulate calling a weather API
    temperature = random.randint(15, 30)
    conditions = ["Sunny", "Cloudy", "Rainy", "Windy"]
    condition = random.choice(conditions)
    
    # Your calculations
    feels_like = temperature + random.randint(-3, 3)
    humidity = random.randint(40, 80)
    
    # Return processed data to frontend
    return {
        "temperature": f"{temperature}°C",
        "condition": condition,
        "feels_like": f"{feels_like}°C",
        "humidity": f"{humidity}%",
        "timestamp": datetime.now().strftime("%H:%M")
    }


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the Indicators backend"}


class YouTubeDownloadRequest(BaseModel):
    url: HttpUrl


def _download_root() -> Path:
    override = os.environ.get("YOUTUBE_DOWNLOAD_DIR")
    if override:
        return Path(override).expanduser()
    return DEFAULT_DOWNLOAD_ROOT


@app.post("/api/youtube/download")
def youtube_download(payload: YouTubeDownloadRequest):
    try:
        result = process_download(str(payload.url))
    except DownloadError as exc:  # pragma: no cover - passthrough for API consumers
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result


@app.get("/api/youtube/downloads/{video_id}")
def youtube_download_file(video_id: str):
    root = _download_root()
    file_path = root / video_id / f"{video_id}.mp4"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video not found.")
    return FileResponse(file_path, media_type="video/mp4", filename=file_path.name)


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
