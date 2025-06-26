# IT Store Chatbot - Separated Frontend/Backend Architecture

This project has been converted from a full-stack Next.js application to a separated frontend (Next.js) and backend (Python FastAPI) architecture.

## Architecture Overview

### Frontend (Next.js)
- **Location**: Root directory
- **Port**: 3000 (default)
- **Tech Stack**: Next.js 14, TypeScript, Tailwind CSS, React

### Backend (Python FastAPI)  
- **Location**: `/backend` directory
- **Port**: 8000 (default)
- **Tech Stack**: FastAPI, Motor (async MongoDB), OpenAI SDK, Pydantic

## Quick Start

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env file with your credentials
nano .env
```

Required environment variables for backend:
```
MONGODB_URI=mongodb://localhost:27017/dashboard-ai-data
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Start Backend Server

```bash
# From backend directory
python start.py

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
# From root directory
npm install

# Copy environment file
cp .env.local.example .env.local

# Edit .env.local file
nano .env.local
```

Required environment variables for frontend:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### 4. Start Frontend Server

```bash
# From root directory
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## API Endpoints

The Python backend provides the following REST API endpoints:

### Chat API
- **POST** `/api/chat`
  - Process user chat messages
  - Returns AI response with product recommendations

### Recommendations API  
- **POST** `/api/recommendations`
  - Get product recommendations based on current selection

### Trending Products API
- **GET** `/api/trending?limit=10`
  - Get trending/popular products

### Search Insights API
- **POST** `/api/insights`
  - Get search analytics and insights

## Key Changes from Full-Stack Version

### Removed
- `/app/api/` - All Next.js API routes
- `/lib/mongodb.ts` - Direct MongoDB connection from frontend
- `/lib/chatbot.ts` - Server-side chatbot logic
- `/lib/ai-helpers.ts` - Server-side AI helpers

### Added
- `/backend/` - Complete Python FastAPI backend
- `/lib/api-client.ts` - Frontend API client for backend communication
- Environment configuration for separated services

### Modified
- `/app/page.tsx` - Updated to use API client instead of direct API calls
- Package dependencies - Removed server-side packages from frontend

## Development Workflow

1. **Start Backend First**: Always start the Python backend before the frontend
2. **API Changes**: Modify backend code in `/backend/app/`
3. **Frontend Changes**: Modify Next.js code in root directory
4. **Database**: Backend connects directly to MongoDB
5. **Environment**: Keep separate environment files for frontend and backend

## Production Deployment

### Backend Deployment
- Deploy FastAPI app using Docker, Railway, or cloud providers
- Set production environment variables
- Configure CORS for your frontend domain

### Frontend Deployment  
- Deploy Next.js app to Vercel, Netlify, or cloud providers
- Update `NEXT_PUBLIC_API_URL` to point to production backend

### Database
- Use MongoDB Atlas or cloud MongoDB instance
- Update `MONGODB_URI` in backend environment

## Benefits of Separated Architecture

1. **Scalability**: Frontend and backend can be scaled independently
2. **Technology Flexibility**: Can use different tech stacks for each layer
3. **Team Organization**: Frontend and backend teams can work independently
4. **Deployment Flexibility**: Can deploy to different platforms
5. **API Reusability**: Backend API can be used by multiple frontends (mobile, web, etc.)

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure backend CORS is configured for frontend URL
2. **Connection Refused**: Ensure backend is running before starting frontend  
3. **Environment Variables**: Check that all required env vars are set
4. **MongoDB Connection**: Verify MongoDB URI and database access

### Logs
- **Backend Logs**: Check FastAPI server console output
- **Frontend Logs**: Check browser console and Next.js terminal
- **Database**: Check MongoDB logs if connection issues persist