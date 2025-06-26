#!/usr/bin/env python3
"""
Test script for Two-Stage LLM System
Tests various Thai queries including brand filtering and gaming requirements
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.two_stage_llm import (
    stage1_basic_query_builder,
    stage2_content_analyzer,
    generate_two_stage_response,
    normalize_text_advanced
)

# Mock Product class for testing
class MockProduct:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 'test-id')
        self.title = kwargs.get('title', 'Test Product')
        self.description = kwargs.get('description', 'Test Description')
        self.cateName = kwargs.get('cateName', 'Test Category')
        self.price = kwargs.get('price', 10000)
        self.salePrice = kwargs.get('salePrice', 9000)
        self.stockQuantity = kwargs.get('stockQuantity', 5)
        self.rating = kwargs.get('rating', 4.5)
        self.totalReviews = kwargs.get('totalReviews', 100)
        self.productView = kwargs.get('productView', 1000)
        self.freeShipping = kwargs.get('freeShipping', True)

# Test cases based on the examples you provided
TEST_CASES = [
    # Brand filtering test cases
    {
        "input": "มีโน้ตบุ๊ค ASUS ไหม",
        "description": "Brand filtering - ASUS notebook query"
    },
    {
        "input": "โน้ตบุ๊ค ASUS งบ 20000",
        "description": "Brand + budget filtering - ASUS notebook with 20k budget"
    },
    
    # Gaming requirement test cases  
    {
        "input": "โนตบุคสำหรับเล่นเกม valorant ไม่เกิน 30000",
        "description": "Gaming requirement - Valorant gaming laptop under 30k"
    },
    {
        "input": "คอมพิวเตอร์เล่นเกมรุ่นไหนดีสุดในร้านตอนนี้",
        "description": "Gaming computer recommendation"
    },
    
    # Computer context test cases
    {
        "input": "อยากได้คอมทำงานกราฟิก แนะนำหน่อย",
        "description": "Computer for graphics work"
    },
    {
        "input": "การ์ดจอสำหรับเล่นเกม",
        "description": "Graphics card for gaming"
    },
    
    # Additional test cases
    {
        "input": "เมาส์เกมมิ่งไร้สาย RGB ราคาไม่เกิน 3000",
        "description": "Wireless gaming mouse with RGB under 3k"
    },
    {
        "input": "คีย์บอร์ด mechanical เงียบๆ สำหรับทำงาน",
        "description": "Quiet mechanical keyboard for work"
    }
]

# Mock products for testing
MOCK_PRODUCTS = [
    MockProduct(
        id="1",
        title="ASUS VivoBook 15 X1504VA-BQ086W Indie Black",
        description="โน้ตบุ๊คสำหรับใช้งานทั่วไป เหมาะสำหรับเรียนและทำงาน มาพร้อม Intel Core i5",
        cateName="Notebooks",
        price=22000,
        salePrice=19990,
        productView=2500
    ),
    MockProduct(
        id="2", 
        title="HP Pavilion Gaming 15-dk1056TX Shadow Black",
        description="โน้ตบุ๊คเกมมิ่งสำหรับเล่นเกม Valorant, PUBG, GTA V ได้อย่างลื่นไหล พร้อม GTX 1650",
        cateName="Gaming Notebooks",
        price=35000,
        salePrice=29990,
        productView=3200
    ),
    MockProduct(
        id="3",
        title="Dell Inspiron 15 3000 Series Silver",
        description="คอมพิวเตอร์โน้ตบุ๊คสำหรับใช้งานทั่วไป office excel powerpoint",
        cateName="Notebooks", 
        price=18000,
        salePrice=16990,
        productView=1800
    ),
    MockProduct(
        id="4",
        title="MSI Gaming Desktop Tower Intel Core i7 RTX 4060",
        description="คอมพิวเตอร์ตั้งโต๊ะเกมมิ่ง เล่นเกมได้ทุกเกม Valorant 200+ FPS พร้อม RGB",
        cateName="Desktop PC",
        price=45000,
        salePrice=39990,
        productView=5000
    ),
    MockProduct(
        id="5",
        title="NVIDIA GeForce RTX 4060 Ti Gaming Graphics Card",
        description="การ์ดจอเกมมิ่งรุ่นใหม่ เล่นเกมได้ลื่นไหล 1440p gaming performance",
        cateName="Graphics Cards",
        price=18000,
        salePrice=16990,
        productView=4200
    ),
    MockProduct(
        id="6",
        title="Razer DeathAdder V3 Wireless Gaming Mouse RGB",
        description="เมาส์เกมมิ่งไร้สาย พร้อมไฟ RGB สำหรับเล่นเกม FPS",
        cateName="Gaming Mouse",
        price=3500,
        salePrice=2990,
        productView=1500
    )
]

async def test_stage1_query_builder(test_case):
    """Test Stage 1 LLM query building"""
    print(f"\n🔍 Stage 1 Test: {test_case['description']}")
    print(f"Input: '{test_case['input']}'")
    
    try:
        result = await stage1_basic_query_builder(test_case['input'])
        
        print(f"✅ Stage 1 Success:")
        print(f"   MongoDB Query: {result['query']}")
        print(f"   Used Terms: {result['processedTerms'].get('used', [])}")
        print(f"   Remaining Terms: {result['processedTerms'].get('remaining', [])}")
        print(f"   Reasoning: {result['reasoning']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Stage 1 Error: {e}")
        return None

async def test_stage2_content_analyzer(test_case, stage1_result):
    """Test Stage 2 LLM content analysis"""
    print(f"\n🎯 Stage 2 Test: {test_case['description']}")
    
    if not stage1_result:
        print("❌ Cannot test Stage 2 without Stage 1 result")
        return []
    
    try:
        filtered_products = await stage2_content_analyzer(
            test_case['input'],
            stage1_result,
            MOCK_PRODUCTS
        )
        
        print(f"✅ Stage 2 Success:")
        print(f"   Filtered Products: {len(filtered_products)}")
        for i, product in enumerate(filtered_products[:3]):
            print(f"   {i+1}. {product.title}")
        
        return filtered_products
        
    except Exception as e:
        print(f"❌ Stage 2 Error: {e}")
        return []

async def test_full_response_generation(test_case, stage1_result, products):
    """Test full response generation"""
    print(f"\n💬 Response Generation Test: {test_case['description']}")
    
    if not stage1_result or not products:
        print("❌ Cannot test response generation without previous results")
        return
    
    try:
        response = await generate_two_stage_response(
            test_case['input'],
            stage1_result,
            products
        )
        
        print(f"✅ Response Generated:")
        print(f"   Length: {len(response)} characters")
        print(f"   Response Preview: {response[:200]}...")
        
        return response
        
    except Exception as e:
        print(f"❌ Response Generation Error: {e}")
        return None

async def run_comprehensive_test(test_case):
    """Run complete two-stage test for a single test case"""
    print(f"\n{'='*80}")
    print(f"🧪 COMPREHENSIVE TEST: {test_case['description']}")
    print(f"{'='*80}")
    
    # Stage 1: Query Building
    stage1_result = await test_stage1_query_builder(test_case)
    
    # Stage 2: Content Analysis  
    products = await test_stage2_content_analyzer(test_case, stage1_result)
    
    # Response Generation
    response = await test_full_response_generation(test_case, stage1_result, products)
    
    print(f"\n📊 Test Summary:")
    print(f"   Stage 1: {'✅ Success' if stage1_result else '❌ Failed'}")
    print(f"   Stage 2: {'✅ Success' if products else '❌ Failed'}")
    print(f"   Response: {'✅ Success' if response else '❌ Failed'}")

async def test_text_normalization():
    """Test advanced text normalization"""
    print(f"\n{'='*80}")
    print(f"🔤 TEXT NORMALIZATION TESTS")
    print(f"{'='*80}")
    
    test_inputs = [
        "โน้ตบุ๊ค",
        "โนตบุค", 
        "โน๊ตบุ๊ค",
        "คอม",
        "คอมพิวเตอร์",
        "การ์ดจอ",
        "การ์จอ",
        "กราฟิก",
        "คีบอร์ด",
        "เม้าส์"
    ]
    
    for input_text in test_inputs:
        normalized = normalize_text_advanced(input_text)
        print(f"   '{input_text}' → '{normalized}'")

async def main():
    """Main test runner"""
    print("🚀 Starting Two-Stage LLM System Tests")
    print(f"Testing {len(TEST_CASES)} cases with {len(MOCK_PRODUCTS)} mock products")
    
    # Test text normalization first
    await test_text_normalization()
    
    # Run comprehensive tests for each case
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n📝 Test Case {i}/{len(TEST_CASES)}")
        await run_comprehensive_test(test_case)
    
    print(f"\n{'='*80}")
    print("🎉 All tests completed!")
    print(f"{'='*80}")

if __name__ == "__main__":
    # Check if OPENAI_API_KEY is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set. Setting test key...")
        print("⚠️  Note: You need a valid OpenAI API key to run real tests")
        os.environ['OPENAI_API_KEY'] = 'test-key-for-local-testing'
    
    # Run tests
    asyncio.run(main())