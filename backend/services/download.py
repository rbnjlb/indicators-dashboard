"""Utilities for downloading YouTube videos via yt-dlp.

The module can be imported by FastAPI routes as well as executed directly
from the command line for manual testing. It handles optional cookie-based
sessions and configurable download roots.
"""

from __future__ import annotations

import os
import sys
import time
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


def _normalize_error_message(message: str) -> str:
    """Lowercase error messages and normalize apostrophes for matching."""
    return message.lower().replace("’", "'").replace("‘", "'")


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


def _test_browser_cookies(browser: str) -> bool:
    """Test if browser cookies are available and working."""
    try:
        browser_spec = (browser,)

        test_opts = {
            "cookiesfrombrowser": browser_spec,
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
        }

        with yt_dlp.YoutubeDL(test_opts) as ydl:
            # Try to extract info from a simple video without downloading
            info = ydl.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=False)
            return info is not None
    except Exception as e:
        # Don't print errors for browser cookie testing
        return False


def _validate_cookies(cookies_file: Path) -> bool:
    """Validate that the cookies file contains valid YouTube cookies."""
    try:
        if not cookies_file.exists():
            return False
            
        with open(cookies_file, 'r') as f:
            content = f.read()
            
        # Check for basic YouTube cookie indicators
        required_indicators = ['.youtube.com', 'TRUE', '/']
        if not all(indicator in content for indicator in required_indicators):
            return False
            
        # Check if cookies are not expired (basic check)
        lines = content.strip().split('\n')
        valid_cookies = 0
        
        for line in lines:
            if line.startswith('#') or not line.strip():
                continue
                
            parts = line.split('\t')
            if len(parts) >= 5:
                # Check expiration timestamp (5th field)
                try:
                    expiration = int(parts[4])
                    # If expiration is 0 (session cookie) or in the future
                    if expiration == 0 or expiration > int(time.time()):
                        valid_cookies += 1
                except (ValueError, IndexError):
                    continue
                    
        # Need at least a few valid cookies
        return valid_cookies >= 3
        
    except Exception:
        return False


def download_video(
    url: str,
    video_id: str,
    destination: Path,
    *,
    cookies_file: Optional[Path] = None,
) -> Path:
    """Download a single YouTube video as MP4 using yt-dlp."""
    destination.mkdir(parents=True, exist_ok=True)

    # Multiple user agents to rotate through if one fails
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
    ]

    last_exception = None
    
    # Validate cookies if provided
    valid_cookies = None
    if cookies_file and _validate_cookies(cookies_file):
        valid_cookies = cookies_file
        print(f"Using valid cookies from {cookies_file}")
    elif cookies_file:
        print(f"Warning: Cookies file {cookies_file} appears invalid or expired, will try without cookies")
    
    # Test which browser cookies are available
    available_browsers = []
    for browser in ["chrome", "firefox", "safari", "edge"]:
        if _test_browser_cookies(browser):
            available_browsers.append(browser)
            print(f"✅ {browser.capitalize()} cookies available")
        else:
            print(f"❌ {browser.capitalize()} cookies not available")
    
    # Try multiple strategies in order of preference
    strategies = []
    
    # Add file-based cookies first if valid
    if valid_cookies:
        strategies.append({"cookies": valid_cookies, "cookies_from_browser": None, "description": "with cookies file"})
    
    # Add available browser cookies
    for browser in available_browsers:
        strategies.append({"cookies": None, "cookies_from_browser": browser, "description": f"with browser cookies ({browser})"})
    
    # Always include a strategy without cookies as a final fallback
    strategies.append({"cookies": None, "cookies_from_browser": None, "description": "without cookies"})
    
    # Remove duplicates while preserving order
    seen = set()
    unique_strategies = []
    for strategy in strategies:
        key = (strategy["cookies"], strategy["cookies_from_browser"])
        if key not in seen:
            seen.add(key)
            unique_strategies.append(strategy)
    strategies = unique_strategies
    
    for strategy in strategies:
        for i, user_agent in enumerate(user_agents):
            ydl_opts = {
                "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[ext=mp4]",
                "outtmpl": str(destination / f"{video_id}.mp4"),
                "noplaylist": True,
                "quiet": False,
                "verbose": True,
                "merge_output_format": "mp4",
                "extractor_retries": 5,
                "fragment_retries": 5,
                "retries": 5,
                "sleep_interval": 2,
                "max_sleep_interval": 10,
                "user_agent": user_agent,
                "referer": "https://www.youtube.com/",
                "origin": "https://www.youtube.com",
                # Additional anti-detection measures
                "extractor_args": {
                    "youtube": {
                        "skip": ["dash", "hls"],  # Skip some formats that might trigger bot detection
                        "player_skip": ["configs"],  # Skip some player configs
                    }
                },
                # Use a more conservative approach
                "no_check_certificate": True,
                "ignoreerrors": False,
                # Add some randomization to avoid patterns
                "sleep_interval_subtitles": 1,
            }
            
            # Add cookies if available
            if strategy["cookies"]:
                ydl_opts["cookiefile"] = str(strategy["cookies"])
            elif strategy["cookies_from_browser"]:
                browser_spec = strategy["cookies_from_browser"]
                if isinstance(browser_spec, str):
                    browser_spec = (browser_spec,)
                ydl_opts["cookiesfrombrowser"] = browser_spec
                
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                final_path = destination / f"{video_id}.mp4"
                if final_path.exists():
                    return final_path
                    
            except Exception as exc:
                last_exception = exc
                error_msg = _normalize_error_message(str(exc))
                
                # If we get bot detection, try next strategy
                if any(phrase in error_msg for phrase in [
                    "sign in to confirm you're not a bot",
                    "bot detection",
                    "captcha",
                    "verify you are human",
                    "unusual traffic"
                ]):
                    print(f"Bot detection encountered with {strategy['description']} and user agent {i+1}, trying next...")
                    continue
                else:
                    # For other errors, don't retry
                    raise DownloadError(f"yt-dlp failed: {exc}") from exc
    
    # If all strategies failed
    if last_exception:
        error_msg = str(last_exception)
        normalized = _normalize_error_message(error_msg)
        if "sign in to confirm you're not a bot" in normalized:
            cookie_help = ""
            if not valid_cookies and not available_browsers:
                cookie_help = "\n\n🍪 COOKIE SETUP REQUIRED:\n" \
                            "1. Make sure you're logged into YouTube in your browser\n" \
                            "2. Or export cookies manually using 'Get cookies.txt' extension\n" \
                            "3. Save cookies as: backend/cookies/youtube.txt\n"
            
            raise DownloadError(
                "YouTube is blocking automated requests after trying all available methods.\n"
                f"Tried: {len(strategies)} different authentication strategies\n"
                f"Available browsers: {', '.join(available_browsers) if available_browsers else 'None'}\n"
                f"Valid cookies file: {'Yes' if valid_cookies else 'No'}\n"
                f"{cookie_help}"
                "OTHER SOLUTIONS:\n"
                "1. Wait 10-15 minutes before trying again\n"
                "2. Try using a VPN or different IP address\n"
                "3. Make sure you're logged into YouTube in your browser\n"
                f"\nOriginal error: {error_msg}"
            )
        else:
            raise DownloadError(f"yt-dlp failed after trying all strategies: {error_msg}") from last_exception
    else:
        raise DownloadError(f"yt-dlp reported success but {destination / f'{video_id}.mp4'} is missing.")


def _get_cookie_instructions() -> str:
    """Get instructions for updating cookies when bot detection occurs."""
    return """
To fix YouTube bot detection issues:

1. **Update your cookies file:**
   - Open YouTube in your browser and log in
   - Use a browser extension like "Get cookies.txt" or "cookies.txt"
   - Export cookies for youtube.com
   - Replace the cookies file at: backend/cookies/youtube.txt

2. **Alternative methods:**
   - Wait 10-15 minutes before trying again
   - Try using a different IP address or VPN
   - Use a different user agent by modifying the code

3. **For production deployment:**
   - Set YOUTUBE_COOKIES_PATH environment variable
   - Use Render secrets or similar to store fresh cookies
   - Consider implementing cookie refresh automation

4. **Check cookie expiration:**
   - YouTube cookies typically expire every 6 months
   - Session cookies expire when browser closes
   - Update cookies regularly to avoid issues
"""


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

    try:
        video_file = download_video(url, video_id, target_dir, cookies_file=cookies_file)
    except DownloadError as e:
        # Add helpful context to the error message
        error_msg = str(e)
        if "sign in to confirm you're not a bot" in _normalize_error_message(error_msg):
            enhanced_error = f"{error_msg}\n\n{_get_cookie_instructions()}"
            raise DownloadError(enhanced_error) from e
        else:
            raise

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
