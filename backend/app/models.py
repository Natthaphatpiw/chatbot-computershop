from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Annotated
from bson import ObjectId
from pydantic import field_validator

class PyObjectId(str):
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError('Invalid ObjectId')

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

class ImageSize(BaseModel):
    heigth: Optional[str] = None  # Note: "heigth" is misspelled in original schema
    url: List[str] = []
    width: Optional[str] = None

class Images(BaseModel):
    icon: Optional[ImageSize] = None
    large: Optional[ImageSize] = None
    medium: Optional[ImageSize] = None
    original: Optional[ImageSize] = None
    small: Optional[ImageSize] = None

class Product(BaseModel):
    id: str = Field(alias="_id")
    title: str
    description: str
    cateName: str  # หมวดหมู่สินค้า (แทน navigation.categoryMessage1)
    price: float
    salePrice: float
    stockQuantity: int
    rating: float
    totalReviews: int
    productView: int
    images: Optional[Images] = None
    freeShipping: Optional[bool] = False  # ฟิลด์ใหม่
    product_warranty_2_year: Optional[str] = None  # ฟิลด์ใหม่
    product_warranty_3_year: Optional[str] = None  # ฟิลด์ใหม่
    
    # ฟิลด์เสริมจาก schema
    categoryId: Optional[int] = None
    cateId: Optional[int] = None
    productCode: Optional[str] = None

    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class Budget(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None

class ExtractedEntities(BaseModel):
    category: Optional[str] = None
    subCategory: Optional[str] = None
    usage: Optional[str] = None
    budget: Optional[Budget] = None
    brand: Optional[str] = None
    specs: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    features: Optional[List[str]] = None
    intent: Optional[str] = None
    suggestions: Optional[List[str]] = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str
    products: List[Product]
    reasoning: Optional[str] = None
    entities: Optional[ExtractedEntities] = None
    queryReasoning: Optional[str] = None
    mongoQuery: Optional[Dict[str, Any]] = None  # เพิ่ม MongoDB query ที่ LLM สร้างขึ้น
    success: bool

class RecommendationRequest(BaseModel):
    productId: str
    limit: Optional[int] = 5

class InsightsRequest(BaseModel):
    query: Dict[str, Any]