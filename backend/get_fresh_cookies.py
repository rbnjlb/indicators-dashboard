#!/usr/bin/env python3
"""
Script to help get fresh cookies from your browser for YouTube downloads.

This script will guide you through the process of getting fresh cookies
from your browser to bypass YouTube bot detection.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_yt_dlp_version():
    """Check if yt-dlp is installed and get version."""
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ yt-dlp version: {result.stdout.strip()}")
            return True
        else:
            print("❌ yt-dlp not found or not working")
            return False
    except FileNotFoundError:
        print("❌ yt-dlp not installed")
        return False

def test_browser_cookies():
    """Test which browsers have YouTube cookies available."""
    browsers = ["chrome", "firefox", "safari", "edge", "chromium", "brave"]
    available = []
    
    print("\n🔍 Testing browser cookies...")
    
    for browser in browsers:
        try:
            cmd = [
                'yt-dlp', 
                '--cookies-from-browser', browser,
                '--print-json',
                '--no-download',
                'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ {browser.capitalize()}: Cookies available")
                available.append(browser)
            else:
                print(f"❌ {browser.capitalize()}: No cookies or error")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {browser.capitalize()}: Timeout (may need login)")
        except Exception as e:
            print(f"❌ {browser.capitalize()}: Error - {e}")
    
    return available

def export_cookies_from_browser(browser):
    """Export cookies from browser using yt-dlp."""
    cookies_file = Path(__file__).parent / "cookies" / "youtube.txt"
    cookies_file.parent.mkdir(exist_ok=True)
    
    print(f"\n🍪 Exporting cookies from {browser}...")
    
    try:
        cmd = [
            'yt-dlp',
            '--cookies-from-browser', browser,
            '--cookies', str(cookies_file),
            '--print-json',
            '--no-download',
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and cookies_file.exists():
            print(f"✅ Cookies exported to: {cookies_file}")
            print(f"📊 File size: {cookies_file.stat().st_size} bytes")
            return True
        else:
            print(f"❌ Failed to export cookies: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - make sure you're logged into YouTube in your browser")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_download_with_cookies():
    """Test download with the exported cookies."""
    print("\n🧪 Testing download with exported cookies...")
    
    try:
        cmd = [
            'yt-dlp',
            '--cookies', str(Path(__file__).parent / "cookies" / "youtube.txt"),
            '--format', 'worst[ext=mp4]',  # Download worst quality for testing
            '--output', '/tmp/test_%(id)s.%(ext)s',
            '--print-json',
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Download test successful!")
            return True
        else:
            print(f"❌ Download test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Download test timeout")
        return False
    except Exception as e:
        print(f"❌ Download test error: {e}")
        return False

def main():
    """Main function."""
    print("🍪 YouTube Cookie Exporter")
    print("=" * 50)
    
    # Check yt-dlp
    if not check_yt_dlp_version():
        print("\n💡 Install yt-dlp: pip install yt-dlp")
        return
    
    # Test browser cookies
    available_browsers = test_browser_cookies()
    
    if not available_browsers:
        print("\n❌ No browsers with YouTube cookies found!")
        print("\n📋 Manual steps:")
        print("1. Open YouTube in your browser and log in")
        print("2. Install 'Get cookies.txt' browser extension")
        print("3. Export cookies and save as 'backend/cookies/youtube.txt'")
        return
    
    print(f"\n✅ Found cookies in: {', '.join(available_browsers)}")
    
    # Try to export from the first available browser
    browser = available_browsers[0]
    if export_cookies_from_browser(browser):
        # Test the exported cookies
        if test_download_with_cookies():
            print("\n🎉 Success! Your cookies are working.")
            print("You can now use the YouTube download service.")
        else:
            print("\n⚠️ Cookies exported but download test failed.")
            print("You may need to wait a few minutes or try a different browser.")
    else:
        print(f"\n❌ Failed to export cookies from {browser}")
        print("Try logging into YouTube in your browser first.")

if __name__ == "__main__":
    main()
