import { openai } from "@ai-sdk/openai"
import { generateText } from "ai"
import type { Product, ExtractedEntities, MongoQueryWithReason } from "@/types"
import { CategoryMapper } from "./category-mapper"

// Text normalization function
export function normalizeText(text: string): string {
  return text
    .replace(/โน้?[ดต๊]บุ๊?[คก]/g, 'โน้ตบุ๊ก')
    .replace(/การ์[จด]อ/g, 'การ์ดจอ')
    .replace(/คอมพิ?วเ?ตอร์/g, 'คอมพิวเตอร์')
    .replace(/(\d+)k/gi, (_, p1) => (parseInt(p1) * 1000).toString())
    .replace(/เม้าส์/g, 'เมาส์')
    .replace(/คีบอร์ด/g, 'คีย์บอร์ด')
    .replace(/คีบอด/g, 'คีย์บอร์ด')
}

// Category keyword mapping
export function getCategoryKeywords(categoryInput: string): string[] {
  const categoryMap: Record<string, string[]> = {
    'โน้ตบุ๊ก': ['notebook', 'laptop', 'โน้ตบุ๊ก', 'โน้ตบุ้ค', 'โน๊ตบุ๊ค', 'โน้ดบุ๊ค'],
    'คีย์บอร์ด': ['keyboard', 'คีย์บอร์ด', 'คีบอร์ด', 'คีบอด'],
    'เมาส์': ['mouse', 'เมาส์', 'เม้าส์', 'เมาท์'],
    'จอมอนิเตอร์': ['monitor', 'display', 'จอ', 'จอมอนิเตอร์', 'มอนิเตอร์'],
    'การ์ดจอ': ['vga', 'graphics', 'การ์ดจอ', 'การ์จอ', 'กราฟฟิค', 'การ์ดกราฟิก'],
    'ซีพียู': ['cpu', 'processor', 'ซีพียู', 'โปรเซสเซอร์', 'ตัวประมวลผล'],
    'หูฟัง': ['headphone', 'headset', 'หูฟัง', 'เฮดโฟน', 'เฮดเซต'],
    'เมนบอร์ด': ['mainboard', 'motherboard', 'เมนบอร์ด', 'แม่บอร์ด'],
    'แรม': ['ram', 'memory', 'แรม', 'หน่วยความจำ'],
    'เคส': ['case', 'casing', 'เคส', 'กล่องเครื่อง'],
    'พาวเวอร์': ['power', 'psu', 'พาวเวอร์', 'แหล่งจ่ายไฟ'],
    'ฮาร์ดดิสก์': ['hdd', 'harddisk', 'storage', 'ฮาร์ดดิสก์', 'หน่วยเก็บข้อมูล'],
    'เอสเอสดี': ['ssd', 'solid state', 'เอสเอสดี']
  }
  
  for (const [, keywords] of Object.entries(categoryMap)) {
    if (keywords.some(keyword => 
      categoryInput.toLowerCase().includes(keyword.toLowerCase())
    )) {
      return keywords
    }
  }
  
  // If no exact match, return the input itself for flexible search
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
    // Add variations for common Thai tech terms
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
    
    // Add number variations (16GB, 16 GB, 16G)
    const numberMatch = term.match(/(\d+)(GB?)/i)
    if (numberMatch) {
      const [, num] = numberMatch
      enhanced.push(`${num}GB`, `${num} GB`, `${num}G`)
    }
  })
  
  return [...new Set(enhanced)] // Remove duplicates
}

// LLM-based entity extraction
export async function extractEntitiesWithLLM(userInput: string): Promise<ExtractedEntities> {
  const normalizedInput = normalizeText(userInput)
  const categoryMapper = CategoryMapper.getInstance()
  const allCategories = categoryMapper.getAllCategories()
  
  // Pre-analyze input to get relevant categories
  const relevantCategories = categoryMapper.getCategoryTerms(normalizedInput)
  const relevantBrands = categoryMapper.getBrandTerms(normalizedInput)
  const relevantUsage = categoryMapper.getUsageTerms(normalizedInput)
  
  const prompt = `
คุณคือ AI ผู้เชี่ยวชาญในการวิเคราะห์ความต้องการสินค้าไอทีจากภาษาไทย
วิเคราะห์ข้อความต่อไปนี้และดึงข้อมูลสำคัญออกมา:

INPUT: "${normalizedInput}"

ฐานข้อมูลมีหมวดหมู่หลักดังนี้:
${allCategories.categoryMessage1.slice(0, 15).join(', ')}

หมวดหมู่ย่อยที่เกี่ยวข้อง:
${allCategories.categoryMessage2.slice(0, 20).join(', ')}

ให้ตอบในรูปแบบ JSON เท่านั้น:
{
  "category": "หมวดหมู่หลัก (เลือกจาก categoryMessage1 ข้างต้น หรือ null)",
  "subCategory": "หมวดหมู่ย่อย (เลือกจาก categoryMessage2 หรือ null)",
  "usage": "การใช้งาน (Gaming, Office, Student, Creative, Programming หรือ null)",
  "budget": {"min": ตัวเลข, "max": ตัวเลข} หรือ null,
  "brand": "แบรนด์ (ASUS, MSI, Intel, AMD, Logitech, Razer, etc. หรือ null)",
  "specs": ["รายการสเปคที่ระบุ เช่น 16GB, RTX 4060, i7"] หรือ null,
  "keywords": ["คำสำคัญทั้งหมดที่เกี่ยวข้อง"],
  "features": ["คุณสมบัติพิเศษ เช่น RGB, Wireless, Mechanical"] หรือ null
}

หลักการวิเคราะห์:
1. ใช้ชื่อหมวดหมู่ภาษาอังกฤษตามฐานข้อมูลจริง
2. งบประมาณ: ค้นหาตัวเลข แล้วแปลงเป็น min/max
3. แบรนด์: ใช้ชื่อแบรนด์มาตรฐาน (ตัวพิมพ์ใหญ่)
4. สเปค: เก็บตัวเลขและรุ่นที่ระบุชัดเจน
5. การใช้งาน: แปลงเป็นภาษาอังกฤษ

ตัวอย่างที่ถูกต้อง:
"โน้ตบุ๊คทำงานงบ 20000" → {"category": "NOTEBOOKS", "subCategory": "Notebooks", "usage": "Office", "budget": {"max": 20000}, "keywords": ["โน้ตบุ๊ค", "ทำงาน"]}

"เมาส์เกมมิ่งไร้สาย RGB" → {"category": "KEYBOARD / MOUSE / PEN TABLET", "subCategory": "Gaming Mouse", "usage": "Gaming", "features": ["Wireless", "RGB"], "keywords": ["เมาส์", "เกมมิ่ง"]}

"การ์ดจอ RTX 4060 งบ 15000" → {"category": "COMPUTER HARDWARE (DIY)", "subCategory": "Graphics Cards", "specs": ["RTX 4060"], "budget": {"max": 15000}, "keywords": ["การ์ดจอ"]}

"คีย์บอร์ด mechanical RGB" → {"category": "KEYBOARD / MOUSE / PEN TABLET", "subCategory": "Mechanical & Gaming Keyboard", "features": ["Mechanical", "RGB"], "keywords": ["คีย์บอร์ด"]}

"จอมอนิเตอร์ 24 นิ้ว" → {"category": "MONITOR ", "subCategory": "Monitor", "specs": ["24"], "keywords": ["จอมอนิเตอร์"]}

หลักการเลือก category:
- โน้ตบุ๊ก/laptop → "NOTEBOOKS"
- เมาส์/mouse → "KEYBOARD / MOUSE / PEN TABLET"  
- คีย์บอร์ด/keyboard → "KEYBOARD / MOUSE / PEN TABLET"
- จอ/monitor → "MONITOR "
- การ์ดจอ/vga → "COMPUTER HARDWARE (DIY)"
- ซีพียู/cpu → "COMPUTER HARDWARE (DIY)"

ห้าม: สร้างชื่อหมวดหมู่ใหม่ที่ไม่มีในฐานข้อมูล
ตอบเฉพาะ JSON เท่านั้น ห้ามใส่ข้อความอื่น
`

  try {
    const { text } = await generateText({
      model: openai("gpt-4o-mini"),
      prompt,
      temperature: 0.1,
    })
    
    // Clean the response to extract just the JSON part
    let cleanedText = text.trim()
    
    // Remove markdown code blocks if present
    if (cleanedText.startsWith('```json')) {
      cleanedText = cleanedText.replace(/^```json\s*/, '').replace(/\s*```$/, '')
    } else if (cleanedText.startsWith('```')) {
      cleanedText = cleanedText.replace(/^```\s*/, '').replace(/\s*```$/, '')
    }
    
    return JSON.parse(cleanedText.trim())
  } catch (error) {
    console.error("Entity extraction error:", error)
    // Fallback entity extraction
    return extractEntitiesFallback(normalizedInput)
  }
}

// Fallback entity extraction without LLM
function extractEntitiesFallback(input: string): ExtractedEntities {
  const entities: ExtractedEntities = {
    keywords: []
  }
  
  // Simple category detection
  const categories = ['โน้ตบุ๊ก', 'คีย์บอร์ด', 'เมาส์', 'การ์ดจอ', 'ซีพียู', 'หูฟัง']
  for (const category of categories) {
    if (input.includes(category)) {
      entities.category = category
      entities.keywords?.push(category)
      break
    }
  }
  
  // Simple budget extraction
  const budgetMatch = input.match(/(\d+(?:,\d+)*)/g)
  if (budgetMatch) {
    const budget = parseInt(budgetMatch[0].replace(/,/g, ''))
    if (budget > 1000) {
      entities.budget = { max: budget }
    }
  }
  
  // Add input as keyword
  entities.keywords?.push(input)
  
  return entities
}

// Build MongoDB query from extracted entities
export function buildQuery(entities: ExtractedEntities): Record<string, any> {
  let query: Record<string, any> = { 
    productActive: true, 
    stockQuantity: { $gt: 0 } 
  }
  
  // Budget filtering
  if (entities.budget?.max) {
    query.salePrice = { $lte: entities.budget.max }
    if (entities.budget.min) {
      query.salePrice.$gte = entities.budget.min
    }
  }
  
  // PRIORITY 1: Category filtering (must match) - high priority
  if (entities.category) {
    query['navigation.categoryMessage1'] = { $regex: entities.category, $options: 'i' }
  }
  
  // PRIORITY 2: Sub-category filtering (if available)
  if (entities.subCategory) {
    query['navigation.categoryMessage2'] = { $regex: entities.subCategory, $options: 'i' }
  }
  
  // PRIORITY 3: Additional filtering with OR conditions for other criteria
  const additionalConditions: any[] = []
  
  // Collect all search terms for flexible matching
  const searchTerms: string[] = []
  
  // Add all relevant terms
  if (entities.keywords) searchTerms.push(...entities.keywords)
  if (entities.specs) searchTerms.push(...entities.specs)
  if (entities.features) searchTerms.push(...entities.features)
  if (entities.usage) searchTerms.push(entities.usage)
  
  // Enhanced search terms for secondary matching
  if (searchTerms.length > 0) {
    const enhancedTerms = enhanceSearchTerms(searchTerms)
    const uniqueTerms = [...new Set(enhancedTerms)].filter(term => term && term.length > 0)
    
    // Add text-based searches as additional conditions
    additionalConditions.push(
      { title: { $regex: uniqueTerms.join('|'), $options: 'i' }},
      { description: { $regex: uniqueTerms.join('|'), $options: 'i' }},
      { keyword: { $in: uniqueTerms.map(term => term.toUpperCase()) }},
      { 'navigation.categoryMessage3': { $regex: uniqueTerms.join('|'), $options: 'i' }}
    )
  }
  
  // Add additional conditions as AND with the main category filter
  if (additionalConditions.length > 0) {
    query.$and = query.$and || []
    query.$and.push({ $or: additionalConditions })
  }
  
  // Brand-specific filtering (high priority)
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
    
    // Generate reasoning
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
      sort: { productView: -1, rating: -1 }, // Sort by popularity and rating
      limit: 10,
      reason
    }
  } catch (error) {
    console.error("Query generation error:", error)
    
    // Fallback query
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
  
  // Calculate discount if applicable
  const discount = topProduct.price - topProduct.salePrice
  const hasDiscount = discount > 0
  const discountPercent = hasDiscount ? Math.round((discount / topProduct.price) * 100) : 0

  let response = `พบสินค้าที่ตรงกับความต้องการ ${totalProducts} รายการ 🛍️\n\n`
  
  if (reason) {
    response += `${reason}\n\n`
  }
  
  // Highlight top recommendation
  response += `⭐ **แนะนำ: ${topProduct.title}**\n`
  response += `💰 ราคา: ฿${topProduct.salePrice.toLocaleString()}`
  
  if (hasDiscount) {
    response += ` (ลด ${discountPercent}% จาก ฿${topProduct.price.toLocaleString()})`
  }
  
  response += `\n📦 คงเหลือ: ${topProduct.stockQuantity} ชิ้น`
  response += `\n⭐ คะแนน: ${topProduct.rating}/5 (${topProduct.totalReviews} รีวิว)`
  response += `\n👀 ยอดนิยม: ${topProduct.productView.toLocaleString()} ครั้งเข้าชม`
  
  // Add reasons for recommendation
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