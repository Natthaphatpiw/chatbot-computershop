#!/usr/bin/env python3
"""
Test the FINAL system with LLM1 (Simple Query) + LLM2 (Complex Analysis)
"""

import asyncio
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.ai_helpers_final import (
    generate_simple_mongo_query,
    analyze_and_rank_products_advanced,
    generate_natural_response_advanced,
    normalize_text
)

# Mock Product class for testing
class MockProduct:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.title = kwargs.get('title', 'Test Product')
        self.description = kwargs.get('description', 'Test description')
        self.cateName = kwargs.get('cateName', 'Notebooks')
        self.price = kwargs.get('price', 20000)
        self.salePrice = kwargs.get('salePrice', 18000)
        self.stockQuantity = kwargs.get('stockQuantity', 5)
        self.rating = kwargs.get('rating', 4.5)
        self.totalReviews = kwargs.get('totalReviews', 100)
        self.productView = kwargs.get('productView', 5000)
        self.freeShipping = kwargs.get('freeShipping', True)

async def test_final_system():
    """Test the complete FINAL system"""
    
    print("🧪 Testing FINAL 2-LLM System")
    print("="*60)
    
    test_cases = [
        {
            "name": "Simple Query - Basic Notebook",
            "input": "โน้ตบุ๊คราคาไม่เกิน 15,000",
            "expected": "Should generate simple query: stockQuantity + cateName + salePrice, NO description regex"
        },
        {
            "name": "Complex Query - Gaming Notebook", 
            "input": "โน้ตบุ๊คงบ 30000 เล่นเกม valorant",
            "expected": "Should use LLM2 to analyze descriptions for gaming specs"
        },
        {
            "name": "Complex Query - Work Notebook",
            "input": "โน้ตบุ๊คงบ 25000 ทำงาน excel powerpoint",
            "expected": "Should use LLM2 to analyze descriptions for office work"
        },
        {
            "name": "Simple Query - Graphics Card",
            "input": "การ์ดจอไม่เกิน 20000",
            "expected": "Should generate simple query without description analysis"
        },
        {
            "name": "Complex Query - Gaming Graphics Card",
            "input": "การ์ดจอ RTX 4060 เล่นเกมระดับ high setting",
            "expected": "Should use LLM2 to analyze gaming performance specs"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"Input: \"{test_case['input']}\"")
        print(f"Expected: {test_case['expected']}")
        print("-" * 50)
        
        try:
            # Step 1: LLM1 - Generate simple query
            print("🔍 STEP 1: LLM1 - Simple Query Generation")
            llm1_result = await generate_simple_mongo_query(test_case['input'])
            
            query = llm1_result["query"]
            entities = llm1_result["entities"]
            
            print(f"Generated Query:")
            print(json.dumps(query, ensure_ascii=False, indent=2))
            
            print(f"\nExtracted Entities:")
            print(f"  Category: {entities.get('category', 'N/A')}")
            print(f"  Budget: {entities.get('budget', 'N/A')}")
            print(f"  Complexity: {entities.get('complexity', 'N/A')}")
            print(f"  Intent: {entities.get('intent', 'N/A')}")
            
            # Validation checks for LLM1
            print(f"\n✅ LLM1 Validation:")
            
            # Check for forbidden fields
            if '$or' in query or any('$regex' in str(v) for v in query.values()):
                print("❌ ERROR: Found regex/text search in LLM1 query!")
            else:
                print("✅ No regex/text search (correct for LLM1)")
            
            # Check for required fields
            if 'stockQuantity' in query:
                print("✅ stockQuantity filter present")
            else:
                print("❌ Missing stockQuantity filter")
            
            if entities.get('category') and 'cateName' in query:
                print("✅ Category filter applied")
            elif not entities.get('category'):
                print("ℹ️  No category detected (OK)")
            else:
                print("❌ Category detected but not applied")
            
            # Step 2: Mock database results (simulate products)
            print(f"\n📦 STEP 2: Mock Database Results")
            mock_products = [
                MockProduct(
                    id=1,
                    title="ASUS VivoBook 15 X1504GA Gaming Notebook",
                    description="Intel Core i5-1235U, 8GB DDR4, 512GB SSD, สำหรับเล่นเกม Valorant, PUBG ได้ลื่น",
                    cateName="Gaming Notebooks",
                    salePrice=28900,
                    rating=4.3,
                    productView=8500
                ),
                MockProduct(
                    id=2,
                    title="HP Pavilion 15 Office Notebook",
                    description="Intel Core i3-1215U, 8GB RAM, 256GB SSD, เหมาะสำหรับทำงาน Office, Excel, PowerPoint",
                    cateName="Notebooks", 
                    salePrice=18900,
                    rating=4.1,
                    productView=3200
                ),
                MockProduct(
                    id=3,
                    title="Acer Aspire 5 Budget Notebook",
                    description="AMD Ryzen 3, 4GB RAM, 128GB SSD, ใช้งานทั่วไป เบาๆ",
                    cateName="Notebooks",
                    salePrice=12900,
                    rating=3.8,
                    productView=1500
                )
            ]
            
            print(f"Simulated {len(mock_products)} products from database")
            
            # Step 3: LLM2 - Product Analysis
            print(f"\n🎯 STEP 3: LLM2 - Product Analysis")
            
            complexity = entities.get('complexity', 'simple')
            if complexity == "simple":
                print("Simple query detected - using basic sorting")
                ranked_products = sorted(mock_products, 
                                       key=lambda p: (p.productView, p.rating), 
                                       reverse=True)[:3]
            else:
                print("Complex query detected - using LLM2 analysis")
                ranked_products = await analyze_and_rank_products_advanced(
                    test_case['input'],
                    entities,
                    mock_products,
                    query
                )
            
            print(f"Selected {len(ranked_products)} products:")
            for j, product in enumerate(ranked_products, 1):
                print(f"  {j}. {product.title} - ฿{product.salePrice:,}")
            
            # Step 4: Generate Response
            print(f"\n💬 STEP 4: Natural Language Response")
            response = await generate_natural_response_advanced(
                test_case['input'],
                entities,
                ranked_products,
                llm1_result.get('reasoning', ''),
                query
            )
            
            print("Generated Response:")
            print(response[:300] + "..." if len(response) > 300 else response)
            
            # Overall Assessment
            print(f"\n🎯 OVERALL ASSESSMENT:")
            
            # Check if system worked as expected
            if complexity == "simple" and ('$or' not in query and '$regex' not in str(query)):
                print("✅ Simple query correctly handled without text search")
            elif complexity == "complex" and len(ranked_products) > 0:
                print("✅ Complex query correctly analyzed with LLM2")
            else:
                print("⚠️  System behavior unclear")
            
            print(f"Strategy: {'LLM2 Analysis' if complexity == 'complex' else 'Basic Sorting'}")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*60)

async def test_specific_user_case():
    """Test user's specific problematic case"""
    
    print("\n🎯 Testing User's Specific Case")
    print("="*50)
    
    user_input = "มีโน้ตบุ๊คราคาไม่เกิน 15,000 ไหม"
    
    print(f"INPUT: \"{user_input}\"")
    print("\nEXPECTED BEHAVIOR:")
    print("1. LLM1: Generate simple query (no description regex)")
    print("2. Detect as 'simple' complexity")  
    print("3. Use basic sorting (no LLM2 needed)")
    print("4. Return products sorted by popularity")
    
    try:
        # Test LLM1
        result = await generate_simple_mongo_query(user_input)
        
        print(f"\nACTUAL RESULTS:")
        print(f"Query: {json.dumps(result['query'], ensure_ascii=False, indent=2)}")
        print(f"Complexity: {result['entities'].get('complexity', 'N/A')}")
        print(f"Category: {result['entities'].get('category', 'N/A')}")
        print(f"Budget: {result['entities'].get('budget', 'N/A')}")
        
        # Validate
        query = result['query']
        complexity = result['entities'].get('complexity', 'simple')
        
        print(f"\n✅ VALIDATION:")
        if '$or' not in query and 'description' not in str(query):
            print("✅ No description regex (correct for simple query)")
        else:
            print("❌ Contains unwanted text search")
        
        if complexity == "simple":
            print("✅ Correctly detected as simple query")
        else:
            print(f"❌ Incorrectly detected as {complexity}")
        
        if query.get('cateName') == 'Notebooks':
            print("✅ Correct category: Notebooks")
        else:
            print(f"❌ Wrong category: {query.get('cateName')}")
        
        if query.get('salePrice', {}).get('$lte') == 15000:
            print("✅ Correct budget: ≤15,000")
        else:
            print(f"❌ Wrong budget: {query.get('salePrice')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Run all final tests"""
    print("🚀 Testing FINAL 2-LLM System")
    print("="*70)
    print("LLM1: Simple Query Generator (NO description regex)")
    print("LLM2: Complex Product Analyzer (analyzes descriptions)")
    print("="*70)
    
    # Test specific user case first
    await test_specific_user_case()
    
    # Test complete system
    await test_final_system()
    
    print(f"\n✅ All FINAL system tests completed!")

if __name__ == "__main__":
    asyncio.run(main())