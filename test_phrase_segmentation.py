#!/usr/bin/env python3
"""
Test script for improved contextual phrase segmentation
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.two_stage_llm import contextual_phrase_segmentation, extract_basic_entities

def test_phrase_segmentation():
    """Test the improved phrase segmentation"""
    print("🧪 Testing Contextual Phrase Segmentation")
    print("=" * 50)
    
    test_cases = [
        {
            "input": "อยากได้คอมทำงานกราฟิก แนะนำหน่อย",
            "expected": ["อยากได้คอม", "ทำงานกราฟิก", "แนะนำหน่อย"]
        },
        {
            "input": "โน้ตบุ๊ค ASUS งบ 20000",
            "expected": ["โน้ตบุ๊ก", "ASUS", "งบ 20000"]
        },
        {
            "input": "การ์ดจอเล่นเกม RTX 4060",
            "expected": ["การ์ดจอ", "เล่นเกม", "RTX 4060"]
        },
        {
            "input": "เมาส์เกมมิ่งไร้สาย RGB ไม่เกิน 3000",
            "expected": ["เมาส์", "เล่นเกม", "ไร้สาย", "RGB", "ไม่เกิน 3000"]
        },
        {
            "input": "คีย์บอร์ด mechanical สำหรับทำงาน",
            "expected": ["คีย์บอร์ด", "mechanical", "สำหรับทำงาน"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['input']}")
        
        # Test segmentation
        result = contextual_phrase_segmentation(test_case['input'])
        print(f"  Result: {result}")
        print(f"  Expected: {test_case['expected']}")
        
        # Check if key phrases are captured
        has_important_phrases = any(
            expected in ' '.join(result) for expected in test_case['expected']
        )
        
        if has_important_phrases:
            print(f"  ✅ Key phrases captured")
        else:
            print(f"  ❌ Missing important phrases")

def test_entity_extraction():
    """Test the improved entity extraction with phrase segmentation"""
    print("\n🧪 Testing Entity Extraction with Phrase Segmentation")
    print("=" * 50)
    
    test_cases = [
        {
            "input": "อยากได้คอมทำงานกราฟิก แนะนำหน่อย",
            "description": "Graphics work computer request"
        },
        {
            "input": "โน้ตบุ๊ค ASUS งบ 20000", 
            "description": "ASUS notebook with budget"
        },
        {
            "input": "เมาส์เกมมิ่งไร้สาย RGB ไม่เกิน 3000",
            "description": "Wireless gaming mouse with RGB under 3k"
        }
    ]
    
    # Mock categories data
    categories_data = ["Desktop PC", "Notebooks", "Mouse", "Gaming Mouse", "Graphics Cards"]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        print(f"Input: {test_case['input']}")
        
        try:
            result = extract_basic_entities(test_case['input'], categories_data)
            
            print(f"✅ Segmented Phrases: {result.get('segmentedPhrases', [])}")
            print(f"✅ Used: {result.get('used', [])}")
            print(f"✅ Remaining: {result.get('remaining', [])}")
            print(f"✅ Category: {result.get('category', 'None')}")
            print(f"✅ Budget: {result.get('budget', 'None')}")
            print(f"✅ Analysis: {result.get('analysis', 'None')}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_phrase_segmentation()
    test_entity_extraction()
    
    print("\n🎉 Testing completed!")