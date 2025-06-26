#!/usr/bin/env python3
"""
Test Enhanced Three-Stage System
ทดสอบระบบ chatbot 3 stage ที่ปรับปรุงแล้วตามความต้องการของผู้ใช้
"""

import asyncio
import json
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.two_stage_llm import (
    enhanced_contextual_phrase_segmentation,
    stage1_context_analysis_and_query_builder,
    normalize_text_advanced
)

def test_enhanced_phrase_segmentation():
    """ทดสอบระบบแยกวลีใหม่"""
    print("🧠 Testing Enhanced Phrase Segmentation")
    print("=" * 50)
    
    test_cases = [
        "อยากได้คอมทำงานกราฟิก แนะนำหน่อย",
        "โน้ตบุ๊คราคาไม่เกิน 15000 ไหม",
        "โน้ตบุ๊กเล่นเกม valorant ราคาไม่เกิน 25000",
        "Ryzen 5 5600G เล่นเกมได้ไหม",
        "เมาส์ gaming ASUS RGB งบ 2000",
        "การ์ดจอ RTX 4060 สำหรับเล่นเกม"
    ]
    
    for i, input_text in enumerate(test_cases, 1):
        print(f"\n{i}. Input: \"{input_text}\"")
        
        # Test enhanced segmentation
        result = enhanced_contextual_phrase_segmentation(input_text)
        
        print(f"   Segmented phrases: {len(result['segmented_phrases'])}")
        for phrase_info in result['segmented_phrases']:
            print(f"     - \"{phrase_info['phrase']}\" ({phrase_info['type']}) → {phrase_info['stage']}")
        
        print(f"   Stage assignments:")
        for stage, phrases in result['stage_assignments'].items():
            if phrases:
                print(f"     {stage}: {phrases}")

async def test_stage1_analysis():
    """ทดสอบ Stage 1 ใหม่"""
    print("\n\n🔍 Testing Enhanced Stage 1 Analysis")
    print("=" * 50)
    
    test_cases = [
        "อยากได้คอมทำงานกราฟิก แนะนำหน่อย",
        "โน้ตบุ๊คราคาไม่เกิน 15000 ไหม", 
        "Ryzen 5 5600G เล่นเกมได้ไหม",
        "เมาส์ gaming ASUS RGB งบ 2000"
    ]
    
    for i, input_text in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: \"{input_text}\"")
        
        try:
            result = await stage1_context_analysis_and_query_builder(input_text)
            
            print(f"   Query: {json.dumps(result['query'], ensure_ascii=False)}")
            print(f"   Stage assignments:")
            
            stage_assignments = result.get('stageAssignments', {})
            for stage, phrases in stage_assignments.items():
                if phrases:
                    print(f"     {stage}: {phrases}")
            
            print(f"   Reasoning: {result.get('reasoning', 'N/A')}")
            
        except Exception as e:
            print(f"   Error: {e}")

def test_phrase_classification():
    """ทดสอบการจัดหมวดหมู่วลี"""
    print("\n\n📝 Testing Phrase Classification")
    print("=" * 50)
    
    test_phrases = [
        "อยากได้คอม",      # stage1_filter - product desire
        "โน้ตบุ๊ก",         # stage1_filter - category 
        "งบ 20000",        # stage1_filter - budget
        "Ryzen 5 5600G",   # stage1_inference - specific product
        "ASUS",            # stage2_content - brand
        "ทำงานกราฟิก",      # stage2_content - usage
        "เล่นเกม valorant", # stage2_content - gaming usage
        "แนะนำหน่อย",       # stage3_questions - recommendation
        "เล่นเกมได้ไหม",    # stage3_questions - question
        "RGB",             # stage2_content - specification
    ]
    
    for phrase in test_phrases:
        result = enhanced_contextual_phrase_segmentation(phrase)
        if result['segmented_phrases']:
            phrase_info = result['segmented_phrases'][0]
            print(f"   \"{phrase}\" → {phrase_info['type']} ({phrase_info['stage']})")
        else:
            print(f"   \"{phrase}\" → No classification")

def test_examples_from_description():
    """ทดสอบตัวอย่างที่ผู้ใช้ให้มา"""
    print("\n\n🎯 Testing User Examples")
    print("=" * 50)
    
    examples = [
        {
            "input": "อยากได้คอมทำงานกราฟิก แนะนำหน่อย",
            "expected_phrases": ["อยากได้คอม", "ทำงานกราฟิก", "แนะนำหน่อย"],
            "expected_stage1_filter": ["อยากได้คอม"],
            "expected_stage2_content": ["ทำงานกราฟิก"],
            "expected_stage3_questions": ["แนะนำหน่อย"]
        },
        {
            "input": "มีโน้ตบุ๊คราคาไม่เกิน 15,000 ไหม",
            "expected_phrases": ["มีโน้ตบุ๊ค", "ราคาไม่เกิน 15,000 ไหม"],
            "expected_stage1_filter": ["โน้ตบุ๊ก", "ไม่เกิน 15000"],
            "expected_stage3_questions": ["มีไหม"]
        },
        {
            "input": "โน้ตบุ๊กเล่นเกม valorant ราคาไม่เกิน 25000",
            "expected_phrases": ["โน้ตบุ๊ก", "เล่นเกม valorant", "ราคาไม่เกิน 25000"],
            "expected_stage1_filter": ["โน้ตบุ๊ก", "ไม่เกิน 25000"],
            "expected_stage2_content": ["เล่นเกม valorant"]
        },
        {
            "input": "Ryzen 5 5600G เล่นเกมได้ไหม",
            "expected_phrases": ["Ryzen 5 5600G", "เล่นเกมได้ไหม"],
            "expected_stage1_inference": ["Ryzen 5 5600G"],
            "expected_stage2_content": ["Ryzen 5 5600G"],
            "expected_stage3_questions": ["เล่นเกมได้ไหม"]
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. Testing: \"{example['input']}\"")
        
        result = enhanced_contextual_phrase_segmentation(example['input'])
        phrases = [p['phrase'] for p in result['segmented_phrases']]
        
        print(f"   Expected phrases: {example['expected_phrases']}")
        print(f"   Actual phrases: {phrases}")
        
        stage_assignments = result['stage_assignments']
        print(f"   Stage assignments:")
        for stage, actual_phrases in stage_assignments.items():
            if actual_phrases:
                expected_key = f"expected_{stage}"
                expected = example.get(expected_key, [])
                status = "✅" if set(actual_phrases) == set(expected) else "❌"
                print(f"     {stage}: {actual_phrases} {status}")

async def main():
    """ฟังก์ชันหลักสำหรับทดสอบ"""
    print("🚀 Testing Enhanced Three-Stage System")
    print("=" * 60)
    
    # Test phrase segmentation
    test_enhanced_phrase_segmentation()
    
    # Test phrase classification
    test_phrase_classification()
    
    # Test user examples
    test_examples_from_description()
    
    # Test Stage 1 analysis
    await test_stage1_analysis()
    
    print("\n\n✅ Testing completed!")
    print("\n🎯 **Enhanced Three-Stage System Summary:**")
    print("**Stage 1**: Context analysis + phrase segmentation + basic filtering")
    print("  - Filter phrases: หมวดหมู่ชัดเจน, งบประมาณ")
    print("  - Inference phrases: ชื่อผลิตภัณฑ์เฉพาะ (อนุมานหมวดหมู่)")
    print("  - Output: MongoDB query + phrase assignments for other stages")
    print()
    print("**Stage 2**: Content analysis of assigned phrases")
    print("  - Content phrases: แบรนด์, การใช้งาน, สเปค, ชื่อผลิตภัณฑ์เฉพาะ")
    print("  - Analysis: title (แบรนด์/ชื่อผลิตภัณฑ์) + description (การใช้งาน/สเปค)")
    print()
    print("**Stage 3**: Question answering using filtered products")
    print("  - Question phrases: คำถาม, คำขอแนะนำ")
    print("  - Analysis: ตอบคำถามจากข้อมูลสินค้าที่ผ่าน Stage 1+2")

if __name__ == "__main__":
    asyncio.run(main()) 