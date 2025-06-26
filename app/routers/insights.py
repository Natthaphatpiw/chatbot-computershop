from fastapi import APIRouter, HTTPException, Depends
from app.models import InsightsRequest
from app.database import get_database
from app.services.chatbot import ITStoreChatbot
from typing import Dict, Any

router = APIRouter()

@router.post("/insights")
async def get_search_insights(
    request: InsightsRequest,
    db=Depends(get_database)
) -> Dict[str, Any]:
    try:
        chatbot = ITStoreChatbot(db)
        insights = await chatbot.get_search_insights(request.query)
        return insights
    except Exception as error:
        print(f"Insights API Error: {error}")
        raise HTTPException(status_code=500, detail="Failed to get search insights")