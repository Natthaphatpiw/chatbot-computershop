from fastapi import APIRouter, HTTPException, Depends
from app.models import RecommendationRequest, Product
from app.database import get_database
from app.services.chatbot import ITStoreChatbot
from bson import ObjectId
from typing import List

router = APIRouter()

@router.post("/recommendations", response_model=List[Product])
async def get_recommendations(request: RecommendationRequest, db=Depends(get_database)):
    try:
        chatbot = ITStoreChatbot(db)
        
        # Get the current product first
        current_product_data = await db["product_details"].find_one(
            {"_id": ObjectId(request.productId)}
        )
        
        if not current_product_data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Create Product instance with proper field mapping
        current_product = Product(**current_product_data)
        
        # Get recommendations
        recommendations = await chatbot.get_recommendations(
            current_product, 
            request.limit
        )
        
        return recommendations
    except Exception as error:
        print(f"Recommendations API Error: {error}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")