export interface Product {
  _id: string
  name: string
  description: string
  price: number
  image_url: string
  category: "โน้ตบุ๊ค" | "คอมพิวเตอร์ตั้งโต๊ะ" | "อุปกรณ์เสริม" | "จัดเก็บข้อมูล" | "เกมมิ่งเกียร์"
  stock: number
  inStock?: boolean
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
