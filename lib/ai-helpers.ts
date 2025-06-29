import { openai } from "@ai-sdk/openai"
import { generateText } from "ai"
import type { Product, ExtractedEntities, MongoQueryWithReason } from "@/types"
import { CategoryMapper } from "./category-mapper"

// Text normalization function
export function normalizeText(text: string): string {
  return text
    .replace(/โน้?[ดต๊]บุ๊?[คก]/g, 'โน้ตบุ๊ก')
    .replace(/การ์[จด]อ/g, 'การ์ดจอ')
    .replace(/[วฟ]ีจีเอ/g, 'การ์ดจอ')
    .replace(/กราฟิ?[คกข]/g, 'การ์ดจอ')
    .replace(/แรม/g, 'แรม')
    .replace(/ram/gi, 'แรม')
    .replace(/memory/gi, 'แรม')
    .replace(/หน่วยความจำ/g, 'แรม')
    .replace(/คอมพิ?วเ?ตอร์/g, 'คอมพิวเตอร์')
    .replace(/(\d+)k/gi, (_, p1) => (parseInt(p1) * 1000).toString())
    .replace(/เม้าส์/g, 'เมาส์')
    .replace(/คีบอร์ด/g, 'คีย์บอร์ด')
    .replace(/คีบอด/g, 'คีย์บอร์ด')
    .replace(/ซีพียู/g, 'ซีพียู')
    .replace(/cpu/gi, 'ซีพียู')
    .replace(/โปรเซส[เซส]อร์/g, 'ซีพียู')
}

// Category keyword mapping
export function getCategoryKeywords(categoryInput: string): string[] {
  const categoryMap: Record<string, string[]> = {
    'โน้ตบุ๊ก': ['notebook', 'laptop', 'โน้ตบุ๊ก', 'โน้ตบุ้ค', 'โน๊ตบุ๊ค', 'โน้ดบุ๊ค', 'โนตบุ๊ก', 'โน้ต', 'โนต'],
    'คีย์บอร์ด': ['keyboard', 'คีย์บอร์ด', 'คีบอร์ด', 'คีบอด', 'คีย์', 'คี', 'บอร์ด'],
    'เมาส์': ['mouse', 'เมาส์', 'เม้าส์', 'เมาท์', 'เมาส', 'เม้าส'],
    'จอมอนิเตอร์': ['monitor', 'display', 'จอ', 'จอมอนิเตอร์', 'มอนิเตอร์', 'จอคอม', 'หน้าจอ'],
    'การ์ดจอ': ['vga', 'graphics', 'การ์ดจอ', 'การ์จอ', 'กราฟฟิค', 'การ์ดกราฟิก', 'วีจีเอ', 'กราฟิก', 'การ์ด', 'จอ'],
    'ซีพียู': ['cpu', 'processor', 'ซีพียู', 'โปรเซสเซอร์', 'ตัวประมวลผล', 'ซีพี', 'cpu', 'โปรเซส'],
    'หูฟัง': ['headphone', 'headset', 'หูฟัง', 'เฮดโฟน', 'เฮดเซต', 'หู', 'ฟัง'],
    'เมนบอร์ด': ['mainboard', 'motherboard', 'เมนบอร์ด', 'แม่บอร์ด', 'เมน', 'บอร์ด'],
    'แรม': ['ram', 'memory', 'แรม', 'หน่วยความจำ', 'ความจำ', 'แรมม์', 'แรมมี่', 'ram', 'memory'],
    'เคส': ['case', 'casing', 'เคส', 'กล่องเครื่อง', 'case', 'เคสคอม'],
    'พาวเวอร์': ['power', 'psu', 'พาวเวอร์', 'แหล่งจ่ายไฟ', 'พาว', 'เวอร์', 'จ่ายไฟ'],
    'ฮาร์ดดิสก์': ['hdd', 'harddisk', 'storage', 'ฮาร์ดดิสก์', 'หน่วยเก็บข้อมูล', 'ฮาร์ด', 'ดิสก์'],
    'เอสเอสดี': ['ssd', 'solid state', 'เอสเอสดี', 'ssd', 'เอส']
  }
  
  for (const [, keywords] of Object.entries(categoryMap)) {
    if (keywords.some(keyword => 
      categoryInput.toLowerCase().includes(keyword.toLowerCase())
    )) {
      return keywords
    }
  }
  
  return [categoryInput]
}

// Usage keyword mapping
export function getUsageKeywords(usage: string): string[] {
  const usageMap: Record<string, string[]> = {
    'เล่นเกม': ['gaming', 'game', 'เกม', 'เล่นเกม', 'เกมมิ่ง'],
    'ทำงาน': ['office', 'work', 'business', 'ทำงาน', 'ออฟฟิศ'],
    'เรียน': ['student', 'education', 'study', 'เรียน', 'การศึกษา'],
    'กราฟิก': ['graphic', 'design', 'creative', 'กราฟิก', 'ออกแบบ'],
    'โปรแกรม': ['programming', 'coding', 'developer', 'โปรแกรม', 'เขียนโค้ด'],
    'วิดีโอ': ['video', 'editing', 'rendering', 'วิดีโอ', 'ตัดต่อ']
  }
  
  for (const [, keywords] of Object.entries(usageMap)) {
    if (keywords.some(keyword => 
      usage.toLowerCase().includes(keyword.toLowerCase())
    )) {
      return keywords
    }
  }
  
  return [usage]
}

// Enhanced search terms with variations
export function enhanceSearchTerms(originalTerms: string[]): string[] {
  const enhanced = [...originalTerms]
  
  originalTerms.forEach(term => {
    if (term.includes('โน้ต')) {
      enhanced.push('laptop', 'notebook')
    }
    if (term.includes('การ์ด')) {
      enhanced.push('card', 'vga', 'graphics')
    }
    if (term.includes('คีย์')) {
      enhanced.push('keyboard', 'key')
    }
    if (term.includes('เมาส์')) {
      enhanced.push('mouse')
    }
    
    const numberMatch = term.match(/(\d+)(GB?)/i)
    if (numberMatch) {
      const [, num] = numberMatch
      enhanced.push(`${num}GB`, `${num} GB`, `${num}G`)
    }
  })
  
  return [...new Set(enhanced)]
}

// === QUERY LLM === 
// LLM ตัวที่ 1: เฉพาะทางในการสร้าง MongoDB Query ที่แม่นยำ
export async function generateOptimalMongoQuery(userInput: string): Promise<{
  query: Record<string, any>,
  entities: ExtractedEntities,
  reasoning: string
}> {
  const normalizedInput = normalizeText(userInput)
  const categoryMapper = CategoryMapper.getInstance()
  const allCategories = categoryMapper.getAllCategories()
  
  const prompt = `
คุณคือ MongoDB Query Expert AI ที่เชี่ยวชาญในการสร้าง Query ให้ตรงกับความต้องการของผู้ใช้มากที่สุด

INPUT: "${normalizedInput}"

ฐานข้อมูล MongoDB Schema:
- Collection: product_details
- Fields: title, description, keyword[], price, salePrice, stockQuantity, navigation.{categoryId, categoryMessage1, categoryMessage2, categoryMessage3}, productActive, rating, totalReviews, productView, images

หมวดหมู่หลัก (categoryMessage1):
${allCategories.categoryMessage1.slice(0, 15).join(', ')}

หมวดหมู่ย่อย (categoryMessage2):
${allCategories.categoryMessage2.slice(0, 20).join(', ')}

**หลักการสำคัญ:**
1. **จัดการคำกำกวม**: เช่น "โน้ตบุ๊ค", "การ์ดจอมีอะไรบ้าง", "คอมมีอะไรบ้าง" - ต้องเข้าใจและสร้าง query ที่เหมาะสม
2. **Budget Parsing**: "งบ 15000", "เกิน 15000 แต่ไม่ถึง 20000", "ไม่เกิน 30000"
3. **Stock Filter**: ต้องกรอง stockQuantity > 0 เสมอ
4. **Flexible Matching**: ใช้ regex และ array matching สำหรับ keyword
5. **Predictive Intent**: ถ้า input ไม่ชัดเจน ให้คาดเดาความต้องการ

**ตัวอย่าง Input ที่ยาก:**
- "โน้ตบุ๊คงบ 15000" → budget: {max: 15000}, category: NOTEBOOKS
- "การ์ดจอเกิน 15000 แต่ไม่ถึง 20000" → budget: {min: 15001, max: 19999}, category: COMPUTER HARDWARE (DIY)
- "คอมมีอะไรบ้าง" → หมวดหมู่คอมพิวเตอร์ทั้งหมด (NOTEBOOKS, COMPUTER HARDWARE, etc.)
- "การ์ดจอมีอะไรบ้าง" → category: COMPUTER HARDWARE (DIY), subCategory: Graphics Cards
- "โน้ตบุ๊ค" → category: NOTEBOOKS, คาดเดาเป็น Student/Office usage

ให้ตอบในรูปแบบ JSON:
{
  "mongoQuery": {
    "productActive": true,
    "stockQuantity": {"$gt": 0}
    // ... MongoDB query conditions
  },
  "entities": {
    "category": "หมวดหมู่หลัก",
    "subCategory": "หมวดหมู่ย่อย",
    "usage": "Gaming|Office|Student|Creative|Programming",
    "budget": {"min": number, "max": number},
    "brand": "แบรนด์",
    "specs": ["รายการสเปค"],
    "keywords": ["คำสำคัญ"],
    "features": ["คุณสมบัติ"],
    "intent": "ประเภทความต้องการ: specific_product|category_browse|price_range|comparison"
  },
  "reasoning": "อธิบายเหตุผลการสร้าง query นี้",
  "confidence": 0.8,
  "suggestions": ["คำถามเพิ่มเติมหากความมั่นใจต่ำ"]
}

**การจัดการ Edge Cases:**
- Input เป็นแค่ "แรม" → เสนอ default budget range และ usage
- "เกิน X แต่ไม่ถึง Y" → ใช้ $gte: X+1, $lte: Y-1
- "คอมมีอะไรบ้าง" → query หลายหมวดหมู่ที่เกี่ยวข้องกับคอมพิวเตอร์

สร้าง MongoDB Query ที่:
1. ตรงกับ user intent มากที่สุด
2. กรอง stock > 0 เสมอ
3. จัดการ budget range ได้ถูกต้อง
4. รองรับคำค้นหาที่กำกวม
5. มี fallback mechanism

ตอบเฉพาะ JSON เท่านั้น
`

  try {
    const { text } = await generateText({
      model: openai("gpt-4o-mini"),
      prompt,
      temperature: 0.1,
    })
    
    let cleanedText = text.trim()
    if (cleanedText.startsWith('```json')) {
      cleanedText = cleanedText.replace(/^```json\s*/, '').replace(/\s*```$/, '')
    } else if (cleanedText.startsWith('```')) {
      cleanedText = cleanedText.replace(/^```\s*/, '').replace(/\s*```$/, '')
    }
    
    const result = JSON.parse(cleanedText.trim())
    
    return {
      query: result.mongoQuery,
      entities: result.entities,
      reasoning: result.reasoning || 'Query generated from user input'
    }
  } catch (error) {
    console.error("Query generation error:", error)
    return generateFallbackQuery(normalizedInput)
  }
}

// Fallback query generation
function generateFallbackQuery(input: string): {
  query: Record<string, any>,
  entities: ExtractedEntities,
  reasoning: string
} {
  const entities = extractEntitiesFallback(input)
  const query = buildQuery(entities)
  
  return {
    query,
    entities,
    reasoning: 'Fallback query generated due to parsing error'
  }
}

// === RESPONSE LLM ===
// LLM ตัวที่ 2: เฉพาะทางในการสร้างคำแนะนำสินค้าที่เป็นธรรมชาติ
export async function generateNaturalProductRecommendation(
  userInput: string,
  entities: ExtractedEntities,
  queryResult: Product[],
  searchReasoning: string
): Promise<string> {
  if (queryResult.length === 0) {
    return await generateNoResultsResponse(userInput, entities)
  }

  const topProducts = queryResult.slice(0, 3)
  const totalResults = queryResult.length
  
  const prompt = `
คุณคือ AI Sales Assistant ที่เชี่ยวชาญในการแนะนำสินค้าไอทีให้ลูกค้า

User Input: "${userInput}"
Search Reasoning: ${searchReasoning}
Total Results: ${totalResults}

Top Products Found:
${topProducts.map((p, i) => `
${i + 1}. ${p.title}
   - ราคา: ฿${p.salePrice.toLocaleString()} (ราคาเต็ม: ฿${p.price.toLocaleString()})
   - คะแนน: ${p.rating}/5 (${p.totalReviews} รีวิว)
   - ยอดนิยม: ${p.productView.toLocaleString()} ครั้งเข้าชม
   - สต็อก: ${p.stockQuantity} ชิ้น
   - หมวด: ${p.navigation?.categoryMessage1} > ${p.navigation?.categoryMessage2}`).join('')}

User Entities:
- หมวดหมู่: ${entities.category || 'ไม่ระบุ'}
- การใช้งาน: ${entities.usage || 'ไม่ระบุ'}
- งบประมาณ: ${entities.budget ? `฿${entities.budget.min || 0}-${entities.budget.max || '∞'}` : 'ไม่ระบุ'}
- แบรนด์: ${entities.brand || 'ไม่ระบุ'}
- สเปค: ${entities.specs?.join(', ') || 'ไม่ระบุ'}
- คุณสมบัติ: ${entities.features?.join(', ') || 'ไม่ระบุ'}

**Instructions:**
1. สร้างการแนะนำที่เป็นธรรมชาติ เหมือนพนักงานขายมืออาชีพ
2. อธิบายว่าทำไมแนะนำสินค้านี้ (highlight key selling points)
3. เปรียบเทียบตัวเลือกหากมีหลายตัว
4. ระบุข้อดี: ราคา, คะแนน, ความนิยม, ส่วนลด, สต็อก
5. แนะนำเพิ่มเติมหากเป็นคำถามกำกวม
6. ใช้ emoji เพื่อให้น่าสนใจ
7. ไม่ต้องแสดง JSON หรือข้อมูลดิบ

**Response Format:**
- เริ่มด้วยการสรุปผลการค้นหา
- แนะนำสินค้าอันดับ 1 พร้อมเหตุผล
- กล่าวถึงตัวเลือกอื่นๆ หากมี
- ปิดท้ายด้วยคำแนะนำเพิ่มเติม

สร้างการแนะนำที่เป็นธรรมชาติ เป็นกันเอง และมีประโยชน์!
`

  try {
    const { text } = await generateText({
      model: openai("gpt-4o-mini"),
      prompt,
      temperature: 0.7,
    })
    
    return text.trim()
  } catch (error) {
    console.error("Response generation error:", error)
    return generateFallbackResponse(userInput, queryResult)
  }
}

// Generate response when no results found
async function generateNoResultsResponse(userInput: string, entities: ExtractedEntities): Promise<string> {
  const prompt = `
คุณคือ AI Assistant ที่ช่วยลูกค้าเมื่อไม่พบสินค้าที่ต้องการ

User Input: "${userInput}"
Entities: ${JSON.stringify(entities, null, 2)}

สร้างข้อความที่:
1. แสดงความเสียใจที่ไม่พบสินค้า
2. วิเคราะห์สาเหตุที่เป็นไปได้
3. เสนอทางเลือก: ขยายงบ, เปลี่ยนแบรนด์, เปลี่ยนสเปค
4. เสนอหมวดหมู่ที่เกี่ยวข้อง
5. ให้คำแนะนำในการค้นหาใหม่

ใช้ emoji และโทนเป็นกันเอง ช่วยเหลือ
`

  try {
    const { text } = await generateText({
      model: openai("gpt-4o-mini"),
      prompt,
      temperature: 0.6,
    })
    return text.trim()
  } catch (error) {
    console.error("No results response error:", error)
    return generateBasicNoResultsMessage(userInput, entities)
  }
}

// Fallback response generation
function generateFallbackResponse(userInput: string, products: Product[]): string {
  const topProduct = products[0]
  const totalResults = products.length
  
  let response = `พบสินค้าที่ตรงกับความต้องการ ${totalResults} รายการ 🛍️\n\n`
  response += `⭐ แนะนำ: ${topProduct.title}\n`
  response += `💰 ราคา: ฿${topProduct.salePrice.toLocaleString()}`
  
  const discount = topProduct.price - topProduct.salePrice
  if (discount > 0) {
    const discountPercent = Math.round((discount / topProduct.price) * 100)
    response += ` (ลด ${discountPercent}% จาก ฿${topProduct.price.toLocaleString()})`
  }
  
  response += `\n📦 คงเหลือ: ${topProduct.stockQuantity} ชิ้น`
  response += `\n⭐ คะแนน: ${topProduct.rating}/5 (${topProduct.totalReviews} รีวิว)`
  
  if (totalResults > 1) {
    response += `\n\n📋 ดูสินค้าทั้งหมด ${totalResults} รายการเพื่อเลือกที่ใช่สำหรับคุณ!`
  }
  
  return response
}

function generateBasicNoResultsMessage(userInput: string, entities: ExtractedEntities): string {
  let response = "ขออภัย ไม่พบสินค้าที่ตรงกับความต้องการของคุณ 🔍\n\n"
  
  if (entities.category) response += `หมวด: ${entities.category}\n`
  if (entities.budget?.max) response += `งบประมาณ: ฿${entities.budget.max.toLocaleString()}\n`
  if (entities.usage) response += `การใช้งาน: ${entities.usage}\n`
  
  response += "\n💡 ข้อเสนอแนะ:\n"
  response += "• ลองเพิ่มงบประมาณ\n"
  response += "• ค้นหาด้วยคำอื่น\n"
  response += "• ระบุความต้องการให้ชัดเจนมากขึ้น"
  
  return response
}

// === LEGACY FUNCTIONS (for backward compatibility) ===
export async function extractEntitiesWithLLM(userInput: string): Promise<ExtractedEntities> {
  const result = await generateOptimalMongoQuery(userInput)
  return result.entities
}

// Fallback entity extraction without LLM
function extractEntitiesFallback(input: string): ExtractedEntities {
  const entities: ExtractedEntities = {
    keywords: []
  }
  
  const categoryMap = {
    'แรม': { cat: 'COMPUTER HARDWARE (DIY)', sub: 'Memory', usage: 'Office' },
    'การ์ดจอ': { cat: 'COMPUTER HARDWARE (DIY)', sub: 'Graphics Cards', usage: 'Gaming' },
    'โน้ตบุ๊ก': { cat: 'NOTEBOOKS', sub: 'Notebooks', usage: 'Student' },
    'คีย์บอร์ด': { cat: 'KEYBOARD / MOUSE / PEN TABLET', sub: 'Keyboard', usage: 'Office' },
    'เมาส์': { cat: 'KEYBOARD / MOUSE / PEN TABLET', sub: 'Mouse', usage: 'Office' },
    'ซีพียู': { cat: 'COMPUTER HARDWARE (DIY)', sub: 'Processors', usage: 'Office' },
    'หูฟัง': { cat: 'HEADPHONES', sub: 'Headphones', usage: 'Gaming' }
  }
  
  for (const [keyword, config] of Object.entries(categoryMap)) {
    if (input.includes(keyword)) {
      entities.category = config.cat
      entities.subCategory = config.sub
      entities.usage = config.usage
      entities.keywords?.push(keyword)
      
      if (keyword === 'แรม') {
        entities.suggestions = [
          'ต้องการแรมขนาดเท่าไหร่ (8GB, 16GB, 32GB)?',
          'ใช้กับคอมเดสก์ทอปหรือโน้ตบุ๊ก?',
          'งบประมาณเท่าไหร่?'
        ]
        entities.budget = { min: 1000, max: 10000 }
      } else if (keyword === 'การ์ดจอ') {
        entities.suggestions = [
          'ใช้เล่นเกมหรือทำงาน?',
          'งบประมาณเท่าไหร่?',
          'ต้องการรุ่นไหน (GTX, RTX)?'
        ]
        entities.budget = { min: 5000, max: 50000 }
      } else if (keyword === 'โน้ตบุ๊ก') {
        entities.suggestions = [
          'ใช้ทำงานหรือเรียน?',
          'งบประมาณเท่าไหร่?',
          'ต้องการหน้าจอขนาดเท่าไหร่?'
        ]
        entities.budget = { min: 15000, max: 40000 }
      }
      break
    }
  }
  
  const budgetMatch = input.match(/(\d+(?:,\d+)*)/g)
  if (budgetMatch) {
    const budget = parseInt(budgetMatch[0].replace(/,/g, ''))
    if (budget > 1000) {
      entities.budget = { max: budget }
    }
  }
  
  entities.keywords?.push(input)
  
  return entities
}

// Build MongoDB query from extracted entities
export function buildQuery(entities: ExtractedEntities): Record<string, any> {
  let query: Record<string, any> = { 
    productActive: true, 
    stockQuantity: { $gt: 0 } 
  }
  
  if (entities.budget?.max) {
    query.salePrice = { $lte: entities.budget.max }
    if (entities.budget.min) {
      query.salePrice.$gte = entities.budget.min
    }
  }
  
  if (entities.category) {
    query['navigation.categoryMessage1'] = { $regex: entities.category, $options: 'i' }
  }
  
  if (entities.subCategory) {
    query['navigation.categoryMessage2'] = { $regex: entities.subCategory, $options: 'i' }
  }
  
  const additionalConditions: any[] = []
  const searchTerms: string[] = []
  
  if (entities.keywords) searchTerms.push(...entities.keywords)
  if (entities.specs) searchTerms.push(...entities.specs)
  if (entities.features) searchTerms.push(...entities.features)
  if (entities.usage) searchTerms.push(entities.usage)
  
  if (searchTerms.length > 0) {
    const enhancedTerms = enhanceSearchTerms(searchTerms)
    const uniqueTerms = [...new Set(enhancedTerms)].filter(term => term && term.length > 0)
    
    additionalConditions.push(
      { title: { $regex: uniqueTerms.join('|'), $options: 'i' }},
      { description: { $regex: uniqueTerms.join('|'), $options: 'i' }},
      { keyword: { $in: uniqueTerms.map(term => term.toUpperCase()) }},
      { 'navigation.categoryMessage3': { $regex: uniqueTerms.join('|'), $options: 'i' }}
    )
  }
  
  if (additionalConditions.length > 0) {
    query.$and = query.$and || []
    query.$and.push({ $or: additionalConditions })
  }
  
  if (entities.brand) {
    query.$and = query.$and || []
    query.$and.push({
      $or: [
        { keyword: { $in: [entities.brand.toUpperCase()] }},
        { title: { $regex: entities.brand, $options: 'i' }},
        { 'navigation.categoryMessage3': { $regex: entities.brand, $options: 'i' }}
      ]
    })
  }
  
  return query
}

// Generate MongoDB query with reasoning
export async function generateMongoQuery(userInput: string): Promise<MongoQueryWithReason> {
  try {
    const entities = await extractEntitiesWithLLM(userInput)
    const filter = buildQuery(entities)
    
    let reason = "ค้นหาตาม"
    const reasons: string[] = []
    
    if (entities.category) {
      let categoryText = entities.category
      if (entities.subCategory) {
        categoryText += ` > ${entities.subCategory}`
      }
      reasons.push(`หมวดหมู่ ${categoryText}`)
    }
    if (entities.usage) reasons.push(`การใช้งาน ${entities.usage}`)
    if (entities.budget?.max) reasons.push(`งบประมาณไม่เกิน ${entities.budget.max.toLocaleString()} บาท`)
    if (entities.brand) reasons.push(`แบรนด์ ${entities.brand}`)
    if (entities.specs?.length) reasons.push(`สเปค ${entities.specs.join(', ')}`)
    if (entities.features?.length) reasons.push(`คุณสมบัติ ${entities.features.join(', ')}`)
    
    reason += reasons.length > 0 ? ` ${reasons.join(', ')}` : 'คำค้นหาที่ระบุ'
    
    return {
      filter,
      sort: { productView: -1, rating: -1 },
      limit: 10,
      reason
    }
  } catch (error) {
    console.error("Query generation error:", error)
    
    return {
      filter: {
        productActive: true,
        stockQuantity: { $gt: 0 },
        $or: [
          { title: { $regex: userInput, $options: "i" } },
          { description: { $regex: userInput, $options: "i" } },
        ],
      },
      limit: 5,
      reason: "ค้นหาจากข้อความที่ระบุ (fallback)",
    }
  }
}

// Enhanced product response formatting
export async function formatProductResponse(
  _userInput: string,
  products: Product[],
  reason?: string
): Promise<string> {
  if (products.length === 0) {
    return "ขออภัย ไม่พบสินค้าที่ตรงกับความต้องการของคุณ ลองค้นหาด้วยคำอื่นหรือปรับเงื่อนไขดูนะคะ 🔍"
  }

  const topProduct = products[0]
  const totalProducts = products.length
  
  const discount = topProduct.price - topProduct.salePrice
  const hasDiscount = discount > 0
  const discountPercent = hasDiscount ? Math.round((discount / topProduct.price) * 100) : 0

  let response = `พบสินค้าที่ตรงกับความต้องการ ${totalProducts} รายการ 🛍️\n\n`
  
  if (reason) {
    response += `${reason}\n\n`
  }
  
  response += `⭐ **แนะนำ: ${topProduct.title}**\n`
  response += `💰 ราคา: ฿${topProduct.salePrice.toLocaleString()}`
  
  if (hasDiscount) {
    response += ` (ลด ${discountPercent}% จาก ฿${topProduct.price.toLocaleString()})`
  }
  
  response += `\n📦 คงเหลือ: ${topProduct.stockQuantity} ชิ้น`
  response += `\n⭐ คะแนน: ${topProduct.rating}/5 (${topProduct.totalReviews} รีวิว)`
  response += `\n👀 ยอดนิยม: ${topProduct.productView.toLocaleString()} ครั้งเข้าชม`
  
  const recommendationReasons: string[] = []
  
  if (topProduct.rating > 4) {
    recommendationReasons.push(`ได้รีวิวดี (${topProduct.rating}/5)`)
  }
  
  if (topProduct.productView > 1000) {
    recommendationReasons.push(`เป็นที่นิยม`)
  }
  
  if (hasDiscount) {
    recommendationReasons.push(`มีส่วนลด ${discountPercent}%`)
  }
  
  if (topProduct.stockQuantity > 10) {
    recommendationReasons.push(`มีสต็อกเพียงพอ`)
  }
  
  if (recommendationReasons.length > 0) {
    response += `\n\n💡 **ทำไมถึงแนะนำ:** ${recommendationReasons.join(', ')}`
  }
  
  if (totalProducts > 1) {
    response += `\n\n📋 ดูสินค้าทั้งหมด ${totalProducts} รายการด้านล่าง และเลือกที่ใช่สำหรับคุณ!`
  }

  return response
}