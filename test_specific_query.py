#!/usr/bin/env python3
"""
Test the specific problematic query mentioned by user
"""

import asyncio
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.ai_helpers_v3 import generate_optimal_mongo_query_v3

async def test_specific_problematic_query():
    """Test the exact query user had problems with"""
    
    print("🎯 Testing User's Specific Problematic Query")
    print("="*60)
    
    user_input = "มีโน้ตบุ๊คราคาไม่เกิน 15,000 ไหม"
    
    print(f"INPUT: \"{user_input}\"")
    print("\nEXPECTED PERFECT QUERY:")
    expected_query = {
        "stockQuantity": {"$gt": 0},
        "cateName": "Notebooks",
        "salePrice": {"$lte": 15000}
    }
    print(json.dumps(expected_query, ensure_ascii=False, indent=2))
    
    print("\nRUNNING V3 SYSTEM...")
    print("-" * 40)
    
    try:
        result = await generate_optimal_mongo_query_v3(user_input)
        
        actual_query = result["query"]
        print("ACTUAL QUERY GENERATED:")
        print(json.dumps(actual_query, ensure_ascii=False, indent=2))
        
        print("\n📊 VALIDATION RESULTS:")
        
        # Check each component
        issues = []
        
        # 1. stockQuantity check
        if actual_query.get("stockQuantity", {}).get("$gt") == 0:
            print("✅ stockQuantity: Correct")
        else:
            print("❌ stockQuantity: Missing or incorrect")
            issues.append("stockQuantity")
        
        # 2. cateName check  
        if actual_query.get("cateName") == "Notebooks":
            print("✅ cateName: Perfect match")
        elif "cateName" in actual_query:
            print(f"⚠️  cateName: Got '{actual_query['cateName']}', expected 'Notebooks'")
            issues.append("cateName mismatch")
        else:
            print("❌ cateName: Missing")
            issues.append("cateName missing")
        
        # 3. salePrice check
        if actual_query.get("salePrice", {}).get("$lte") == 15000:
            print("✅ salePrice: Perfect budget filter")
        elif "salePrice" in actual_query:
            print(f"⚠️  salePrice: Got {actual_query['salePrice']}, expected {{'$lte': 15000}}")
            issues.append("salePrice mismatch")
        else:
            print("❌ salePrice: Missing budget filter")
            issues.append("salePrice missing")
        
        # 4. productActive check (should NOT exist)
        if "productActive" in actual_query:
            print("❌ productActive: Invalid field present!")
            issues.append("invalid productActive")
        else:
            print("✅ productActive: Correctly absent")
        
        # 5. $or check (should not be needed for exact category match)
        if "$or" in actual_query:
            print("⚠️  $or: Using text search instead of exact category match")
            issues.append("unnecessary $or")
        else:
            print("✅ $or: Correctly absent (using exact match)")
        
        print(f"\n🎯 OVERALL SCORE:")
        total_checks = 5
        passed_checks = total_checks - len(issues)
        score = (passed_checks / total_checks) * 100
        print(f"   {passed_checks}/{total_checks} checks passed ({score:.1f}%)")
        
        if len(issues) == 0:
            print("🎉 PERFECT! Query matches expected output exactly!")
        else:
            print(f"⚠️  Issues found: {', '.join(issues)}")
        
        # Show additional info
        print(f"\n📋 Additional Info:")
        print(f"   Confidence: {result.get('confidence', 0)}")
        print(f"   Reasoning: {result.get('reasoning', 'N/A')}")
        
        entities = result.get("entities", {})
        if entities:
            print(f"   Entities: {entities}")
        
        warnings = result.get('validationWarnings', [])
        if warnings:
            print(f"   Warnings: {warnings}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_specific_problematic_query())