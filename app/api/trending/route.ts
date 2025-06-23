import { type NextRequest, NextResponse } from "next/server"
import clientPromise from "@/lib/mongodb"
import { ITStoreChatbot } from "@/lib/chatbot"

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url)
    const limit = parseInt(searchParams.get("limit") || "10")

    const client = await clientPromise
    const chatbot = new ITStoreChatbot(client)
    
    // Get trending products
    const trendingProducts = await chatbot.getTrendingProducts(limit)

    return NextResponse.json({
      products: trendingProducts,
      success: true
    })
  } catch (error) {
    console.error("Trending API Error:", error)
    return NextResponse.json({ 
      error: "Failed to get trending products",
      products: [],
      success: false
    }, { status: 500 })
  }
}