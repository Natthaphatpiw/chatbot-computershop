import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def get_database():
    return db.database

async def connect_to_mongodb():
    """Create database connection"""
    db.client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db.database = db.client["dashboard-ai-data"]
    print("Connected to MongoDB")

async def close_mongodb_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")