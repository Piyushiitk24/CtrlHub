#!/usr/bin/env python3
"""
Test CtrlHub Local Agent API
"""

import urllib.request
import json

def test_api():
    try:
        # Test main endpoint
        print("🧪 Testing CtrlHub Local Agent API")
        print("=" * 40)
        
        response = urllib.request.urlopen('http://localhost:8001/')
        data = json.loads(response.read().decode())
        print("✅ Main endpoint:", data)
        
        # Test status endpoint
        response = urllib.request.urlopen('http://localhost:8001/status')
        data = json.loads(response.read().decode())
        print("✅ Status endpoint:", data)
        
        # Test hardware scan
        response = urllib.request.urlopen('http://localhost:8001/hardware/scan')
        data = json.loads(response.read().decode())
        print("✅ Hardware scan:", data)
        
        print("\n🎉 All API tests passed!")
        
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    test_api()
