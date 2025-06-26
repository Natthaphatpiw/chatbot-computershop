#!/usr/bin/env python3

"""
Simple test script to verify the backend is working correctly
Run this after starting the backend server to test the API endpoints
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_health_endpoint():
    """Test the health check endpoint"""
    print("🏥 Testing health endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

async def test_chat_endpoint():
    """Test the chat endpoint with a simple message"""
    print("💬 Testing chat endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            payload = {"message": "โน้ตบุ๊คงบ 20000"}
            response = await client.post(
                f"{BASE_URL}/api/chat",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Chat endpoint working")
                print(f"   Response: {data.get('message', '')[:100]}...")
                print(f"   Products found: {len(data.get('products', []))}")
                return True
            else:
                print(f"❌ Chat endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Chat endpoint error: {e}")
            return False

async def test_trending_endpoint():
    """Test the trending products endpoint"""
    print("📈 Testing trending endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/trending?limit=3")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Trending endpoint working")
                print(f"   Products returned: {len(data)}")
                return True
            else:
                print(f"❌ Trending endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Trending endpoint error: {e}")
            return False

async def main():
    print("🧪 Backend API Test Suite")
    print("=" * 40)
    
    # Test health first
    health_ok = await test_health_endpoint()
    if not health_ok:
        print("\n❌ Backend is not responding. Make sure it's running on port 8000.")
        return
    
    print()
    
    # Test other endpoints
    chat_ok = await test_chat_endpoint()
    print()
    
    trending_ok = await test_trending_endpoint()
    print()
    
    # Summary
    print("📊 Test Results:")
    print("=" * 40)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Chat API: {'✅ PASS' if chat_ok else '❌ FAIL'}")
    print(f"Trending API: {'✅ PASS' if trending_ok else '❌ FAIL'}")
    
    if all([health_ok, chat_ok, trending_ok]):
        print("\n🎉 All tests passed! Backend is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    asyncio.run(main())