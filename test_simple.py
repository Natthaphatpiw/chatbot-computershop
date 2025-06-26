#!/usr/bin/env python3
"""
Simple test to identify the string formatting issue
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.two_stage_llm import normalize_text_advanced, get_comprehensive_category_mapping

async def test_basic_functions():
    print("Testing basic functions...")
    
    # Test normalization
    test_text = "โน้ตบุ๊ค ASUS"
    normalized = normalize_text_advanced(test_text)
    print(f"Normalized: '{test_text}' → '{normalized}'")
    
    # Test category mapping  
    mapping = get_comprehensive_category_mapping()
    print(f"Category mapping loaded: {len(mapping)} entries")
    
    print("✅ Basic functions work!")

async def test_stage1_minimal():
    print("\nTesting Stage 1 with minimal prompt...")
    
    # Import the function
    from app.services.two_stage_llm import stage1_basic_query_builder
    
    # Set a dummy API key
    os.environ.setdefault('OPENAI_API_KEY', 'test-key')
    
    try:
        result = await stage1_basic_query_builder("โน้ตบุ๊ค")
        print(f"✅ Stage 1 Success: {result}")
    except Exception as e:
        print(f"❌ Stage 1 Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_basic_functions())
    asyncio.run(test_stage1_minimal())