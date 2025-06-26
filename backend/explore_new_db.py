#!/usr/bin/env python3

import os
import asyncio
import json
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment
load_dotenv()

async def explore_products_collection():
    print("🔍 สำรวจ collection 'products' ใน database 'dashboard-ai-data'")
    print("=" * 60)
    
    try:
        # Connect to MongoDB
        mongodb_uri = os.getenv("MONGODB_URI")
        client = AsyncIOMotorClient(mongodb_uri)
        db = client["dashboard-ai-data"]
        collection = db["products"]
        
        # 1. Count total documents
        total_count = await collection.count_documents({})
        print(f"📊 จำนวนสินค้าทั้งหมด: {total_count:,} รายการ")
        
        # 2. Sample a few documents to see structure
        print("\n📋 ตัวอย่างเอกสาร 3 รายการแรก:")
        sample_docs = await collection.find().limit(3).to_list(length=3)
        
        for i, doc in enumerate(sample_docs, 1):
            print(f"\n--- ตัวอย่างที่ {i} ---")
            # Show main fields only
            print(f"ID: {doc.get('_id')}")
            print(f"Title: {doc.get('title', 'N/A')[:100]}...")
            print(f"Category: {doc.get('cateName', 'N/A')}")
            print(f"Price: {doc.get('price', 0):,.0f} ฿")
            print(f"Sale Price: {doc.get('salePrice', 0):,.0f} ฿")
            print(f"Stock: {doc.get('stockQuantity', 0)}")
            print(f"Rating: {doc.get('rating', 0)}/5 ({doc.get('totalReviews', 0)} reviews)")
            print(f"Free Shipping: {doc.get('freeShipping', False)}")
            print(f"2Y Warranty: {doc.get('product_warranty_2_year', 'N/A')}")
            print(f"3Y Warranty: {doc.get('product_warranty_3_year', 'N/A')}")
            
            # Check image structure
            images = doc.get('images', {})
            if images and 'original' in images:
                original_urls = images['original'].get('url', [])
                if original_urls:
                    print(f"Image URL: {original_urls[0] if original_urls else 'No image'}")
            
        # 3. Analyze categories
        print("\n📂 หมวดหมู่สินค้า (cateName) ที่มีในระบบ:")
        categories = await collection.distinct("cateName")
        print(f"จำนวนหมวดหมู่: {len(categories)}")
        for i, cat in enumerate(sorted(categories)[:20], 1):
            count = await collection.count_documents({"cateName": cat})
            print(f"{i:2d}. {cat} ({count:,} สินค้า)")
        
        if len(categories) > 20:
            print(f"... และอีก {len(categories) - 20} หมวดหมู่")
        
        # 4. Price analysis
        print("\n💰 การวิเคราะห์ราคา:")
        pipeline = [
            {"$group": {
                "_id": None,
                "min_price": {"$min": "$salePrice"},
                "max_price": {"$max": "$salePrice"},
                "avg_price": {"$avg": "$salePrice"},
                "total_products": {"$sum": 1}
            }}
        ]
        
        price_stats = await collection.aggregate(pipeline).to_list(length=1)
        if price_stats:
            stats = price_stats[0]
            print(f"ราคาต่ำสุด: {stats['min_price']:,.0f} ฿")
            print(f"ราคาสูงสุด: {stats['max_price']:,.0f} ฿")
            print(f"ราคาเฉลี่ย: {stats['avg_price']:,.0f} ฿")
        
        # 5. Check stock availability
        in_stock = await collection.count_documents({"stockQuantity": {"$gt": 0}})
        print(f"\n📦 สินค้าที่มีสต็อก: {in_stock:,}/{total_count:,} รายการ ({in_stock/total_count*100:.1f}%)")
        
        # 6. Check fields that might be missing or null
        print("\n🔍 การตรวจสอบฟิลด์พิเศษ:")
        free_shipping_count = await collection.count_documents({"freeShipping": True})
        warranty_2y_count = await collection.count_documents({"product_warranty_2_year": {"$ne": None}})
        warranty_3y_count = await collection.count_documents({"product_warranty_3_year": {"$ne": None}})
        
        print(f"Free Shipping: {free_shipping_count:,} สินค้า")
        print(f"Warranty 2 Year: {warranty_2y_count:,} สินค้า")
        print(f"Warranty 3 Year: {warranty_3y_count:,} สินค้า")
        
        # 7. Sample search test
        print("\n🔎 ทดสอบการค้นหา:")
        
        # Test search by category
        notebook_count = await collection.count_documents({
            "cateName": {"$regex": "โน้ตบุ๊ก", "$options": "i"}
        })
        print(f"โน้ตบุ๊ก: {notebook_count:,} สินค้า")
        
        # Test search by title
        gaming_count = await collection.count_documents({
            "title": {"$regex": "gaming", "$options": "i"}
        })
        print(f"Gaming (ในชื่อสินค้า): {gaming_count:,} สินค้า")
        
        # Test price range
        budget_20k = await collection.count_documents({
            "salePrice": {"$lte": 20000},
            "stockQuantity": {"$gt": 0}
        })
        print(f"สินค้าราคาไม่เกิน 20,000 ฿ (มีสต็อก): {budget_20k:,} สินค้า")
        
        client.close()
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    asyncio.run(explore_products_collection())