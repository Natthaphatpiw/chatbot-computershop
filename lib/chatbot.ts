import type { MongoClient, Collection } from "mongodb"
import type { Product, ExtractedEntities, MongoQueryWithReason } from "@/types"
import { 
  generateOptimalMongoQuery,
  generateNaturalProductRecommendation,
  normalizeText,
  getCategoryKeywords,
  enhanceSearchTerms
} from "./ai-helpers"

export class ITStoreChatbot {
  private collection: Collection
  
  constructor(mongoClient: MongoClient) {
    const db = mongoClient.db("dashboard-ai-data")
    this.collection = db.collection("product_details")
  }
  
  async processUserInput(userInput: string) {
    try {
      // 1. Normalize text
      const normalizedInput = normalizeText(userInput)
      
      // 2. LLM 1: Generate optimal MongoDB query
      const queryResult = await generateOptimalMongoQuery(normalizedInput)
      
      // 3. Search products with progressive fallback
      const products = await this.searchWithFallback(queryResult.entities, queryResult.query)
      
      // 4. LLM 2: Generate natural product recommendations
      const response = await generateNaturalProductRecommendation(
        userInput,
        queryResult.entities,
        products,
        queryResult.reasoning
      )
      
      return {
        products,
        response,
        reasoning: this.explainSelection(queryResult.entities, products),
        entities: queryResult.entities,
        queryReasoning: queryResult.reasoning
      }
    } catch (error) {
      console.error("Chatbot error:", error)
      return {
        products: [],
        response: "ขออภัย เกิดข้อผิดพลาดในการค้นหาสินค้า กรุณาลองใหม่อีกครั้ง 🔧",
        reasoning: null,
        entities: null,
        queryReasoning: null
      }
    }
  }
  
  // Enhanced search with progressive fallback system and stock filtering
  private async searchWithFallback(entities: ExtractedEntities, primaryQuery: Record<string, any>): Promise<Product[]> {
    // Ensure stock filtering is always applied
    const baseQuery = {
      ...primaryQuery,
      productActive: true,
      stockQuantity: { $gt: 0 }
    }
    
    // Primary search with all criteria
    let products = await this.searchProducts(baseQuery)
    console.log(`Primary search found: ${products.length} products`)
    
    // If no results, try progressively broader searches
    if (products.length === 0 && entities.budget) {
      console.log("No results with budget constraint, removing budget filter...")
      const relaxedQuery = { ...baseQuery }
      delete relaxedQuery.salePrice
      products = await this.searchProducts(relaxedQuery)
      console.log(`Budget relaxed search found: ${products.length} products`)
    }
    
    // If still no results, search with just category keywords
    if (products.length === 0 && entities.category) {
      console.log("No results with complex query, trying category-only search...")
      const categoryKeywords = getCategoryKeywords(entities.category)
      const enhancedKeywords = enhanceSearchTerms(categoryKeywords)
      
      const keywordQuery = {
        productActive: true,
        stockQuantity: { $gt: 0 },
        $or: [
          { title: { $regex: enhancedKeywords.join("|"), $options: "i" }},
          { description: { $regex: enhancedKeywords.join("|"), $options: "i" }},
          { keyword: { $in: enhancedKeywords.map(term => term.toUpperCase()) }},
          { "navigation.categoryMessage1": { $regex: enhancedKeywords.join("|"), $options: "i" }},
          { "navigation.categoryMessage2": { $regex: enhancedKeywords.join("|"), $options: "i" }},
          { "navigation.categoryMessage3": { $regex: enhancedKeywords.join("|"), $options: "i" }}
        ]
      }
      products = await this.searchProducts(keywordQuery)
      console.log(`Category search found: ${products.length} products`)
    }
    
    // Final fallback: simple text search
    if (products.length === 0) {
      console.log("No results with category search, trying simple text search...")
      const searchTerm = entities.category || entities.keywords?.[0] || ""
      const fallbackQuery = {
        productActive: true,
        stockQuantity: { $gt: 0 },
        $or: [
          { title: { $regex: searchTerm, $options: "i" }},
          { description: { $regex: searchTerm, $options: "i" }}
        ]
      }
      products = await this.searchProducts(fallbackQuery)
      console.log(`Fallback search found: ${products.length} products`)
    }
    
    return products
  }
  
  async searchProducts(query: Record<string, any>, limit = 10): Promise<Product[]> {
    try {
      const results = await this.collection
        .find(query, {
          projection: {
            _id: 1,
            title: 1,
            description: 1,
            keyword: 1,
            price: 1,
            salePrice: 1,
            stockQuantity: 1,
            navigation: 1,
            productActive: 1,
            rating: 1,
            totalReviews: 1,
            productView: 1,
            images: 1,
          },
        })
        .sort({ productView: -1, rating: -1, totalReviews: -1 }) // Sort by popularity, rating, and social proof
        .limit(limit)
        .toArray()
      
      return results as unknown as Product[]
    } catch (error) {
      console.error("Database search error:", error)
      return []
    }
  }
  
  // Legacy method - now handled by Response LLM
  async generateResponse(entities: ExtractedEntities, products: Product[]): Promise<string> {
    // This method is kept for backward compatibility but no longer used in main flow
    // The response generation is now handled by generateNaturalProductRecommendation
    if (products.length === 0) {
      let response = "ขออภัย ไม่พบสินค้าที่ตรงกับความต้องการของคุณ"
      
      if (entities.category) response += ` ในหมวด${entities.category}`
      if (entities.budget?.max) response += ` ในงบ ${entities.budget.max.toLocaleString()} บาท`
      if (entities.usage) response += ` สำหรับ${entities.usage}`
      
      response += " 🔍\n\n💡 **ข้อเสนอแนะ:**\n"
      response += "• ลองค้นหาด้วยคำอื่น หรือขยายงบประมาณ\n"
      response += "• ลองใช้คำค้นหาที่เฉพาะเจาะจงมากขึ้น\n"
      response += "• หรือบอกความต้องการใช้งานให้ชัดเจนมากขึ้น"
      
      return response
    }
    
    // Simple fallback response for legacy compatibility
    const topProduct = products[0]
    return `พบสินค้า ${products.length} รายการ\n\n⭐ แนะนำ: ${topProduct.title}\n💰 ราคา: ฿${topProduct.salePrice.toLocaleString()}`
  }
  
  explainSelection(entities: ExtractedEntities, products: Product[]): string | null {
    if (products.length === 0) return null
    
    const topProduct = products[0]
    let reasoning = `💭 **ทำไมแนะนำ "${topProduct.title}":**\n`
    
    const reasons: string[] = []
    
    // Budget fit
    if (entities.budget?.max && topProduct.salePrice <= entities.budget.max) {
      reasons.push(`✅ ราคาอยู่ในงบ (฿${topProduct.salePrice.toLocaleString()})`)
    }
    
    // High rating
    if (topProduct.rating > 4) {
      reasons.push(`⭐ ได้รีวิวดี (${topProduct.rating}/5 จาก ${topProduct.totalReviews.toLocaleString()} รีวิว)`)
    }
    
    // Popular product
    if (topProduct.productView > 1000) {
      reasons.push(`🔥 เป็นที่นิยม (${topProduct.productView.toLocaleString()} ครั้งเข้าชม)`)
    }
    
    // Discount
    const discount = topProduct.price - topProduct.salePrice
    if (discount > 0) {
      const discountPercent = Math.round((discount / topProduct.price) * 100)
      reasons.push(`💰 มีส่วนลด ${discountPercent}% (ประหยัด ฿${discount.toLocaleString()})`)
    }
    
    // Stock availability
    if (topProduct.stockQuantity > 10) {
      reasons.push(`📦 มีสต็อกเพียงพอ (${topProduct.stockQuantity} ชิ้น)`)
    } else if (topProduct.stockQuantity > 0) {
      reasons.push(`⚠️ สต็อกเหลือน้อย (${topProduct.stockQuantity} ชิ้น)`)
    }
    
    // Category match
    if (entities.category) {
      const categoryMatch = topProduct.navigation?.categoryMessage1?.includes(entities.category) ||
                           topProduct.navigation?.categoryMessage2?.includes(entities.category) ||
                           topProduct.navigation?.categoryMessage3?.includes(entities.category)
      if (categoryMatch) {
        reasons.push(`🎯 ตรงตามหมวดหมู่ที่ต้องการ`)
      }
    }
    
    // Usage match
    if (entities.usage) {
      const usageKeywords = ["เล่นเกม", "ทำงาน", "เรียน", "กราฟิก"]
      const usageMatch = usageKeywords.some(keyword => 
        topProduct.description.toLowerCase().includes(keyword) ||
        topProduct.title.toLowerCase().includes(keyword)
      )
      if (usageMatch) {
        reasons.push(`🎮 เหมาะสำหรับ${entities.usage}`)
      }
    }
    
    if (reasons.length === 0) {
      reasons.push("📊 อันดับต้นๆ จากการค้นหา")
    }
    
    return reasoning + reasons.join("\n")
  }
  
  // Dynamic category discovery
  async discoverCategories(searchTerm: string): Promise<Array<{categoryId: string, path: string}>> {
    try {
      const categoryQuery = {
        productActive: true,
        $or: [
          { "navigation.categoryMessage1": { $regex: searchTerm, $options: "i" }},
          { "navigation.categoryMessage2": { $regex: searchTerm, $options: "i" }},
          { "navigation.categoryMessage3": { $regex: searchTerm, $options: "i" }}
        ]
      }
      
      const results = await this.collection.distinct("navigation", categoryQuery)
      
      return results.map((nav: any) => ({
        categoryId: nav.categoryId,
        path: `${nav.categoryMessage1} > ${nav.categoryMessage2} > ${nav.categoryMessage3}`
      }))
    } catch (error) {
      console.error("Category discovery error:", error)
      return []
    }
  }
  
  // Get product recommendations based on current selection
  async getRecommendations(currentProduct: Product, limit = 5): Promise<Product[]> {
    try {
      const recommendationQuery = {
        productActive: true,
        stockQuantity: { $gt: 0 },
        _id: { $ne: currentProduct._id },
        $or: [
          { "navigation.categoryId": currentProduct.navigation.categoryId },
          { 
            salePrice: { 
              $gte: currentProduct.salePrice * 0.8, 
              $lte: currentProduct.salePrice * 1.2 
            }
          }
        ]
      }
      
      return await this.searchProducts(recommendationQuery, limit)
    } catch (error) {
      console.error("Recommendations error:", error)
      return []
    }
  }
  
  // Get trending products
  async getTrendingProducts(limit = 10): Promise<Product[]> {
    try {
      const trendingQuery = {
        productActive: true,
        stockQuantity: { $gt: 0 },
        rating: { $gte: 4 },
        totalReviews: { $gte: 10 }
      }
      
      const results = await this.collection
        .find(trendingQuery)
        .sort({ productView: -1, totalReviews: -1 })
        .limit(limit)
        .toArray()
      
      return results as unknown as Product[]
    } catch (error) {
      console.error("Trending products error:", error)
      return []
    }
  }
  
  // Analytics: Get search insights
  async getSearchInsights(query: Record<string, any>): Promise<{
    totalResults: number,
    averagePrice: number,
    priceRange: { min: number, max: number },
    topBrands: string[],
    categories: string[]
  }> {
    try {
      const pipeline = [
        { $match: query },
        {
          $group: {
            _id: null,
            totalResults: { $sum: 1 },
            averagePrice: { $avg: "$salePrice" },
            minPrice: { $min: "$salePrice" },
            maxPrice: { $max: "$salePrice" },
            brands: { $push: "$keyword" },
            categories: { $push: "$navigation.categoryMessage1" }
          }
        }
      ]
      
      const results = await this.collection.aggregate(pipeline).toArray()
      
      if (results.length === 0) {
        return {
          totalResults: 0,
          averagePrice: 0,
          priceRange: { min: 0, max: 0 },
          topBrands: [],
          categories: []
        }
      }
      
      const data = results[0]
      
      return {
        totalResults: data.totalResults,
        averagePrice: Math.round(data.averagePrice),
        priceRange: { min: data.minPrice, max: data.maxPrice },
        topBrands: [...new Set(data.brands.flat())].slice(0, 5),
        categories: [...new Set(data.categories)].slice(0, 5)
      }
    } catch (error) {
      console.error("Search insights error:", error)
      return {
        totalResults: 0,
        averagePrice: 0,
        priceRange: { min: 0, max: 0 },
        topBrands: [],
        categories: []
      }
    }
  }
}