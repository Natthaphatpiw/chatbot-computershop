#!/usr/bin/env python3
"""
Test the V3 system with actual schema and navigation attributes
"""

import asyncio
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.ai_helpers_v3 import (
    generate_optimal_mongo_query_v3,
    load_real_schema_and_categories,
    normalize_text,
    get_category_mapping
)

async def test_v3_query_generation():
    """Test V3 MongoDB query generation with real schema"""
    
    print("🧪 Testing V3 System - Real Schema + Categories")
    print("="*60)
    
    # Load real data first
    schema_data, categories_data = load_real_schema_and_categories()
    
    print(f"📊 Loaded Schema: {len(schema_data.get('properties', {})) if schema_data else 0} fields")
    print(f"📊 Loaded Categories: {len(categories_data)} categories")
    
    if schema_data and 'properties' in schema_data:
        print(f"🔍 Available Fields: {list(schema_data['properties'].keys())[:10]}...")
    
    test_cases = [
        {
            "name": "User's Original Problem",
            "input": "มีโน้ตบุ๊คราคาไม่เกิน 15,000 ไหม",
            "expected": "Should create exact query with cateName=Notebooks, salePrice<=15000, NO productActive"
        },
        {
            "name": "Graphics Card with Budget",
            "input": "การ์ดจอ RTX 4060 ไม่เกิน 15000", 
            "expected": "Should use cateName=Graphics Cards"
        },
        {
            "name": "Gaming Mouse",
            "input": "เมาส์เกมมิ่งไร้สาย RGB",
            "expected": "Should use cateName=Gaming Mouse or Mouse"
        },
        {
            "name": "Ambiguous Computer",
            "input": "คอมทำงานงบ 20000",
            "expected": "Should handle multiple possible categories"
        },
        {
            "name": "Headphone Browse",
            "input": "หูฟังมีอะไรบ้าง",
            "expected": "Should use cateName=Headphone"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"Input: \"{test_case['input']}\"")
        print(f"Expected: {test_case['expected']}")
        print("-" * 50)
        
        try:
            # Generate query
            result = await generate_optimal_mongo_query_v3(test_case['input'])
            
            # Display results
            print(f"✅ Generated Query:")
            query = result["query"]
            print(json.dumps(query, ensure_ascii=False, indent=2))
            
            # Validation checks
            print(f"\n🔍 Validation Results:")
            
            # Check for productActive (should NOT exist)
            if 'productActive' in query:
                print("❌ ERROR: Query contains 'productActive' field that doesn't exist!")
            else:
                print("✅ No invalid 'productActive' field")
            
            # Check for stockQuantity (should exist)
            if 'stockQuantity' in query and query['stockQuantity'].get('$gt') == 0:
                print("✅ Correct stockQuantity filter")
            else:
                print("❌ Missing or incorrect stockQuantity filter")
            
            # Check for budget handling
            if 'salePrice' in query:
                print(f"✅ Budget filter: salePrice <= {query['salePrice'].get('$lte', 'N/A')}")
            else:
                print("ℹ️  No budget filter (may be intended)")
            
            # Check category
            if 'cateName' in query:
                category = query['cateName']
                if isinstance(category, str):
                    print(f"✅ Category: {category}")
                    if category in categories_data:
                        print(f"✅ Category exists in navigation_attributes.json")
                    else:
                        print(f"❌ Category '{category}' NOT found in navigation_attributes.json")
                elif isinstance(category, dict) and '$in' in category:
                    cats = category['$in']
                    print(f"✅ Multiple categories: {cats}")
                    valid_cats = [c for c in cats if c in categories_data]
                    if len(valid_cats) == len(cats):
                        print(f"✅ All categories valid")
                    else:
                        print(f"❌ Some categories invalid: {set(cats) - set(valid_cats)}")
            
            # Show extracted entities
            entities = result.get("entities", {})
            print(f"\n🎯 Extracted Entities:")
            for key, value in entities.items():
                if value:
                    print(f"   {key}: {value}")
            
            # Show reasoning and confidence
            print(f"\n💭 Reasoning: {result.get('reasoning', 'N/A')}")
            print(f"🎯 Confidence: {result.get('confidence', 0)}")
            
            # Show validation warnings
            warnings = result.get('validationWarnings', [])
            if warnings:
                print(f"\n⚠️  Validation Warnings:")
                for warning in warnings:
                    print(f"   - {warning}")
                    
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*60)

def test_schema_loading():
    """Test schema and categories loading"""
    
    print("\n📁 Testing Schema and Categories Loading")
    print("="*50)
    
    schema_data, categories_data = load_real_schema_and_categories()
    
    if schema_data:
        print(f"✅ Schema loaded successfully")
        if 'properties' in schema_data:
            fields = list(schema_data['properties'].keys())
            print(f"📊 Found {len(fields)} fields")
            print(f"🔍 Sample fields: {fields[:10]}")
            
            # Check for critical fields
            critical_fields = ['cateName', 'salePrice', 'stockQuantity', 'title', 'description']
            for field in critical_fields:
                if field in fields:
                    print(f"✅ Critical field '{field}' found")
                else:
                    print(f"❌ Critical field '{field}' missing")
        else:
            print("❌ Schema missing 'properties' section")
    else:
        print("❌ Failed to load schema")
    
    if categories_data:
        print(f"\n✅ Categories loaded successfully")
        print(f"📊 Found {len(categories_data)} categories")
        print(f"🔍 Sample categories: {categories_data[:10]}")
        
        # Check for key categories
        key_categories = ['Notebooks', 'Graphics Cards', 'Mouse', 'Keyboard', 'Headphone']
        for cat in key_categories:
            if cat in categories_data:
                print(f"✅ Key category '{cat}' found")
            else:
                print(f"❌ Key category '{cat}' missing")
    else:
        print("❌ Failed to load categories")

async def main():
    """Run all V3 tests"""
    print("🚀 Testing V3 Enhanced System with Real Schema")
    print("="*70)
    
    # Test schema loading first
    test_schema_loading()
    
    # Test query generation
    await test_v3_query_generation()
    
    print(f"\n✅ All V3 tests completed!")

if __name__ == "__main__":
    asyncio.run(main())