#!/usr/bin/env python3
"""
Quick test for the improved 2-LLM system
Tests just the core functionality without database connection
"""

import asyncio
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.ai_helpers_improved import (
    generate_optimal_mongo_query_v2,
    filter_and_rank_products_v2,
    normalize_text,
    load_categories,
    get_category_mapping
)

async def test_llm1_query_generation():
    """Test LLM1 - MongoDB query generation"""
    
    print("🧪 Testing LLM1 - MongoDB Query Generation")
    print("="*50)
    
    test_cases = [
        "มีโน้ตบุ๊คราคาไม่เกิน 15,000 ไหม",
        "การ์ดจอ RTX 4060 ไม่เกิน 15000", 
        "เมาส์เกมมิ่งไร้สาย RGB",
        "คีย์บอร์ด mechanical เงียบๆ",
        "หูฟังมีอะไรบ้าง"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_input}")
        print("-" * 40)
        
        try:
            # Normalize text
            normalized = normalize_text(test_input)
            print(f"Normalized: {normalized}")
            
            # Generate query
            result = await generate_optimal_mongo_query_v2(test_input)
            
            print(f"✅ Query generated:")
            print(json.dumps(result["query"], ensure_ascii=False, indent=2))
            
            print(f"📊 Entities:")
            for key, value in result["entities"].items():
                if value:
                    print(f"   {key}: {value}")
            
            print(f"💭 Reasoning: {result['reasoning']}")
            print(f"🎯 Confidence: {result.get('confidence', 0)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

def test_category_mapping():
    """Test category mapping and navigation attributes loading"""
    
    print("\n🗂️ Testing Category Mapping System")
    print("="*50)
    
    # Test loading categories
    categories = load_categories()
    print(f"✅ Loaded {len(categories)} categories from navigation_attributes.json")
    print("Sample categories:", categories[:10])
    
    # Test mapping
    mapping = get_category_mapping()
    print(f"\n✅ Category mapping has {len(mapping)} Thai terms")
    
    # Test specific mappings
    test_terms = ["โน้ตบุ๊ก", "การ์ดจอ", "เมาส์", "คีย์บอร์ด"]
    for term in test_terms:
        if term in mapping:
            print(f"   {term} → {mapping[term]}")
        else:
            print(f"   {term} → Not found")

async def main():
    """Run all tests"""
    print("🚀 Testing Enhanced 2-LLM System Components")
    print("="*60)
    
    # Test category system first
    test_category_mapping()
    
    # Test LLM1 query generation
    await test_llm1_query_generation()
    
    print(f"\n✅ All component tests completed!")

if __name__ == "__main__":
    asyncio.run(main())