import { type NextRequest, NextResponse } from "next/server"
import clientPromise from "@/lib/mongodb"
import { ITStoreChatbot } from "@/lib/chatbot"

export async function POST(req: NextRequest) {
  try {
    const { productId } = await req.json()
    if (!productId) {
      return NextResponse.json({ error: "Product ID is required" }, { status: 400 })
    }

    const client = await clientPromise
    const chatbot = new ITStoreChatbot(client)
    
    // First get the current product
    const currentProduct = await chatbot.searchProducts({ _id: productId }, 1)
    if (currentProduct.length === 0) {
      return NextResponse.json({ error: "Product not found" }, { status: 404 })
    }
    
    // Get recommendations
    const recommendations = await chatbot.getRecommendations(currentProduct[0])

    return NextResponse.json({
      recommendations,
      success: true
    })
  } catch (error) {
    console.error("Recommendations API Error:", error)
    return NextResponse.json({ 
      error: "Failed to get recommendations",
      recommendations: [],
      success: false
    }, { status: 500 })
  }
}