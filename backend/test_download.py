#!/usr/bin/env python3
"""
Test script to verify YouTube download functionality and cookies.

This script tests the download service with a simple YouTube video to verify
that cookies and bot detection bypasses are working correctly.
"""

import sys
from pathlib import Path

# Add the backend directory to the path so we can import our modules
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.download import process_download, _resolve_cookies_path, _validate_cookies

def test_cookies():
    """Test cookie validation."""
    print("🍪 Testing cookie validation...")
    
    cookies_file = _resolve_cookies_path()
    if cookies_file:
        print(f"   Found cookies file: {cookies_file}")
        
        is_valid = _validate_cookies(cookies_file)
        if is_valid:
            print("   ✅ Cookies appear valid")
        else:
            print("   ⚠️  Cookies appear invalid or expired")
    else:
        print("   ❌ No cookies file found")
    
    return cookies_file

def test_download():
    """Test downloading a simple YouTube video."""
    print("\n📹 Testing YouTube download...")
    
    # Use a simple, short video for testing
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - short and well-known
    
    try:
        print(f"   Testing with URL: {test_url}")
        result = process_download(test_url)
        
        print("   ✅ Download successful!")
        print(f"   📁 Video saved to: {result['video_path']}")
        print(f"   🎬 Filename: {result['filename']}")
        print(f"   🔗 API URL: {result['download_url']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Download failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 YouTube Download Test Suite")
    print("=" * 50)
    
    # Test cookies first
    cookies_file = test_cookies()
    
    # Test download
    success = test_download()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Your YouTube download service is working correctly.")
    else:
        print("❌ Tests failed. Please check the error messages above.")
        if not cookies_file:
            print("\n💡 Try running: python update_cookies.py")
        print("\n💡 For more help, check the error messages and cookie update instructions.")

if __name__ == "__main__":
    main()
