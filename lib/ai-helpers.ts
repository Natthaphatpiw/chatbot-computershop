import { openai } from "@ai-sdk/openai"
import { generateText } from "ai"
import type { MongoQuery, Product } from "@/types"

export async function generateMongoQuery(userInput: string): Promise<MongoQuery> {
  const prompt = `
You are a MongoDB query generator for a product database. Convert the user's natural language request into a MongoDB query.

The products collection has these fields:
- name (string): product name
- description (string): product description  
- price (number): price in THB (Thai Baht)
- category (string): product category (เสื้อผ้า, เครื่องประดับ, กระเป๋า, รองเท้า, ฯลฯ)
- image_url (string): product image URL
- tags (array): keywords
- rating (number): 1-5
- reviews (number): number of reviews

User request: "${userInput}" (may be in Thai language)

Return ONLY a valid JSON object with this structure:
{
  "filter": { /* MongoDB filter object */ },
  "sort": { /* optional sort object */ },
  "limit": /* optional number, max 10 */
}

Examples:
- "cheap laptops" → {"filter": {"category": "electronics", "name": {"$regex": "laptop", "$options": "i"}, "price": {"$lt": 1000}}, "sort": {"price": 1}, "limit": 5}
- "best rated books" → {"filter": {"category": "books"}, "sort": {"rating": -1}, "limit": 5}
- "red shirts under $50" → {"filter": {"category": "clothing", "description": {"$regex": "red", "$options": "i"}, "price": {"$lt": 50}}, "limit": 5}
`

  const { text } = await generateText({
    model: openai("gpt-4.1"),
    prompt,
    temperature: 0.1,
  })

  try {
    return JSON.parse(text.trim())
  } catch (error) {
    // Fallback query if parsing fails
    return {
      filter: {
        $or: [
          { name: { $regex: userInput, $options: "i" } },
          { description: { $regex: userInput, $options: "i" } },
        ],
      },
      limit: 5,
    }
    console.log(text)
  }
}

export async function formatProductResponse(userInput: string, products: Product[]): Promise<string> {
  if (products.length === 0) {
    return "I couldn't find any products matching your request. Try searching for something else!"
  }

  const prompt = `
You are a helpful shopping assistant. The user asked: "${userInput}"

Here are the products I found:
${products.map((p) => `- ${p.name}: ${p.description} - $${p.price} (${p.inStock ? "In Stock" : "Out of Stock"})`).join("\n")}

Write a friendly, helpful response (2-3 sentences) that:
1. Acknowledges their request
2. Briefly highlights the best matches
3. Encourages them to check out the products

Keep it conversational and enthusiastic!
`

  const { text } = await generateText({
    model: openai("gpt-4.1"),
    prompt,
    temperature: 0.7,
  })

  return text
}
