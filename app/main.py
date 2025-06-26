import os
from dotenv import load_dotenv

# Load environment variables first, before importing other modules
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, recommendations, trending, insights
from app.database import connect_to_mongodb, close_mongodb_connection

app = FastAPI(
    title="IT Store Chatbot API",
    description="AI-powered chatbot API for IT equipment store",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await connect_to_mongodb()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongodb_connection()

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(recommendations.router, prefix="/api", tags=["recommendations"])
app.include_router(trending.router, prefix="/api", tags=["trending"])
app.include_router(insights.router, prefix="/api", tags=["insights"])

@app.get("/")
async def root():
    return {"message": "IT Store Chatbot API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}