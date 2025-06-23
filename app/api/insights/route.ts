import { type NextRequest, NextResponse } from "next/server"
import clientPromise from "@/lib/mongodb"
import { ITStoreChatbot } from "@/lib/chatbot"
import { buildQuery, extractEntitiesWithLLM } from "@/lib/ai-helpers"

export async function POST(req: NextRequest) {
  try {
    const { query, userInput } = await req.json()
    
    const client = await clientPromise
    const chatbot = new ITStoreChatbot(client)
    
    let searchQuery = query
    
    // If userInput is provided, extract entities and build query
    if (userInput && !query) {
      const entities = await extractEntitiesWithLLM(userInput)
      searchQuery = buildQuery(entities)
    }
    
    if (!searchQuery) {
      return NextResponse.json({ error: "Query or userInput is required" }, { status: 400 })
    }
    
    // Get search insights
    const insights = await chatbot.getSearchInsights(searchQuery)

    return NextResponse.json({
      insights,
      success: true
    })
  } catch (error) {
    console.error("Insights API Error:", error)
    return NextResponse.json({ 
      error: "Failed to get search insights",
      insights: null,
      success: false
    }, { status: 500 })
  }
}