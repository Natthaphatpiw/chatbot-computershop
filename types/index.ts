export interface Product {
  _id: string
  name: string
  description: string
  price: number
  image_url: string // ✅ เปลี่ยนจาก `image` เป็น `image_url`
  category: string
  inStock?: boolean // ✅ เป็น optional เพราะข้อมูลคุณไม่มี field นี้
  rating?: number
  reviews?: number
  tags?: string[]
}


export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  products?: Product[]
  timestamp: Date
}

export interface MongoQuery {
  filter: Record<string, any>
  sort?: Record<string, 1 | -1>
  limit?: number
}
