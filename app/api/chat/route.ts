import { type NextRequest, NextResponse } from "next/server"
import clientPromise from "@/lib/mongodb"
import { generateMongoQuery, formatProductResponse } from "@/lib/ai-helpers"
import type { Product } from "@/types"

export async function POST(req: NextRequest) {
  try {
    const { message } = await req.json()

    if (!message) {
      return NextResponse.json({ error: "Message is required" }, { status: 400 })
    }

    const mongoQuery = await generateMongoQuery(message)

    const client = await clientPromise
    const db = client.db("shopdb") // ✅ Database name you use
    const collection = db.collection("products")

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

    const responseText = await formatProductResponse(message, products)

    return NextResponse.json({
      message: responseText,
      products,
    })
  } catch (error) {
    console.error("API Error:", error)
    return NextResponse.json({ error: "Failed to process request" }, { status: 500 })
  }
}
