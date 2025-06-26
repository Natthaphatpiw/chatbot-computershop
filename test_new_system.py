#!/usr/bin/env python3

import requests
import json
import time
import subprocess
import sys

def test_new_system():
    print("🧪 ทดสอบระบบใหม่กับ database products")
    print("=" * 50)
    
    # Start backend
    backend_proc = subprocess.Popen(
        [sys.executable, '/Users/pp/Downloads/chatbot-computershop/backend/start.py'],
        cwd='/Users/pp/Downloads/chatbot-computershop/backend'
    )
    
    # Wait for backend to start
    time.sleep(3)
    
    try:
        # Test queries based on new categories
        test_queries = [
            "โน้ตบุ๊คงบ 20000",
            "การ์ดจอ RTX เกมมิ่ง",
            "คีย์บอร์ด mechanical",
            "หูฟัง gaming ไร้สาย",
            "จอมอนิเตอร์ 27 นิ้ว",
            "สินค้าส่งฟรี ราคาไม่เกิน 5000",
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
                    
                    # Check MongoDB Query
                    mongo_query = data.get('mongoQuery')
                    if mongo_query:
                        print("🔍 MongoDB Query:")
                        print(json.dumps(mongo_query, ensure_ascii=False, indent=2))
                    
                    # Show product details for first product
                    products = data.get('products', [])
                    if products:
                        product = products[0]
                        print(f"\n📦 ตัวอย่างสินค้าแรก:")
                        print(f"   ชื่อ: {product.get('title', '')[:60]}...")
                        print(f"   หมวด: {product.get('cateName', 'N/A')}")
                        print(f"   ราคา: {product.get('salePrice', 0):,.0f} ฿")
                        print(f"   สต็อก: {product.get('stockQuantity', 0)}")
                        print(f"   ส่งฟรี: {'✅' if product.get('freeShipping') else '❌'}")
                        print(f"   รับประกัน 2 ปี: {'✅' if product.get('product_warranty_2_year') else '❌'}")
                        print(f"   รับประกัน 3 ปี: {'✅' if product.get('product_warranty_3_year') else '❌'}")
                        
                        # Check image URL
                        images = product.get('images', {})
                        if images and 'original' in images:
                            urls = images['original'].get('url', [])
                            if urls:
                                print(f"   รูปสินค้า: {urls[0][:50]}...")
                    
                    print(f"\n💭 Response preview: {data.get('message', '')[:200]}...")
                    
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    
    finally:
        # Cleanup
        backend_proc.terminate()
        backend_proc.wait()
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    test_new_system()