"""Utilities for downloading YouTube videos via yt-dlp.

The module can be imported by FastAPI routes as well as executed directly
from the command line for manual testing. It handles optional cookie-based
sessions and configurable download roots.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

import yt_dlp
from dotenv import load_dotenv

# Ensure environment variables from a local .env are available when the module
# is imported (useful during local development). No-op on Render where vars are
# provided via the dashboard/secret files.
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR.parent
DEFAULT_DOWNLOAD_ROOT = Path(
    os.environ.get("YOUTUBE_DOWNLOAD_DIR", BACKEND_DIR / "downloads")
).expanduser()


class DownloadError(Exception):
    """Raised when yt-dlp fails to fetch a video."""


def get_video_id(url: str) -> str:
    """Extract the YouTube video ID from the provided URL."""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    video_id = query_params.get("v", [Path(parsed_url.path).name])[0]
    if not video_id:
        raise DownloadError("Unable to extract video ID from the URL.")
    return video_id


def _resolve_cookies_path(explicit_path: Optional[str | Path] = None) -> Optional[Path]:
    """Locate a cookies.txt file to authenticate YouTube requests."""
    candidates: list[Path] = []

    if explicit_path:
        candidates.append(Path(explicit_path))

    env_path = os.environ.get("YOUTUBE_COOKIES_PATH")
    if env_path:
        candidates.append(Path(env_path))

    # Common fallbacks (local dev, Render secret file, repo-relative path).
    candidates.extend(
        [
            Path("cookies.txt"),
            BACKEND_DIR / "cookies" / "youtube.txt",
            Path("/etc/secrets/youtube_cookies.txt"),
        ]
    )

    for candidate in candidates:
        candidate_path = candidate.expanduser()
        if not candidate_path.is_absolute():
            candidate_path = BACKEND_DIR / candidate_path
        if candidate_path.exists():
            return candidate_path

    return None


def download_video(
    url: str,
    video_id: str,
    destination: Path,
    *,
    cookies_file: Optional[Path] = None,
) -> Path:
    """Download a single YouTube video as MP4 using yt-dlp."""
    destination.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]",
        "outtmpl": str(destination / f"{video_id}.mp4"),
        "noplaylist": True,
        "quiet": False,
        "verbose": True,
        "merge_output_format": "mp4",
        "extractor_retries": 3,
        "fragment_retries": 3,
        "retries": 3,
        "sleep_interval": 1,
        "max_sleep_interval": 5,
        "cookiefile": str(cookies_file) if cookies_file else None,
        # Spoof a common browser to reduce bot checks.
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "referer": "https://www.youtube.com/",
        "origin": "https://www.youtube.com",
    }

    # yt-dlp complains about None cookiefile, so drop the key if we don't have it.
    if not cookies_file:
        ydl_opts.pop("cookiefile", None)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as exc:  # pragma: no cover - yt-dlp raises many custom errors
        raise DownloadError(f"yt-dlp failed: {exc}") from exc

    final_path = destination / f"{video_id}.mp4"
    if not final_path.exists():
        raise DownloadError(f"yt-dlp reported success but {final_path} is missing.")
    return final_path


def process_download(
    url: str,
    *,
    output_root: Optional[str | Path] = None,
    cookies_path: Optional[str | Path] = None,
) -> dict[str, str]:
    """High-level helper used by the API to fetch a video and report metadata."""
    video_id = get_video_id(url)

    root = Path(output_root or DEFAULT_DOWNLOAD_ROOT).expanduser()
    target_dir = root / video_id

    cookies_file = _resolve_cookies_path(cookies_path)

    video_file = download_video(url, video_id, target_dir, cookies_file=cookies_file)

    return {
        "video_id": video_id,
        "video_path": str(video_file),
        "filename": video_file.name,
        "download_url": f"/api/youtube/downloads/{video_id}",
    }


def _cli() -> None:
    """Manual entry point for quick local testing."""
    video_url = input("Enter the YouTube video URL: ").strip()
    if not video_url:
        print("No URL provided.")
        sys.exit(1)

    try:
        result = process_download(video_url)
    except DownloadError as exc:
        print(f"General error: {exc}")
        sys.exit(1)

    print(f"Video saved to {result['video_path']}")
    print(f"Download via API path: {result['download_url']}")


if __name__ == "__main__":
    _cli()
