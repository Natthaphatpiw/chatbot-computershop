from fastapi import APIRouter, HTTPException, Depends
from app.models import ChatRequest, ChatResponse, ExtractedEntities, Budget
from app.database import get_database
from app.services.chatbot import ITStoreChatbot

router = APIRouter()

def convert_stage1_to_entities(stage1_data: dict) -> ExtractedEntities:
    """Convert stage1 processedTerms to ExtractedEntities format"""
    processed_terms = stage1_data.get("processedTerms", {})
    
    # Extract budget
    budget_data = processed_terms.get("budget")
    budget = None
    if budget_data:
        budget = Budget(
            min=budget_data.get("min"),
            max=budget_data.get("max")
        )
    
    return ExtractedEntities(
        category=processed_terms.get("category"),
        budget=budget,
        keywords=processed_terms.get("used", []) + processed_terms.get("remaining", []),
        intent="two_stage_analysis"
    )

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db=Depends(get_database)):
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Initialize chatbot with database
        chatbot = ITStoreChatbot(db)
        
        # Process user input with comprehensive chatbot system
        result = await chatbot.process_user_input(request.message)
        
        # Convert stage1 data to entities format for backward compatibility
        entities = None
        if result.get("stage1"):
            entities = convert_stage1_to_entities(result["stage1"])
        
        return ChatResponse(
            message=result["response"],
            products=result["products"],
            reasoning=result["reasoning"],
            entities=entities,
            queryReasoning=result["queryReasoning"],
            mongoQuery=result["mongoQuery"],
            success=True
        )
    except Exception as error:
        print(f"API Error: {error}")
        return ChatResponse(
            message="ขออภัย เกิดข้อผิดพลาดในการค้นหาสินค้า กรุณาลองใหม่อีกครั้ง 🔧",
            products=[],
            reasoning=None,
            entities=None,
            queryReasoning=None,
            mongoQuery=None,
            success=False
        )