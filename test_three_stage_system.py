#!/usr/bin/env python3
"""
Test script for THREE-STAGE LLM system
ทดสอบระบบ 3 ขั้นตอน LLM ที่ปรับปรุงใหม่
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.two_stage_llm import (
    contextual_phrase_segmentation,
    extract_basic_entities,
    build_basic_query,
    is_non_filter_phrase,
    extract_question_phrases,
    is_question_phrase
)

def test_improved_phrase_segmentation():
    """Test improved phrase segmentation with non-filter detection"""
    print("=== IMPROVED PHRASE SEGMENTATION TEST ===")
    
    test_cases = [
        "อยากได้คอมทำงานกราฟิก แนะนำหน่อย",
        "Ryzen 5 5600G เล่นเกมได้ไหม",  
        "โน้ตบุ๊ค ASUS งบ 20000 ดีไหม",
        "การ์ดจอ RTX 4060 ใช้งานเป็นอย่างไร"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i}. Input: \"{test_input}\"")
        phrases = contextual_phrase_segmentation(test_input)
        print(f"   Segmented Phrases: {phrases}")
        
        # Check for non-filter phrases
        filter_phrases = []
        non_filter_phrases = []
        question_phrases = []
        
        for phrase in phrases:
            if is_non_filter_phrase(phrase):
                non_filter_phrases.append(phrase)
            else:
                filter_phrases.append(phrase)
            
            if is_question_phrase(phrase):
                question_phrases.append(phrase)
        
        print(f"   ✅ Filter Phrases: {filter_phrases}")
        print(f"   ❌ Non-Filter Phrases: {non_filter_phrases}")
        print(f"   ❓ Question Phrases: {question_phrases}")

def test_three_stage_entity_processing():
    """Test entity processing for three-stage system"""
    print("\n\n=== THREE-STAGE ENTITY PROCESSING TEST ===")
    
    test_cases = [
        "อยากได้คอมทำงานกราฟิก แนะนำหน่อย",
        "Ryzen 5 5600G เล่นเกมได้ไหม",
        "โน้ตบุ๊ค ASUS งบ 20000 ดีไหม"
    ]
    
    categories_data = ['Desktop PC', 'Notebooks', 'CPU', 'Graphics Cards', 'Gaming Notebooks']
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i}. Input: \"{test_input}\"")
        
        # Extract entities
        entities = extract_basic_entities(test_input, categories_data)
        
        print(f"   Segmented Phrases: {entities['segmentedPhrases']}")
        print(f"   Used (Stage 1 filtering): {entities['used']}")
        print(f"   Remaining (Stage 2+3): {entities['remaining']}")
        
        # Build query
        query = build_basic_query(entities)
        print(f"   MongoDB Query: {query}")
        
        # Extract questions for Stage 3
        question_phrases = extract_question_phrases(entities['remaining'])
        non_question_remaining = [p for p in entities['remaining'] if p not in question_phrases]
        
        print(f"   Stage 2 Content Analysis: {non_question_remaining}")
        print(f"   Stage 3 Questions: {question_phrases}")
        
        # Show expected behavior
        print(f"   ✅ Expected Flow:")
        print(f"     - Stage 1: กรอง {entities['used']} → MongoDB Query")
        if non_question_remaining:
            print(f"     - Stage 2: วิเคราะห์เนื้อหา {non_question_remaining} → Product Matching")
        if question_phrases:
            print(f"     - Stage 3: ตอบคำถาม {question_phrases} → Answer Generation")

def test_stage_classification():
    """Test phrase classification for different stages"""
    print("\n\n=== STAGE CLASSIFICATION TEST ===")
    
    phrases = [
        "อยากได้คอม",        # Stage 1 - Category filter
        "งบ 20000",           # Stage 1 - Budget filter  
        "ASUS",               # Stage 2 - Brand matching
        "RTX 4060",           # Stage 2 - Product matching
        "ทำงานกราฟิก",        # Stage 2 - Usage analysis
        "แนะนำหน่อย",         # Non-filter - Skip
        "เล่นเกมได้ไหม",      # Stage 3 - Question
        "ดีไหม",             # Stage 3 - Question
        "รุ่นไหนดี"           # Non-filter - Skip
    ]
    
    print("| Phrase | Stage 1 Filter | Stage 2 Content | Stage 3 Question | Skip |")
    print("|--------|----------------|------------------|-------------------|------|")
    
    for phrase in phrases:
        is_non_filter = is_non_filter_phrase(phrase)
        is_question = is_question_phrase(phrase)
        
        stage1 = "❌" if is_non_filter else "✅"
        stage2 = "✅" if not is_non_filter and not is_question else "❌"
        stage3 = "✅" if is_question else "❌"
        skip = "✅" if is_non_filter and not is_question else "❌"
        
        print(f"| {phrase:<15} | {stage1:<13} | {stage2:<15} | {stage3:<16} | {skip:<4} |")

def main():
    """Main test function"""
    print("🚀 Testing THREE-STAGE LLM System")
    print("=" * 60)
    
    test_improved_phrase_segmentation()
    test_three_stage_entity_processing()
    test_stage_classification()
    
    print("\n\n✅ Test completed!")
    print("\n🎯 **Three-Stage System Summary:**")
    print("**Stage 1**: Basic MongoDB filtering (category, budget, stock)")
    print("  - Uses: หมวดหมู่ชัดเจน, งบประมาณ, ชื่อผลิตภัณฑ์เฉพาะ (สำหรับ category inference)")
    print("  - Skips: คำขอ ('แนะนำหน่อย'), คำถาม ('เล่นเกมได้ไหม')")
    print()
    print("**Stage 2**: Content analysis and product matching")
    print("  - Uses: แบรนด์, สเปค, การใช้งาน, ชื่อผลิตภัณฑ์เฉพาะ")  
    print("  - Searches: title และ description")
    print()
    print("**Stage 3**: Question answering")
    print("  - Uses: คำถาม ('เล่นเกมได้ไหม', 'ดีไหม', 'เป็นอย่างไร')")
    print("  - Analyzes: ข้อมูลสินค้าที่คัดเลือกแล้วจาก Stage 1+2")
    print("  - Answers: ตอบคำถามด้วยความรู้ IT + ข้อมูลสินค้า")

if __name__ == "__main__":
    main()