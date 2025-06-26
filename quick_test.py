#!/usr/bin/env python3

import requests
import json
import time

def test_backend():
    base_url = "http://localhost:8000"
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    print("🧪 Testing Backend API Endpoints")
    print("=" * 40)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint: PASS")
        else:
            print(f"❌ Health endpoint: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Health endpoint: ERROR ({e})")
        return False
    
    # Test 2: Chat endpoint
    try:
        payload = {"message": "โน้ตบุ๊คงบ 20000"}
        response = requests.post(
            f"{base_url}/api/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat endpoint: PASS")
            print(f"   Products found: {len(data.get('products', []))}")
            print(f"   Response length: {len(data.get('message', ''))}")
        else:
            print(f"❌ Chat endpoint: FAIL ({response.status_code})")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Chat endpoint: ERROR ({e})")
        return False
    
    # Test 3: Trending endpoint
    try:
        response = requests.get(f"{base_url}/api/trending?limit=3", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Trending endpoint: PASS")
            print(f"   Products returned: {len(data)}")
        else:
            print(f"❌ Trending endpoint: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Trending endpoint: ERROR ({e})")
        return False
    
    print("\n🎉 All API tests passed! Backend is working correctly.")
    return True

if __name__ == "__main__":
    test_backend()