import { type NextRequest, NextResponse } from "next/server"
import clientPromise from "@/lib/mongodb"
import { generateMongoQuery, formatProductResponse } from "@/lib/ai-helpers"
import type { Product } from "@/types"
import type { MongoQueryWithReason } from "@/lib/ai-helpers"

export async function POST(req: NextRequest) {
  try {
    const { message } = await req.json()
    if (!message) {
      return NextResponse.json({ error: "Message is required" }, { status: 400 })
    }

    // รับ reason ด้วย
    const mongoQuery = await generateMongoQuery(message) as MongoQueryWithReason

    const client = await clientPromise
    const db = client.db("shopdb")
    const collection = db.collection("computershop")

    let products: Product[] = []

    try {
      const cursor = collection.find(mongoQuery.filter, {
        projection: {
          _id: 1,
          name: 1,
          description: 1,
          price: 1,
          image_url: 1,
          category: 1,
          inStock: 1,
          rating: 1,
          reviews: 1,
          stock: 1,
          tags: 1,
        },
      })

      if (mongoQuery.sort) cursor.sort(mongoQuery.sort)
      if (mongoQuery.limit) cursor.limit(mongoQuery.limit)

      products = (await cursor.toArray()) as unknown as Product[]
    } catch (dbError) {
      console.error("Database query error:", dbError)
      products = (await collection
        .find({
          $or: [
            { name: { $regex: message, $options: "i" } },
            { description: { $regex: message, $options: "i" } },
          ],
        })
        .limit(5)
        .toArray()) as unknown as Product[]
    }

    // ส่ง reason ให้กับ formatProductResponse ด้วย
    const responseText = await formatProductResponse(message, products, mongoQuery.reason)

    return NextResponse.json({
      message: responseText,
      products,
      reason: mongoQuery.reason, // ส่งกลับ reason เผื่ออยากโชว์ใน UI
    })
  } catch (error) {
    console.error("API Error:", error)
    return NextResponse.json({ error: "Failed to process request" }, { status: 500 })
  }
}
