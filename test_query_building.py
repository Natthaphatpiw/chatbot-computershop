#!/usr/bin/env python3
"""
Test script specifically for MongoDB query building
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.two_stage_llm import extract_basic_entities, build_basic_query, get_comprehensive_category_mapping

def test_query_building():
    """Test MongoDB query building with proper $in operators"""
    print("🧪 Testing MongoDB Query Building")
    print("=" * 50)
    
    # Mock categories data
    categories_data = ["Desktop PC", "All in One PC", "Mini PC", "Notebooks", "Graphics Cards", "Mouse", "Gaming Mouse"]
    
    test_cases = [
        {
            "input": "อยากได้คอมทำงานกราฟิก แนะนำหน่อย",
            "description": "Computer request (should map to multiple categories)"
        },
        {
            "input": "โน้ตบุ๊ค ASUS งบ 20000",
            "description": "Single category with budget"
        },
        {
            "input": "คอมเล่นเกม ไม่เกิน 30000",
            "description": "Computer gaming with budget"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        print(f"Input: {test_case['input']}")
        
        try:
            # Extract entities
            processed_terms = extract_basic_entities(test_case['input'], categories_data)
            
            # Build query
            query = build_basic_query(processed_terms)
            
            print(f"✅ Processed Terms:")
            print(f"   Category: {processed_terms.get('category', 'None')}")
            print(f"   Categories: {processed_terms.get('categories', 'None')}")
            print(f"   Budget: {processed_terms.get('budget', 'None')}")
            
            print(f"✅ MongoDB Query:")
            import json
            print(f"   {json.dumps(query, ensure_ascii=False, indent=2)}")
            
            # Check for correct $in usage
            if "cateName" in query:
                if isinstance(query["cateName"], dict) and "$in" in query["cateName"]:
                    print(f"   ✅ Correctly using $in operator")
                elif isinstance(query["cateName"], list):
                    print(f"   ❌ ERROR: Raw array without $in operator!")
                else:
                    print(f"   ✅ Single category (no $in needed)")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

def test_category_mapping():
    """Test category mapping for 'คอม' specifically"""
    print("\n🧪 Testing Category Mapping for 'คอม'")
    print("=" * 40)
    
    mapping = get_comprehensive_category_mapping()
    
    # Test different computer-related terms
    test_terms = ['คอม', 'คอมพิวเตอร์', 'อยากได้คอม']
    
    for term in test_terms:
        print(f"\nTerm: '{term}'")
        if term in mapping:
            print(f"  Maps to: {mapping[term]}")
        else:
            print(f"  No direct mapping found")
            
        # Check if any key contains this term
        for key, categories in mapping.items():
            if term in key or key in term:
                print(f"  Found in key '{key}': {categories}")

if __name__ == "__main__":
    test_category_mapping()
    test_query_building()
    print("\n🎉 Testing completed!")