/**
 * Test AI Helpers Functions Directly
 * Tests the two-stage LLM system without MongoDB dependency
 */

import { validateProductResults, generateOptimalMongoQueryWithRetry } from './lib/ai-helpers.ts';

async function testQueryGeneration() {
  console.log('🧪 Testing Query Generation with Retry...\n');
  
  const testCases = [
    "อยากได้คอมทำงานกราฟิก แนะนำหน่อย",
    "การ์ดจอ RTX 4060 แนะนำหน่อย", 
    "โน้ตบุ๊คเล่นเกมงบ 30000"
  ];
  
  for (const query of testCases) {
    console.log(`\n🔍 Testing: "${query}"`);
    console.log('='.repeat(60));
    
    try {
      const result = await generateOptimalMongoQueryWithRetry(query);
      
      console.log('📊 Generated Query:');
      console.log(JSON.stringify(result.query, null, 2));
      
      console.log('\n🎯 Extracted Entities:');
      console.log(`   Product Type: ${result.entities.productType}`);
      console.log(`   Category: ${result.entities.category}`);
      console.log(`   Usage: ${result.entities.usage}`);
      console.log(`   Intent: ${result.entities.intent}`);
      console.log(`   Budget: ${JSON.stringify(result.entities.budget)}`);
      
      console.log('\n💭 Reasoning:');
      console.log(result.reasoning);
      
      if (result.retryInfo) {
        console.log('\n🔄 Retry Info:');
        console.log(`   Attempt: ${result.retryInfo.attempt}`);
        console.log(`   Previous Issues: ${result.retryInfo.previousIssues.join(', ')}`);
        console.log(`   Modifications: ${result.retryInfo.modifications.join(', ')}`);
      }
      
    } catch (error) {
      console.error('❌ Error:', error.message);
    }
  }
}

async function testProductValidation() {
  console.log('\n\n🧪 Testing Product Validation...\n');
  
  // Mock product data for testing
  const mockProducts = [
    {
      title: "Gaming Laptop RTX 4060",
      salePrice: 35000,
      navigation: {
        categoryMessage1: "NOTEBOOKS",
        categoryMessage2: "Gaming Notebooks", 
        categoryMessage3: "High Performance"
      },
      rating: 4.5,
      totalReviews: 120,
      stockQuantity: 5,
      productView: 2500
    },
    {
      title: "RTX 4060 Graphics Card",
      salePrice: 15000,
      navigation: {
        categoryMessage1: "COMPUTER HARDWARE (DIY)",
        categoryMessage2: "Graphics Cards",
        categoryMessage3: "Nvidia GeForce 40 Series"
      },
      rating: 4.8,
      totalReviews: 89,
      stockQuantity: 12,
      productView: 1800
    }
  ];
  
  const testCases = [
    {
      input: "อยากได้คอมทำงานกราฟิก แนะนำหน่อย",
      entities: {
        productType: "complete_computer",
        category: "NOTEBOOKS",
        usage: "กราฟิก",
        intent: "recommendation"
      },
      products: mockProducts,
      expected: "Should prefer complete computer (Gaming Laptop)"
    },
    {
      input: "การ์ดจอ RTX 4060 แนะนำหน่อย",
      entities: {
        productType: "component", 
        category: "COMPUTER HARDWARE (DIY)",
        subCategory: "Graphics Cards",
        intent: "recommendation",
        specs: ["RTX 4060"]
      },
      products: mockProducts,
      expected: "Should prefer graphics card component"
    }
  ];
  
  for (const testCase of testCases) {
    console.log(`\n🔍 Testing: "${testCase.input}"`);
    console.log(`Expected: ${testCase.expected}`);
    console.log('='.repeat(60));
    
    try {
      const validation = await validateProductResults(
        testCase.input,
        testCase.entities,
        testCase.products,
        "Test reasoning"
      );
      
      console.log(`✅ Validation Result: ${validation.isValid ? 'VALID' : 'INVALID'}`);
      console.log(`🔄 Needs Retry: ${validation.needsRetry ? 'YES' : 'NO'}`);
      
      if (validation.issues.length > 0) {
        console.log(`⚠️  Issues: ${validation.issues.join(', ')}`);
      }
      
      if (validation.suggestions.length > 0) {
        console.log(`💡 Suggestions: ${validation.suggestions.join(', ')}`);
      }
      
      console.log(`🎯 Valid Products: ${validation.validProducts.length}/${testCase.products.length}`);
      validation.validProducts.forEach((product, index) => {
        console.log(`   ${index + 1}. ${product.title}`);
      });
      
    } catch (error) {
      console.error('❌ Validation Error:', error.message);
    }
  }
}

async function runTests() {
  console.log('🚀 Testing Two-Stage LLM System Components');
  console.log('=' .repeat(80));
  
  await testQueryGeneration();
  await testProductValidation();
  
  console.log('\n\n✅ All component tests completed!');
  console.log('Review results to ensure:');
  console.log('1. Query generation understands user intent correctly');
  console.log('2. Product validation catches mismatches between intent and results');
  console.log('3. Retry mechanism provides appropriate suggestions');
}

runTests().catch(console.error);