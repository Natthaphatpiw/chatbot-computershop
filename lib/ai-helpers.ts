import { openai } from "@ai-sdk/openai"
import { generateText } from "ai"
import type { Product } from "@/types"

// เพิ่ม type สำหรับผลลัพธ์ query ที่มี reason
export interface MongoQueryWithReason {
  filter: Record<string, any>
  sort?: Record<string, 1 | -1>
  limit?: number
  reason?: string
}

export async function generateMongoQuery(userInput: string): Promise<MongoQueryWithReason> {
  const prompt = `
You are a MongoDB query generator for an IT equipment store database. Analyze the user's natural language request and convert it into a MongoDB query.

The computershop collection has these fields:
- name (string)
- description (string)
- price (number, in THB)
- category (string, "โน้ตบุ๊ค", "คอมพิวเตอร์ตั้งโต๊ะ", "อุปกรณ์เสริม", "จัดเก็บข้อมูล", "เกมมิ่งเกียร์")
- image_url (string)
- tags (array)
- rating (number, 1-5)
- reviews (number)
- stock (number)

User request: "${userInput}" (may be in Thai language)

Return ONLY a valid JSON object with this structure:
{
  "filter": { /* MongoDB filter object */ },
  "sort": { /* optional sort object */ },
  "limit": /* optional number, max 10 */,
  "reason": "short explanation in Thai why you choose this filter (e.g. เหมาะกับเล่นเกม, เน้นราคาประหยัด, ฯลฯ)"
}

Examples:
- "โน้ตบุ๊คราคาถูก" → {"filter": {"category": "โน้ตบุ๊ค", "price": {"$lt": 20000}}, "sort": {"price": 1}, "limit": 5, "reason": "คัดเฉพาะโน้ตบุ๊คที่ราคาต่ำกว่า 20,000 บาท"}
- "เกมมิ่งเกียร์สำหรับเกมเมอร์" → {"filter": {"category": "เกมมิ่งเกียร์"}, "sort": {"rating": -1}, "limit": 5, "reason": "เลือกอุปกรณ์ที่ถูกจัดอยู่ในกลุ่มเกมมิ่งเกียร์และจัดอันดับคะแนนสูงสุด"}
`
  const { text } = await generateText({
    model: openai("gpt-4.1"),
    prompt,
    temperature: 0.1,
  })

  try {
    return JSON.parse(text.trim())
  } catch (error) {
    return {
      filter: {
        $or: [
          { name: { $regex: userInput, $options: "i" } },
          { description: { $regex: userInput, $options: "i" } },
        ],
      },
      limit: 5,
      reason: "เลือกจากข้อความค้นหาที่ผู้ใช้กรอกตรง ๆ (fallback)",
    }
  }
}

export async function formatProductResponse(
  userInput: string,
  products: Product[],
  reason?: string
): Promise<string> {
  if (products.length === 0) {
    return "ขออภัย ฉันไม่พบสินค้าที่ตรงกับความต้องการของคุณ ลองค้นหาด้วยคำอื่นดูนะคะ"
  }

  const prompt = `
คุณคือแชทบอทผู้ช่วยร้านค้าอุปกรณ์คอมพิวเตอร์ IT ผู้ใช้ถาม: "${userInput}"

เหตุผลที่เลือกสินค้าเหล่านี้: ${reason || "-"}
รายการสินค้า:
${products.map((p) => `- ${p.name}: ${p.description} - ฿${p.price} (สต็อก ${p.stock})`).join("\n")}

ช่วยสรุปเป็นข้อความตอบผู้ใช้เป็นภาษาไทย (2-3 ประโยค) ที่อธิบายว่าทำไมสินค้านี้ถึงตรงกับความต้องการ (รวมเหตุผลประกอบ), ไฮไลต์จุดเด่นสินค้า, และเชิญชวนให้ผู้ใช้เลือกดูสินค้า (ใช้ emoji ได้บ้าง)
`

  const { text } = await generateText({
    model: openai("gpt-4.1"),
    prompt,
    temperature: 0.7,
  })

  return text
}
