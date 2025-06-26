from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any
from app.models import Product, ExtractedEntities
from app.services.ai_helpers_improved import (
    generate_optimal_mongo_query_v2,
    filter_and_rank_products_v2,
    generate_natural_product_recommendation_v2,
    normalize_text,
    get_category_mapping
)

class ITStoreChatbotV2:
    """
    Enhanced IT Store Chatbot with 2-LLM architecture:
    LLM1: Generates precise MongoDB queries
    LLM2: Filters and ranks product results based on user intent
    """
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["product_details"]  # Updated collection name
    
    async def process_user_input(self, user_input: str):
        try:
            # 1. Normalize text
            normalized_input = normalize_text(user_input)
            
            # 2. LLM 1: Generate optimal MongoDB query with enhanced understanding
            query_result = await generate_optimal_mongo_query_v2(normalized_input)
            
            # 3. Search products with the precise query
            raw_products = await self.search_products_precise(query_result["query"])
            
            # 4. LLM 2: Filter and rank products based on user intent
            filtered_products = await filter_and_rank_products_v2(
                user_input,
                query_result["entities"],
                raw_products,
                query_result["query"]
            )
            
            # 5. Generate natural language response
            response = await generate_natural_product_recommendation_v2(
                user_input,
                query_result["entities"],
                filtered_products,
                query_result["reasoning"],
                query_result["query"]
            )
            
            return {
                "products": filtered_products,
                "response": response,
                "entities": query_result["entities"],
                "mongoQuery": query_result["query"],
                "queryReasoning": query_result["reasoning"],
                "confidence": query_result.get("confidence", 0.8),
                "rawProductCount": len(raw_products),
                "filteredProductCount": len(filtered_products),
                "debug": {
                    "normalizedInput": normalized_input,
                    "llm1Result": query_result,
                    "rawProducts": len(raw_products),
                    "afterLLM2": len(filtered_products)
                }
            }
            
        except Exception as error:
            print(f"Chatbot V2 error: {error}")
            return {
                "products": [],
                "response": "ขออภัย เกิดข้อผิดพลาดในการค้นหาสินค้า กรุณาลองใหม่อีกครั้ง 🔧",
                "entities": None,
                "mongoQuery": None,
                "queryReasoning": None,
                "confidence": 0.0,
                "rawProductCount": 0,
                "filteredProductCount": 0,
                "error": str(error)
            }
    
    async def search_products_precise(self, query: Dict[str, Any], limit: int = 50) -> List[Product]:
        """
        Execute precise MongoDB query with proper error handling
        """
        try:
            print(f"[DEBUG] Executing MongoDB query: {query}")
            
            cursor = self.collection.find(
                query,
                {
                    "_id": 1,
                    "title": 1,
                    "description": 1,
                    "cateName": 1,
                    "price": 1,
                    "salePrice": 1,
                    "stockQuantity": 1,
                    "rating": 1,
                    "totalReviews": 1,
                    "productView": 1,
                    "images": 1,
                    "freeShipping": 1,
                    "product_warranty_2_year": 1,
                    "product_warranty_3_year": 1,
                    "categoryId": 1,
                    "cateId": 1,
                    "productCode": 1,
                    "productActive": 1
                }
            ).sort([
                ("productView", -1),  # Most popular first
                ("rating", -1),       # Highest rated
                ("totalReviews", -1)  # Most reviewed
            ]).limit(limit)
            
            results = await cursor.to_list(length=limit)
            print(f"[DEBUG] Found {len(results)} products from database")
            
            products = []
            for result in results:
                try:
                    # Handle potential data inconsistencies
                    product_data = {
                        "id": result.get("_id"),
                        "title": result.get("title", ""),
                        "description": result.get("description", ""),
                        "cateName": result.get("cateName", ""),
                        "price": float(result.get("price", 0)),
                        "salePrice": float(result.get("salePrice", 0)),
                        "stockQuantity": int(result.get("stockQuantity", 0)),
                        "rating": float(result.get("rating", 0)),
                        "totalReviews": int(result.get("totalReviews", 0)),
                        "productView": int(result.get("productView", 0)),
                        "images": result.get("images", {}),
                        "freeShipping": result.get("freeShipping", False),
                        "product_warranty_2_year": result.get("product_warranty_2_year"),
                        "product_warranty_3_year": result.get("product_warranty_3_year"),
                        "categoryId": result.get("categoryId"),
                        "cateId": result.get("cateId"),
                        "productCode": result.get("productCode", ""),
                        "productActive": result.get("productActive", True)
                    }
                    
                    products.append(Product(**product_data))
                except Exception as product_error:
                    print(f"[WARNING] Failed to parse product: {product_error}")
                    continue
            
            print(f"[DEBUG] Successfully parsed {len(products)} products")
            return products
            
        except Exception as error:
            print(f"[ERROR] Database search error: {error}")
            return []
    
    async def search_with_progressive_fallback(self, entities: Dict[str, Any], primary_query: Dict[str, Any]) -> List[Product]:
        """
        Progressive fallback strategy for when primary query returns no results
        """
        # Try primary query first
        products = await self.search_products_precise(primary_query, limit=20)
        
        if len(products) > 0:
            return products
        
        print("[DEBUG] Primary query returned no results, trying fallback strategies...")
        
        # Fallback 1: Remove budget constraint
        if "salePrice" in primary_query:
            fallback_query = {k: v for k, v in primary_query.items() if k != "salePrice"}
            products = await self.search_products_precise(fallback_query, limit=20)
            if len(products) > 0:
                print("[DEBUG] Fallback 1 (no budget) found products")
                return products
        
        # Fallback 2: Category-only search with broader matching
        if entities.get("category"):
            category_mapping = get_category_mapping()
            possible_categories = []
            
            # Find all possible categories for this user input
            for thai_term, eng_categories in category_mapping.items():
                if thai_term in entities.get("keywords", []):
                    possible_categories.extend(eng_categories)
            
            if possible_categories:
                fallback_query = {
                    "stockQuantity": {"$gt": 0},
                    "productActive": True,
                    "cateName": {"$in": list(set(possible_categories))}
                }
                products = await self.search_products_precise(fallback_query, limit=20)
                if len(products) > 0:
                    print("[DEBUG] Fallback 2 (category matching) found products")
                    return products
        
        # Fallback 3: Text search in title and description
        if entities.get("keywords"):
            search_terms = [kw for kw in entities["keywords"] if len(kw) > 2]
            if search_terms:
                fallback_query = {
                    "stockQuantity": {"$gt": 0},
                    "productActive": True,
                    "$or": [
                        {"title": {"$regex": "|".join(search_terms), "$options": "i"}},
                        {"description": {"$regex": "|".join(search_terms), "$options": "i"}}
                    ]
                }
                products = await self.search_products_precise(fallback_query, limit=20)
                if len(products) > 0:
                    print("[DEBUG] Fallback 3 (text search) found products")
                    return products
        
        print("[DEBUG] All fallback strategies failed")
        return []
    
    async def get_recommendations(self, current_product: Product, limit: int = 5) -> List[Product]:
        """Get product recommendations based on current product"""
        try:
            recommendation_query = {
                "stockQuantity": {"$gt": 0},
                "productActive": True,
                "_id": {"$ne": current_product.id},
                "$or": [
                    {"cateName": current_product.cateName} if current_product.cateName else {},
                    {
                        "salePrice": {
                            "$gte": current_product.salePrice * 0.8,
                            "$lte": current_product.salePrice * 1.2
                        }
                    }
                ]
            }
            
            return await self.search_products_precise(recommendation_query, limit)
        except Exception as error:
            print(f"Recommendations error: {error}")
            return []
    
    async def get_trending_products(self, limit: int = 10) -> List[Product]:
        """Get trending/popular products"""
        try:
            trending_query = {
                "stockQuantity": {"$gt": 0},
                "productActive": True,
                "rating": {"$gte": 3.0}
            }
            
            cursor = self.collection.find(trending_query).sort([
                ("productView", -1),
                ("totalReviews", -1),
                ("rating", -1)
            ]).limit(limit)
            
            results = await cursor.to_list(length=limit)
            return [Product(**result) for result in results]
        except Exception as error:
            print(f"Trending products error: {error}")
            return []
    
    async def get_search_insights(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Get analytics about search results"""
        try:
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": None,
                        "totalResults": {"$sum": 1},
                        "averagePrice": {"$avg": "$salePrice"},
                        "minPrice": {"$min": "$salePrice"},
                        "maxPrice": {"$max": "$salePrice"},
                        "categories": {"$addToSet": "$cateName"},
                        "avgRating": {"$avg": "$rating"},
                        "totalViews": {"$sum": "$productView"}
                    }
                }
            ]
            
            results = await self.collection.aggregate(pipeline).to_list(length=1)
            
            if len(results) == 0:
                return {
                    "totalResults": 0,
                    "averagePrice": 0,
                    "priceRange": {"min": 0, "max": 0},
                    "categories": [],
                    "avgRating": 0,
                    "totalViews": 0
                }
            
            data = results[0]
            
            return {
                "totalResults": data.get("totalResults", 0),
                "averagePrice": round(data.get("averagePrice", 0)),
                "priceRange": {
                    "min": data.get("minPrice", 0), 
                    "max": data.get("maxPrice", 0)
                },
                "categories": data.get("categories", []),
                "avgRating": round(data.get("avgRating", 0), 1),
                "totalViews": data.get("totalViews", 0)
            }
        except Exception as error:
            print(f"Search insights error: {error}")
            return {"error": str(error)}

# Backward compatibility - create an alias
ITStoreChatbot = ITStoreChatbotV2