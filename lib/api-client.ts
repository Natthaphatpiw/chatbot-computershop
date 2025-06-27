const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export interface ApiResponse<T> {
  data?: T
  error?: string
  success: boolean
}

export interface ChatRequest {
  message: string
}

export interface ChatResponse {
  message: string
  response?: string  // Backend ส่ง field นี้มา
  products: any[]
  reasoning?: string
  entities?: any
  queryReasoning?: string
  mongoQuery?: Record<string, any>  // เพิ่ม MongoDB query ที่ LLM สร้างขึ้น
  success: boolean
}

export interface RecommendationRequest {
  productId: string
  limit?: number
}

export interface InsightsRequest {
  query: Record<string, any>
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error)
      throw error
    }
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    const rawResponse = await this.makeRequest<any>('/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    })
    
    // แปลง backend response format เป็น frontend format
    return {
      message: rawResponse.response || rawResponse.message || "ไม่สามารถประมวลผลได้",
      response: rawResponse.response,
      products: rawResponse.products || [],
      reasoning: rawResponse.reasoning,
      entities: rawResponse.entities,
      queryReasoning: rawResponse.queryReasoning,
      mongoQuery: rawResponse.mongoQuery,
      success: true
    }
  }

  async getRecommendations(request: RecommendationRequest): Promise<any[]> {
    return this.makeRequest<any[]>('/recommendations', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getTrendingProducts(limit: number = 10): Promise<any[]> {
    return this.makeRequest<any[]>(`/trending?limit=${limit}`)
  }

  async getInsights(request: InsightsRequest): Promise<any> {
    return this.makeRequest<any>('/insights', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }
}

export const apiClient = new ApiClient()