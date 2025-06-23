import { type NextRequest, NextResponse } from "next/server"
import clientPromise from "@/lib/mongodb"
import { ITStoreChatbot } from "@/lib/chatbot"

export async function POST(req: NextRequest) {
  try {
    const { message } = await req.json()
    if (!message) {
      return NextResponse.json({ error: "Message is required" }, { status: 400 })
    }

    // Initialize chatbot with MongoDB client
    const client = await clientPromise
    const chatbot = new ITStoreChatbot(client)
    
    // Process user input with comprehensive chatbot system
    const result = await chatbot.processUserInput(message)

    return NextResponse.json({
      message: result.response,
      products: result.products,
      reasoning: result.reasoning,
      entities: result.entities, // Include extracted entities for debugging/analytics
      success: true
    })
  } catch (error) {
    console.error("API Error:", error)
    return NextResponse.json({ 
      error: "Failed to process request",
      message: "ขออภัย เกิดข้อผิดพลาดในการค้นหาสินค้า กรุณาลองใหม่อีกครั้ง 🔧",
      products: [],
      reasoning: null,
      entities: null,
      success: false
    }, { status: 500 })
  }
}
