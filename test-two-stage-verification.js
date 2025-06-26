/**
 * Test Two-Stage LLM Verification System
 * Tests the enhanced chatbot with product result validation and retry mechanism
 */

async function testChatbot(query) {
  console.log(`\n🧪 Testing: "${query}"`);
  console.log('='.repeat(80));
  
  try {
    const response = await fetch('http://localhost:3000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: query }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    console.log('📊 Results Summary:');
    console.log(`   Products found: ${data.products?.length || 0}`);
    console.log(`   Validation: ${data.validationInfo?.isValid ? '✅ VALID' : '❌ INVALID'}`);
    console.log(`   Retry attempted: ${data.validationInfo?.hasRetried ? '🔄 YES' : '⏭️ NO'}`);
    
    if (data.validationInfo?.issues?.length > 0) {
      console.log(`   Issues found: ${data.validationInfo.issues.join(', ')}`);
    }
    
    console.log('\n💬 AI Response:');
    console.log(data.response);
    
    if (data.products && data.products.length > 0) {
      console.log('\n🛍️ Top Products:');
      data.products.slice(0, 3).forEach((product, index) => {
        console.log(`   ${index + 1}. ${product.title}`);
        console.log(`      💰 ฿${product.salePrice.toLocaleString()}`);
        console.log(`      📂 ${product.navigation?.categoryMessage1} > ${product.navigation?.categoryMessage2}`);
      });
    }
    
    return data;
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    return null;
  }
}

async function runTests() {
  console.log('🚀 Starting Two-Stage LLM Verification Tests');
  console.log('Testing various scenarios to ensure products match user intent');
  
  const testCases = [
    // Test 1: Complete computer request - should get notebooks, not components
    "อยากได้คอมทำงานกราฟิก แนะนำหน่อย",
    
    // Test 2: Component request - should get graphics cards, not complete computers
    "การ์ดจอ RTX 4060 แนะนำหน่อย",
    
    // Test 3: Budget constraint test
    "โน้ตบุ๊คเล่นเกมงบ 30000",
    
    // Test 4: Specific technical query
    "Ryzen 5 5600G เล่นเกมได้ไหม",
    
    // Test 5: Price inquiry
    "โน้ตบุ๊คราคาเริ่มต้นเท่าไหร่",
    
    // Test 6: Comparison request
    "DDR4 กับ DDR5 ต่างกันยังไง"
  ];
  
  for (const testCase of testCases) {
    await testChatbot(testCase);
    
    // Wait a bit between tests to avoid overwhelming the API
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  console.log('\n✅ All tests completed!');
  console.log('Review the results above to ensure:');
  console.log('1. Products match user intent (complete computers vs components)');
  console.log('2. Budget constraints are respected');
  console.log('3. Technical questions get appropriate responses');
  console.log('4. Validation catches mismatches and triggers retries when needed');
}

// Run the tests
runTests().catch(console.error);