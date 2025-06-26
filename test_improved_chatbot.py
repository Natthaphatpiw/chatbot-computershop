"""
Test script for the improved 2-LLM chatbot system
Tests various user inputs to validate the enhanced query generation and product ranking
"""

import asyncio
import os
import sys
import json
from motor.motor_asyncio import AsyncIOMotorClient

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.chatbot import ITStoreChatbot
from app.database import connect_to_mongodb, get_database

async def test_chatbot_queries():
    """Test the improved chatbot with various user inputs"""
    
    # Initialize database connection
    try:
        await connect_to_mongodb()
        database = await get_database()
        chatbot = ITStoreChatbot(database)
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    # Test cases covering different scenarios
    test_cases = [
        {
            "name": "Budget constraint with category",
            "input": "มีโน้ตบุ๊คราคาไม่เกิน 15,000 ไหม",
            "expected": "Should find notebooks under 15,000 baht"
        },
        {
            "name": "Gaming requirement", 
            "input": "โน้ตบุ๊คเล่นเกมงบ 30000",
            "expected": "Should find gaming notebooks under 30,000 baht"
        },
        {
            "name": "Specific component with misspelling",
            "input": "การ์จอ RTX 4060 ไม่เกิน 15000",
            "expected": "Should find RTX 4060 graphics cards under 15,000 baht"
        },
        {
            "name": "Ambiguous term - คอม",
            "input": "คอมทำงานงบ 20000",
            "expected": "Should understand 'คอม' as computers/notebooks"
        },
        {
            "name": "Keyboard with features",
            "input": "คีย์บอร์ด mechanical เงียบๆ",
            "expected": "Should find quiet mechanical keyboards"
        },
        {
            "name": "Mouse for gaming",
            "input": "เมาส์เกมมิ่งไร้สาย RGB",
            "expected": "Should find wireless gaming mice with RGB"
        },
        {
            "name": "Monitor search",
            "input": "จอมอนิเตอร์ 24 นิ้ว gaming",
            "expected": "Should find 24-inch gaming monitors"
        },
        {
            "name": "Brand specific",
            "input": "โน้ตบุ๊ค ASUS เล่นเกม",
            "expected": "Should find ASUS gaming notebooks"
        },
        {
            "name": "Very specific product",
            "input": "แรม DDR4 16GB 3200MHz",
            "expected": "Should find specific RAM specifications"
        },
        {
            "name": "General category browse",
            "input": "หูฟังมีอะไรบ้าง",
            "expected": "Should show various headphone options"
        }
    ]

    print("\n" + "="*80)
    print("🧪 TESTING IMPROVED 2-LLM CHATBOT SYSTEM")
    print("="*80)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print(f"Input: \"{test_case['input']}\"")
        print(f"Expected: {test_case['expected']}")
        print("-" * 60)
        
        try:
            # Process the user input
            result = await chatbot.process_user_input(test_case['input'])
            
            # Display results
            print(f"🔍 MongoDB Query Generated:")
            print(json.dumps(result.get('mongoQuery', {}), ensure_ascii=False, indent=2))
            
            print(f"\n📊 Results Summary:")
            print(f"- Confidence: {result.get('confidence', 0):.1f}")
            print(f"- Raw products found: {result.get('rawProductCount', 0)}")
            print(f"- Filtered products: {result.get('filteredProductCount', 0)}")
            
            print(f"\n🤖 LLM Response:")
            print(result.get('response', 'No response'))
            
            # Show top products if any
            products = result.get('products', [])
            if products:
                print(f"\n🛍️ Top Products ({len(products)}):")
                for j, product in enumerate(products[:3], 1):
                    print(f"{j}. {product.title}")
                    print(f"   Price: ฿{product.salePrice:,} | Rating: {product.rating}/5 | Stock: {product.stockQuantity}")
                    print(f"   Category: {product.cateName}")
            else:
                print("❌ No products found")
            
            # Show entities extracted
            entities = result.get('entities', {})
            if entities:
                print(f"\n🔬 Entities Extracted:")
                for key, value in entities.items():
                    if value:
                        print(f"   {key}: {value}")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*80)

    print(f"\n✅ Testing completed! Tested {len(test_cases)} cases.")

async def test_specific_query():
    """Test specific problematic query mentioned by user"""
    
    await connect_to_mongodb()
    database = await get_database()
    chatbot = ITStoreChatbot(database)
    
    test_input = "มีโน้ตบุ๊คราคาไม่เกิน 15,000 ไหม"
    
    print("\n🎯 SPECIFIC TEST - User's Problematic Query")
    print("="*60)
    print(f"Input: \"{test_input}\"")
    
    result = await chatbot.process_user_input(test_input)
    
    print(f"\n🔍 Generated MongoDB Query:")
    query = result.get('mongoQuery', {})
    print(json.dumps(query, ensure_ascii=False, indent=2))
    
    print(f"\n📊 Expected vs Actual:")
    print("Expected Query Structure:")
    expected_query = {
        "stockQuantity": {"$gt": 0},
        "cateName": "Notebooks", 
        "salePrice": {"$lte": 15000}
    }
    print(json.dumps(expected_query, ensure_ascii=False, indent=2))
    
    print(f"\n✅ Query Validation:")
    if query.get('cateName') == 'Notebooks':
        print("✅ Category correctly identified as 'Notebooks'")
    else:
        print(f"❌ Category mismatch. Expected 'Notebooks', got '{query.get('cateName')}'")
    
    if query.get('salePrice', {}).get('$lte') == 15000:
        print("✅ Budget correctly set to ≤ 15,000")
    else:
        print(f"❌ Budget mismatch. Expected ≤15000, got {query.get('salePrice')}")
    
    if query.get('stockQuantity', {}).get('$gt') == 0:
        print("✅ Stock filter correctly applied")
    else:
        print("❌ Stock filter missing or incorrect")
    
    products = result.get('products', [])
    print(f"\n📦 Found {len(products)} products")
    
    if products:
        print("Sample products:")
        for i, p in enumerate(products[:3], 1):
            print(f"{i}. {p.title} - ฿{p.salePrice:,} ({p.cateName})")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Chatbot Tests...")
    
    # Run the specific test first
    asyncio.run(test_specific_query())
    
    # Then run comprehensive tests
    asyncio.run(test_chatbot_queries())