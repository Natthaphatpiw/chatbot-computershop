export interface Product {
  _id: string
  title: string
  description: string
  keyword: string[]
  price: number
  salePrice: number
  stockQuantity: number
  navigation: {
    categoryId: string
    categoryMessage1: string
    categoryMessage2: string
    categoryMessage3: string
  }
  productActive: boolean
  rating: number
  totalReviews: number
  productView: number
  images: {
    medium: {
      url: string[]
    }
  }
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
