export interface Product {
  _id: string
  title: string
  description: string
  cateName: string  // หมวดหมู่สินค้า (แทน navigation.categoryMessage1)
  price: number
  salePrice: number
  stockQuantity: number
  rating: number
  totalReviews: number
  productView: number
  images?: {
    original?: {
      url: string[]
    }
    medium?: {
      url: string[]
    }
    large?: {
      url: string[]
    }
    small?: {
      url: string[]
    }
    icon?: {
      url: string[]
    }
  }
  freeShipping?: boolean  // ฟิลด์ใหม่
  product_warranty_2_year?: string  // ฟิลด์ใหม่
  product_warranty_3_year?: string  // ฟิลด์ใหม่
  
  // ฟิลด์เสริม
  categoryId?: number
  cateId?: number
  productCode?: string
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

export interface ExtractedEntities {
  category?: string
  subCategory?: string
  usage?: string
  budget?: {
    min?: number
    max?: number
  }
  brand?: string
  specs?: string[]
  keywords?: string[]
  features?: string[]
  suggestions?: string[]
}

export interface MongoQueryWithReason {
  filter: Record<string, any>
  sort?: Record<string, 1 | -1>
  limit?: number
  reason?: string
}
