#!/usr/bin/env python3
"""
Helper script to update YouTube cookies for the download service.

This script provides guidance on how to update cookies when YouTube bot detection occurs.
"""

import os
import sys
from pathlib import Path

def main():
    """Main function to guide users through cookie updates."""
    print("🍪 YouTube Cookie Update Helper")
    print("=" * 50)
    
    cookies_path = Path(__file__).parent / "cookies" / "youtube.txt"
    
    print(f"\nCurrent cookies file location: {cookies_path}")
    
    if cookies_path.exists():
        print("✅ Cookies file exists")
        
        # Check file modification time
        import time
        mod_time = cookies_path.stat().st_mtime
        age_days = (time.time() - mod_time) / (24 * 3600)
        
        print(f"📅 File last modified: {age_days:.1f} days ago")
        
        if age_days > 30:
            print("⚠️  Warning: Cookies are older than 30 days and may be expired")
        elif age_days > 7:
            print("💡 Consider updating cookies as they're getting old")
        else:
            print("✅ Cookies are relatively fresh")
    else:
        print("❌ Cookies file not found")
    
    print("\n" + "=" * 50)
    print("📋 How to update your cookies:")
    print("\n1. **Using Browser Extension (Recommended):**")
    print("   - Install 'Get cookies.txt' or 'cookies.txt' extension")
    print("   - Go to youtube.com and log in")
    print("   - Click the extension and export cookies")
    print("   - Save as 'youtube.txt' in backend/cookies/")
    
    print("\n2. **Using Command Line (Advanced):**")
    print("   - Use tools like 'browser_cookie3' or 'youtube-dl' with --cookies-from-browser")
    
    print("\n3. **Manual Method:**")
    print("   - Open browser dev tools (F12)")
    print("   - Go to Application/Storage > Cookies > https://youtube.com")
    print("   - Copy relevant cookies and format as Netscape cookie file")
    
    print("\n" + "=" * 50)
    print("🔧 Environment Variables:")
    print("   Set YOUTUBE_COOKIES_PATH to use a custom cookies file location")
    
    print("\n" + "=" * 50)
    print("🚨 If you're still getting bot detection errors:")
    print("   - Wait 10-15 minutes before trying again")
    print("   - Try using a VPN or different IP address")
    print("   - Make sure you're logged into YouTube in your browser")
    print("   - Consider using a different user agent")
    
    print("\n✅ After updating cookies, try your download again!")

if __name__ == "__main__":
    main()
