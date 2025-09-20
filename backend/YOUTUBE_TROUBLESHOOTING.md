# YouTube Download Troubleshooting Guide

This guide helps resolve common issues with YouTube video downloads, particularly the "Sign in to confirm you're not a bot" error.

## Quick Fix

If you're getting bot detection errors:

1. **Update your cookies file:**
   ```bash
   python update_cookies.py
   ```

2. **Test the download:**
   ```bash
   python test_download.py
   ```

## Common Issues & Solutions

### 1. "Sign in to confirm you're not a bot" Error

This is YouTube's bot detection system blocking automated requests.

**Solutions (in order of preference):**

1. **Use Browser Cookies:**
   - Install "Get cookies.txt" browser extension
   - Log into YouTube in your browser
   - Export cookies and save as `backend/cookies/youtube.txt`

2. **Use Browser Integration:**
   - The system will automatically try to use Chrome/Firefox cookies
   - Make sure you're logged into YouTube in your browser

3. **Wait and Retry:**
   - Wait 10-15 minutes before trying again
   - YouTube's detection is often temporary

4. **Change IP Address:**
   - Use a VPN or different IP address
   - Restart your router if you have a dynamic IP

### 2. Cookie File Issues

**Check if cookies are valid:**
```bash
python -c "from services.download import _validate_cookies, _resolve_cookies_path; print(_validate_cookies(_resolve_cookies_path()))"
```

**Common cookie problems:**
- Cookies are expired (older than 6 months)
- Cookies are from a different account
- Cookies file format is incorrect
- Browser isn't logged into YouTube

### 3. Rate Limiting

YouTube may block requests if you download too many videos too quickly.

**Solutions:**
- Add delays between downloads
- Use the built-in retry mechanism (already implemented)
- Implement your own rate limiting

### 4. Network Issues

**Check your connection:**
- Ensure stable internet connection
- Try downloading from a different network
- Check if your ISP blocks YouTube

## Advanced Configuration

### Environment Variables

```bash
# Custom cookies file location
export YOUTUBE_COOKIES_PATH="/path/to/your/cookies.txt"

# Custom download directory
export YOUTUBE_DOWNLOAD_DIR="/path/to/downloads"
```

### Manual Cookie Export

1. **Using Browser Extension:**
   - Install "Get cookies.txt" extension
   - Go to youtube.com and log in
   - Click extension → Export → Save as `youtube.txt`

2. **Using Developer Tools:**
   - Open YouTube in browser
   - Press F12 → Application → Cookies → https://youtube.com
   - Copy relevant cookies and format as Netscape cookie file

3. **Using Command Line:**
   ```bash
   # Extract from browser (if available)
   yt-dlp --cookies-from-browser chrome --print-json "https://youtube.com/watch?v=dQw4w9WgXcQ"
   ```

## Production Deployment

### Render.com Setup

1. **Set environment variables:**
   ```
   YOUTUBE_COOKIES_PATH=/etc/secrets/youtube_cookies.txt
   YOUTUBE_DOWNLOAD_DIR=/tmp/youtube_downloads
   ```

2. **Create secrets file:**
   - Upload fresh cookies to Render secrets
   - Update regularly (every 3-6 months)

3. **Monitor logs:**
   - Watch for bot detection errors
   - Set up alerts for failed downloads

### Cookie Refresh Automation

Consider implementing automatic cookie refresh:

```python
# Example: Check cookie age and refresh if needed
def refresh_cookies_if_needed():
    cookies_file = _resolve_cookies_path()
    if cookies_file and _validate_cookies(cookies_file):
        mod_time = cookies_file.stat().st_mtime
        age_days = (time.time() - mod_time) / (24 * 3600)
        if age_days > 30:
            # Trigger cookie refresh process
            notify_admin("Cookies need refresh")
```

## Testing

### Run Tests

```bash
# Test cookie validation
python test_download.py

# Test with specific video
python -c "from services.download import process_download; print(process_download('https://youtube.com/watch?v=dQw4w9WgXcQ'))"
```

### Debug Mode

Enable verbose logging by setting:
```python
ydl_opts["verbose"] = True
ydl_opts["quiet"] = False
```

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Sign in to confirm you're not a bot" | Bot detection | Update cookies, wait, or change IP |
| "Video unavailable" | Video is private/deleted | Check video URL and permissions |
| "No video formats found" | YouTube changed format | Update yt-dlp version |
| "Cookies file not found" | Missing cookies | Export fresh cookies |

## Best Practices

1. **Keep yt-dlp updated:**
   ```bash
   pip install --upgrade yt-dlp
   ```

2. **Refresh cookies regularly:**
   - Every 3-6 months
   - After getting bot detection errors
   - When switching YouTube accounts

3. **Use appropriate delays:**
   - Don't download too many videos at once
   - Add delays between requests
   - Respect YouTube's rate limits

4. **Monitor for changes:**
   - Watch yt-dlp GitHub for updates
   - Monitor YouTube's changes
   - Update your code accordingly

## Getting Help

1. **Check logs:**
   - Enable verbose logging
   - Look for specific error messages
   - Check network connectivity

2. **Test manually:**
   ```bash
   yt-dlp --verbose "https://youtube.com/watch?v=VIDEO_ID"
   ```

3. **Community resources:**
   - yt-dlp GitHub issues
   - YouTube-DL community forums
   - Stack Overflow

## Legal Notice

Always ensure you have the right to download content and comply with YouTube's Terms of Service. This tool is for educational and personal use only.
