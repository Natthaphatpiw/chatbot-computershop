# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Separated Architecture (Frontend + Backend)
- **Start both services**: `./scripts/start-dev.sh` (recommended for development)
- **Frontend only**: `npm run dev` (starts on http://localhost:3000)
- **Backend only**: `cd backend && python start.py` (starts on http://localhost:8000)
- **Build frontend**: `npm run build` 
- **Lint frontend**: `npm run lint`
- **Test backend**: `cd backend && python test_backend.py`

### Legacy Full-Stack Commands
- **Production start**: `npm start` (frontend only - requires backend running separately)

## Architecture Overview

This system has been converted from a full-stack Next.js application to a **separated frontend/backend architecture**:

- **Frontend**: Next.js 14 with TypeScript, Tailwind CSS, React components
- **Backend**: Python FastAPI with MongoDB, OpenAI GPT-4 integration
- **Communication**: REST API between frontend and backend

The backend provides AI-powered chatbot functionality with advanced entity extraction, flexible search, and intelligent product recommendations.

### Core Components

#### Backend (Python FastAPI)
- **ITStoreChatbot Class**: `/backend/app/services/chatbot.py` - Main chatbot engine with entity extraction, flexible search, fallback systems, and analytics  
- **AI Helpers**: `/backend/app/services/ai_helpers.py` - LLM-based entity extraction, text normalization, category mapping, and query building utilities
- **Chat API**: `/backend/app/routers/chat.py` - Main endpoint using ITStoreChatbot for processing user queries
- **Additional APIs**: `/backend/app/routers/recommendations.py`, `/backend/app/routers/trending.py`, `/backend/app/routers/insights.py` - Extended functionality endpoints
- **Database**: `/backend/app/database.py` - Async MongoDB connection to "dashboard-ai-data" database

#### Frontend (Next.js)
- **API Client**: `/lib/api-client.ts` - Frontend API client for communicating with Python backend
- **ProductCard**: Enhanced component with image carousel, discount display, and new schema support
- **Chat Interface**: `/app/page.tsx` - Main chat interface that calls backend APIs

### Key Architecture Patterns

1. **LLM-Powered Entity Extraction**: Uses OpenAI GPT-4o-mini to extract structured entities (category, usage, budget, brand, specs, features) from natural language
2. **Progressive Search Fallback**: Multi-level search strategy that progressively relaxes constraints when no results are found
3. **Flexible Text Normalization**: Handles Thai language variations, common misspellings, and alternative terms
4. **Smart Query Building**: Combines category keywords, usage patterns, enhanced search terms with MongoDB aggregation
5. **Comprehensive Error Handling**: Graceful degradation with fallback entity extraction and search mechanisms

### Database Schema (New)

MongoDB database: `dashboard-ai-data`  
Collection: `product_details`

**Core Fields:**
- `title`, `description`, `keyword[]` - Product information and searchable terms
- `price`, `salePrice`, `stockQuantity` - Pricing and inventory
- `navigation.{categoryId, categoryMessage1, categoryMessage2, categoryMessage3}` - Hierarchical categorization
- `productActive`, `rating`, `totalReviews`, `productView` - Status and metrics
- `images.medium.url[]` - Product image URLs

### Entity Extraction System

The chatbot extracts structured data from user inputs:
- **Category**: โน้ตบุ๊ก, คีย์บอร์ด, เมาส์, การ์ดจอ, ซีพียู, หูฟัง, etc.
- **Usage**: เล่นเกม, ทำงาน, เรียน, กราฟิก, โปรแกรม, วิดีโอ
- **Budget**: Min/max price ranges extracted from text
- **Brand**: ASUS, HP, Dell, MSI, Razer, Logitech, etc.
- **Specs**: RAM sizes, CPU models, graphics cards, etc.
- **Features**: RGB, ไร้สาย, mechanical, etc.

### Search Strategy

1. **Primary Search**: Full query with all extracted entities
2. **Budget Relaxation**: Remove price constraints if no results
3. **Category-Only Search**: Use enhanced category keywords
4. **Text Fallback**: Simple regex search on title/description
5. **Ranking**: Sort by popularity (productView), rating, and social proof

### API Endpoints (Backend)

**Base URL**: `http://localhost:8000/api` (development)

- `POST /api/chat` - Main chat processing with entity extraction and product search
- `POST /api/recommendations` - Get product recommendations based on current selection  
- `GET /api/trending?limit=N` - Fetch trending/popular products
- `POST /api/insights` - Get search analytics (price ranges, categories, brands)
- `GET /health` - Backend health check endpoint

**Frontend Integration**: All API calls are handled through `/lib/api-client.ts`

### Thai Language Support

- Comprehensive text normalization for common misspellings
- Category keyword mapping with variations (โน้ตบุ๊ก, โน้ตบุ้ค, โน๊ตบุ๊ค, etc.)
- Usage pattern recognition in Thai
- Bilingual keyword enhancement (Thai + English terms)

### Environment Setup

#### Backend Environment (`.env` in `/backend/`)
```
MONGODB_URI=mongodb://localhost:27017/dashboard-ai-data
OPENAI_API_KEY=your_openai_api_key_here
```

#### Frontend Environment (`.env.local` in root)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

**Note**: Backend must be running before starting the frontend for proper API communication.

### Testing User Input Examples

- "โน้ตบุ๊คทำงานงบ 20000" → Budget-constrained work laptop search
- "เมาส์เกมมิ่งไร้สาย RGB" → Gaming mouse with specific features
- "การ์ดจอ RTX 4060 ไม่เกิน 15000" → GPU with spec and budget constraints
- "คีย์บอร์ด mechanical เงียบๆ" → Keyboard with specific features