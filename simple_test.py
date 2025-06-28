#!/usr/bin/env python3

import os
import asyncio
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def test_mongodb():
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            print("❌ MONGODB_URI not found")
            return False
            
        print(f"🔗 Connecting to MongoDB...")
        client = AsyncIOMotorClient(mongodb_uri)
        
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful")
        
        # Test collection access
        db = client["dashboard-ai-data"]
        collection = db["product_details"]
        count = await collection.count_documents({"productActive": True})
        print(f"📊 Found {count} active products")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB error: {e}")
        return False

async def test_openai():
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not found")
            return False
            
        print("🤖 Testing OpenAI connection...")
        client = OpenAI(api_key=api_key)
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("✅ OpenAI connection successful")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return False

async def main():
    print("🧪 Testing Backend Dependencies")
    print("=" * 40)
    
    # Test MongoDB
    mongodb_ok = await test_mongodb()
    print()
    
    # Test OpenAI
    openai_ok = await test_openai()
    print()
    
    # Summary
    print("📋 Test Results:")
    print("=" * 40)
    print(f"MongoDB: {'✅ PASS' if mongodb_ok else '❌ FAIL'}")
    print(f"OpenAI:  {'✅ PASS' if openai_ok else '❌ FAIL'}")
    
    if mongodb_ok and openai_ok:
        print("\n🎉 All dependencies working! Backend should start successfully.")
    else:
        print("\n⚠️  Some dependencies failed. Fix the issues above before starting the backend.")

if __name__ == "__main__":
    asyncio.run(main())