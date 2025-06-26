#!/usr/bin/env python3

import requests
import json
import time
import subprocess
import sys

def test_query_display():
    print("🧪 Testing MongoDB Query Display in Chat Response")
    print("=" * 50)
    
    # Start backend
    backend_proc = subprocess.Popen(
        [sys.executable, '/Users/pp/Downloads/chatbot-computershop/backend/start.py'],
        cwd='/Users/pp/Downloads/chatbot-computershop/backend'
    )
    
    # Wait for backend to start
    time.sleep(3)
    
    try:
        # Test chat with Thai query
        test_queries = [
            "โน้ตบุ๊คงบ 20000",
            "การ์ดจอ RTX เกมมิ่ง",
            "คีย์บอร์ด mechanical ไร้สาย",
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test {i}: {query}")
            print("-" * 30)
            
            try:
                response = requests.post(
                    "http://localhost:8000/api/chat",
                    json={"message": query},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    print("✅ Response received")
                    print(f"📊 Products found: {len(data.get('products', []))}")
                    print(f"💬 Response length: {len(data.get('message', ''))}")
                    
                    # Display MongoDB Query
                    mongo_query = data.get('mongoQuery')
                    if mongo_query:
                        print("🔍 MongoDB Query ที่ LLM สร้าง:")
                        print(json.dumps(mongo_query, ensure_ascii=False, indent=2))
                    else:
                        print("❌ ไม่มี MongoDB Query ในการตอบกลับ")
                    
                    # Show part of the response message
                    message = data.get('message', '')
                    if 'mongodb query' in message.lower() or 'query' in message.lower():
                        print("✅ การตอบกลับมี MongoDB Query แล้ว")
                    else:
                        print("⚠️  การตอบกลับยังไม่แสดง MongoDB Query")
                    
                    print(f"💭 Response preview: {message[:200]}...")
                    
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    
    finally:
        # Cleanup
        backend_proc.terminate()
        backend_proc.wait()
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    test_query_display()