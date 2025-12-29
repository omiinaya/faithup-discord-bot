#!/usr/bin/env python3
"""Debug script for YouVerse VOTD API."""

import os
import sys
from dotenv import load_dotenv

# Add current directory to path to import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from youversion.client import YouVersionClient


def debug_votd():
    """Debug the VOTD functionality step by step."""
    # Load environment variables
    load_dotenv()
    
    username = os.getenv("YOUVERSION_USERNAME")
    password = os.getenv("YOUVERSION_PASSWORD")
    
    if not username or not password:
        print("❌ Error: Credentials not set")
        return
    
    print("🚀 Debugging YouVersion Verse of the Day Implementation")
    print("=" * 50)
    
    try:
        # Initialize client
        client = YouVersionClient()
        print("✅ Client initialized successfully")
        
        # Test authentication
        token = client.authenticator.get_access_token()
        print(f"✅ Authentication successful (token: {token[:20]}...)")
        
        # Test VOTD endpoint only
        print("\n📖 Testing VOTD endpoint only...")
        votd_raw = client.get_verse_of_the_day()
        print("✅ VOTD data received:")
        print(f"   Day: {votd_raw.get('day')}")
        print(f"   USFM: {votd_raw.get('usfm')}")
        print(f"   Image ID: {votd_raw.get('image_id')}")
        
        # Extract USFM reference
        usfm_refs = votd_raw.get("usfm", [])
        if usfm_refs:
            usfm_ref = usfm_refs[0]
            print(f"\n📖 Testing Bible chapter API with USFM: {usfm_ref}")
            
            # Test Bible chapter API
            chapter_data = client.get_verse_text(usfm_ref)
            print("✅ Bible chapter data received:")
            print(f"   Keys: {list(chapter_data.keys())}")
            
            # Try to extract verse text using the client's method
            try:
                verse_number = client._extract_verse_number(usfm_ref)
                print(f"   Extracted verse number: {verse_number}")
                
                verse_text = client._extract_verse_text(chapter_data, verse_number)
                print("✅ Verse text extracted successfully:")
                print(f"   Verse {verse_number}: {verse_text[:100]}...")
                
            except Exception as e:
                print(f"❌ Error extracting verse text: {e}")
                import traceback
                traceback.print_exc()
                
        else:
            print("❌ No USFM references found in VOTD data")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_votd()