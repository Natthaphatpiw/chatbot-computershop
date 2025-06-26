// Test script for problematic queries
const testQueries = [
  // Complete computer queries (should recommend full computers)
  {
    query: "อยากได้คอมทำงานกราฟิก แนะนำหน่อย",
    expected: "Should recommend complete computers (notebooks/workstations), NOT graphics cards"
  },
  {
    query: "มีโน้ตบุ๊คราคาไม่เกิน 15,000 ไหม",
    expected: "Should show notebooks only"
  },
  {
    query: "คอมเล่นเกมราคาไม่แพง",
    expected: "Should recommend gaming computers, not individual components"
  },
  
  // Component queries (should recommend specific components)
  {
    query: "การ์ดจอทำกราฟิกแนะนำอะไร",
    expected: "Should recommend graphics cards specifically"
  },
  {
    query: "RAM DDR4 กับ DDR5 ต่างกันยังไง",
    expected: "Should compare RAM and show RAM products"
  },
  {
    query: "Ryzen 5 5600G เล่นเกมได้ไหม",
    expected: "Should answer about CPU capability and show CPU products"
  },
  
  // Build component queries
  {
    query: "คอมพิวเตอร์ประกอบราคาเริ่มต้นที่เท่าไหร่",
    expected: "Should show PC building components and pricing"
  }
]

async function testChatbot() {
  console.log("Testing chatbot with computer vs component queries...\n")
  
  for (const testCase of testQueries) {
    console.log(`🔍 Testing: "${testCase.query}"`)
    console.log(`📋 Expected: ${testCase.expected}`)
    
    try {
      const response = await fetch('http://localhost:3000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: testCase.query })
      })
      
      if (!response.ok) {
        console.log(`❌ Failed: ${response.status} ${response.statusText}`)
        continue
      }
      
      const data = await response.json()
      console.log(`✅ Response: ${data.response?.substring(0, 150)}...`)
      console.log(`📦 Products found: ${data.products?.length || 0}`)
      
      // Analyze product categories
      if (data.products && data.products.length > 0) {
        const categories = data.products.map(p => p.navigation?.categoryMessage1).filter(Boolean)
        const uniqueCategories = [...new Set(categories)]
        console.log(`📂 Categories: ${uniqueCategories.join(', ')}`)
        
        // Check if results match expectation
        const hasNotebooks = uniqueCategories.some(cat => cat.includes('NOTEBOOKS'))
        const hasWorkstation = uniqueCategories.some(cat => cat.includes('WORKSTATION'))
        const hasHardware = uniqueCategories.some(cat => cat.includes('COMPUTER HARDWARE'))
        
        if (testCase.expected.includes('complete computers') && (hasNotebooks || hasWorkstation)) {
          console.log('✅ Correctly recommended complete computers')
        } else if (testCase.expected.includes('components') && hasHardware) {
          console.log('✅ Correctly recommended components')
        } else if (testCase.expected.includes('notebooks') && hasNotebooks) {
          console.log('✅ Correctly recommended notebooks')
        } else {
          console.log('⚠️  Results may not match expectation')
        }
      }
      
    } catch (error) {
      console.log(`❌ Error: ${error.message}`)
    }
    
    console.log("---\n")
  }
}

testChatbot().catch(console.error)