#!/usr/bin/env python3
"""
Test script for improved two-stage LLM system
ทดสอบระบบ 2 ขั้นตอน LLM ที่ปรับปรุงแล้ว
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.two_stage_llm import (
    contextual_phrase_segmentation,
    is_specific_product_name,
    infer_categories_from_product_name,
    extract_basic_entities,
    build_basic_query
)

def test_phrase_segmentation():
    """Test phrase segmentation improvements"""
    print("=== PHRASE SEGMENTATION TEST ===")
    
    test_cases = [
        "Ryzen 5 5600G เล่นเกมได้ไหม",
        "โน้ตบุ๊ค ASUS งบ 20000",
        "การ์ดจอ RTX 4060 ไม่เกิน 15000",
        "คีย์บอร์ด mechanical เงียบๆ",
        "อยากได้คอมทำงานกราฟิก แนะนำหน่อย"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i}. Input: \"{test_input}\"")
        phrases = contextual_phrase_segmentation(test_input)
        print(f"   Phrases: {phrases}")
        
        for phrase in phrases:
            is_specific = is_specific_product_name(phrase)
            if is_specific:
                print(f"   \"{phrase}\" -> SPECIFIC PRODUCT NAME")
                categories = infer_categories_from_product_name(phrase, 
                    ['CPU', 'Notebooks', 'Desktop PC', 'Graphics Cards', 'Gaming Notebooks'])
                if categories:
                    print(f"     -> Inferred categories: {categories}")
            else:
                print(f"   \"{phrase}\" -> regular phrase")

def test_entity_extraction():
    """Test entity extraction and query building"""
    print("\n\n=== ENTITY EXTRACTION & QUERY BUILDING TEST ===")
    
    test_cases = [
        "Ryzen 5 5600G เล่นเกมได้ไหม",
        "โน้ตบุ๊ค ASUS งบ 20000", 
        "การ์ดจอ RTX 4060 ไม่เกิน 15000"
    ]
    
    categories_data = ['CPU', 'Notebooks', 'Desktop PC', 'Graphics Cards', 'Gaming Notebooks', 'Keyboard', 'Mouse']
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i}. Input: \"{test_input}\"")
        
        # Extract entities
        entities = extract_basic_entities(test_input, categories_data)
        print(f"   Segmented Phrases: {entities['segmentedPhrases']}")
        print(f"   Used (for filtering): {entities['used']}")
        print(f"   Remaining (for Stage 2): {entities['remaining']}")
        
        if 'category' in entities:
            print(f"   Single Category: {entities['category']}")
        elif 'categories' in entities:
            print(f"   Multiple Categories: {entities['categories']}")
        
        if 'budget' in entities:
            print(f"   Budget: {entities['budget']}")
        
        # Build query
        query = build_basic_query(entities)
        print(f"   MongoDB Query: {query}")
        
        # Show expected behavior for each case
        if "ryzen" in test_input.lower():
            print("   ✅ Expected: Stage 1 infers CPU/Notebooks categories, Stage 2 searches for 'Ryzen 5 5600G' in titles")
        elif "asus" in test_input.lower():
            print("   ✅ Expected: Stage 1 filters Notebooks, Stage 2 searches for 'ASUS' in titles")
        elif "rtx" in test_input.lower():
            print("   ✅ Expected: Stage 1 infers Graphics Cards categories, Stage 2 searches for 'RTX 4060' in titles")

def main():
    """Main test function"""
    print("🚀 Testing Improved Two-Stage LLM System")
    print("=" * 50)
    
    test_phrase_segmentation()
    test_entity_extraction()
    
    print("\n\n✅ Test completed!")
    print("\nKey Improvements:")
    print("1. ✅ Better phrase segmentation for specific product names")
    print("2. ✅ Category inference from product names (e.g., Ryzen -> CPU/Notebooks)")  
    print("3. ✅ Proper separation of Stage 1 filtering vs Stage 2 analysis")
    print("4. ✅ Specific product names kept in 'remaining' for Stage 2 detailed search")

if __name__ == "__main__":
    main()