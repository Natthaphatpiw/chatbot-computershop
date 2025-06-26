from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import Product
from app.database import get_database
from app.services.chatbot import ITStoreChatbot
from typing import List

router = APIRouter()

@router.get("/trending", response_model=List[Product])
async def get_trending_products(
    limit: int = Query(default=10, ge=1, le=50),
    db=Depends(get_database)
):
    try:
        chatbot = ITStoreChatbot(db)
        trending_products = await chatbot.get_trending_products(limit)
        return trending_products
    except Exception as error:
        print(f"Trending API Error: {error}")
        raise HTTPException(status_code=500, detail="Failed to get trending products")