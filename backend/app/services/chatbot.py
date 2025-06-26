from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any
from app.models import Product, ExtractedEntities
from app.services.two_stage_llm import (
    stage1_basic_query_builder,
    stage2_content_analyzer,
    generate_two_stage_response,
    normalize_text_advanced
)

class ITStoreChatbot:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["products"]  # Fixed to use correct collection name
    
    async def process_user_input(self, user_input: str):
        try:
            # 1. Normalize text with advanced Thai language processing
            normalized_input = normalize_text_advanced(user_input)
            
            # 2. Stage 1: Basic query building for initial filtering
            stage1_result = await stage1_basic_query_builder(user_input)
            
            # 3. Search products with Stage 1 query
            raw_products = await self.search_products_precise(stage1_result["query"])
            
            # 4. If no results, try progressive fallback
            if len(raw_products) == 0:
                raw_products = await self.search_with_fallback_two_stage(
                    stage1_result["processedTerms"], 
                    stage1_result["query"]
                )
            
            # 5. Stage 2: Deep content analysis and product matching
            filtered_products = await stage2_content_analyzer(
                user_input,
                stage1_result,
                raw_products
            )
            
            # 6. Generate two-stage response with process explanation
            response = await generate_two_stage_response(
                user_input,
                stage1_result,
                filtered_products
            )
            
            return {
                "products": filtered_products,
                "response": response,
                "reasoning": self.explain_two_stage_selection(stage1_result, filtered_products),
                "stage1": stage1_result,
                "queryReasoning": stage1_result["reasoning"],
                "mongoQuery": stage1_result["query"],
                "confidence": stage1_result.get("confidence", 0.8),
                "rawProductCount": len(raw_products),
                "filteredProductCount": len(filtered_products),
                "searchMethod": "two_stage_llm"
            }
        except Exception as error:
            print(f"Chatbot error: {error}")
            return {
                "products": [],
                "response": "ขออภัย เกิดข้อผิดพลาดในการค้นหาสินค้า กรุณาลองใหม่อีกครั้ง 🔧",
                "reasoning": None,
                "stage1": None,
                "queryReasoning": None,
                "mongoQuery": None,
                "confidence": 0.0,
                "rawProductCount": 0,
                "filteredProductCount": 0,
                "searchMethod": "error",
                "error": str(error)
            }
    
    async def search_products_precise(self, query: Dict[str, Any], limit: int = 50) -> List[Product]:
        """Execute precise MongoDB query with proper error handling"""
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
                    "productCode": 1
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
                        "productCode": result.get("productCode", "")
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
    
    async def search_with_fallback_two_stage(self, processed_terms: Dict[str, Any], primary_query: Dict[str, Any]) -> List[Product]:
        """Progressive fallback strategy using enhanced search methods"""
        print("[DEBUG] Starting progressive fallback search...")
        
        # Fallback 1: Remove budget constraint
        if "salePrice" in primary_query:
            fallback_query = {k: v for k, v in primary_query.items() if k != "salePrice"}
            products = await self.search_products_precise(fallback_query, limit=20)
            if len(products) > 0:
                print(f"[DEBUG] Fallback 1 (no budget) found {len(products)} products")
                return products
        
        # Fallback 2: Category-only search with broader matching
        if processed_terms.get("category"):
            fallback_query = {
                "stockQuantity": {"$gt": 0},
                "cateName": processed_terms["category"]
            }
            products = await self.search_products_precise(fallback_query, limit=20)
            if len(products) > 0:
                print(f"[DEBUG] Fallback 2 (category matching) found {len(products)} products")
                return products
        
        # Fallback 3: Text search in title and description using remaining terms
        remaining_terms = processed_terms.get("remaining", [])
        if remaining_terms:
            search_terms = []
            for term in remaining_terms:
                if isinstance(term, str) and len(term.strip()) > 2:
                    search_terms.extend(term.split())
            
            if search_terms:
                search_terms = [term for term in search_terms if len(term) > 2]
                fallback_query = {
                    "stockQuantity": {"$gt": 0},
                    "$or": [
                        {"title": {"$regex": "|".join(search_terms), "$options": "i"}},
                        {"description": {"$regex": "|".join(search_terms), "$options": "i"}}
                    ]
                }
                products = await self.search_products_precise(fallback_query, limit=20)
                if len(products) > 0:
                    print(f"[DEBUG] Fallback 3 (text search) found {len(products)} products")
                    return products
        
        print("[DEBUG] All fallback strategies failed")
        return []
    
    async def search_products(self, query: Dict[str, Any], limit: int = 10) -> List[Product]:
        try:
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
                }
            ).sort([("productView", -1), ("rating", -1), ("totalReviews", -1)]).limit(limit)
            
            results = await cursor.to_list(length=limit)
            return [Product(**result) for result in results]
        except Exception as error:
            print(f"Database search error: {error}")
            return []
    
    def explain_two_stage_selection(self, stage1_result: Dict[str, Any], products: List[Product]) -> str:
        if len(products) == 0:
            return None
        
        top_product = products[0]
        processed_terms = stage1_result.get("processedTerms", {})
        used_terms = processed_terms.get("used", [])
        remaining_terms = processed_terms.get("remaining", [])
        
        reasoning = f"💭 **Two-Stage Analysis - \"{top_product.title}\":**\n"
        
        reasons = []
        
        # Stage 1 filtering info
        if used_terms:
            reasons.append(f"🔍 Stage 1 กรอง: {', '.join(used_terms)}")
        
        # Stage 2 analysis info
        if remaining_terms:
            reasons.append(f"🎯 Stage 2 วิเคราะห์: {', '.join(remaining_terms)}")
        
        # Budget fit
        budget = processed_terms.get("budget")
        if budget and budget.get("max") and top_product.salePrice <= budget["max"]:
            reasons.append(f"✅ ราคาอยู่ในงบ (฿{top_product.salePrice:,})")
        
        # High rating
        if top_product.rating > 4:
            reasons.append(f"⭐ ได้รีวิวดี ({top_product.rating}/5 จาก {top_product.totalReviews:,} รีวิว)")
        
        # Popular product
        if top_product.productView > 1000:
            reasons.append(f"🔥 เป็นที่นิยม ({top_product.productView:,} ครั้งเข้าชม)")
        
        # Discount
        discount = top_product.price - top_product.salePrice
        if discount > 0:
            discount_percent = round((discount / top_product.price) * 100)
            reasons.append(f"💰 มีส่วนลด {discount_percent}% (ประหยัด ฿{discount:,})")
        
        # Stock availability
        if top_product.stockQuantity > 10:
            reasons.append(f"📦 มีสต็อกเพียงพอ ({top_product.stockQuantity} ชิ้น)")
        elif top_product.stockQuantity > 0:
            reasons.append(f"⚠️ สต็อกเหลือน้อย ({top_product.stockQuantity} ชิ้น)")
        
        # Category match
        category = processed_terms.get("category")
        if category and top_product.cateName:
            if category in top_product.cateName:
                reasons.append("🎯 ตรงตามหมวดหมู่ที่ต้องการ")
        
        if len(reasons) == 0:
            reasons.append("📊 อันดับต้นๆ จากการค้นหา")
        
        return reasoning + "\n".join(reasons)
    
    async def get_recommendations(self, current_product: Product, limit: int = 5) -> List[Product]:
        try:
            recommendation_query = {
                "stockQuantity": {"$gt": 0},
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
            
            return await self.search_products(recommendation_query, limit)
        except Exception as error:
            print(f"Recommendations error: {error}")
            return []
    
    async def get_trending_products(self, limit: int = 10) -> List[Product]:
        try:
            trending_query = {
                "stockQuantity": {"$gt": 0},
                "rating": {"$gte": 3},  # ลดเงื่อนไขเพราะข้อมูลใหม่มีรีวิวน้อย
                "totalReviews": {"$gte": 1}
            }
            
            cursor = self.collection.find(trending_query).sort([
                ("productView", -1),
                ("totalReviews", -1)
            ]).limit(limit)
            
            results = await cursor.to_list(length=limit)
            return [Product(**result) for result in results]
        except Exception as error:
            print(f"Trending products error: {error}")
            return []
    
    async def get_search_insights(self, query: Dict[str, Any]) -> Dict[str, Any]:
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
                        "brands": {"$push": "$keyword"},
                        "categories": {"$push": "$navigation.categoryMessage1"}
                    }
                }
            ]
            
            results = await self.collection.aggregate(pipeline).to_list(length=1)
            
            if len(results) == 0:
                return {
                    "totalResults": 0,
                    "averagePrice": 0,
                    "priceRange": {"min": 0, "max": 0},
                    "topBrands": [],
                    "categories": []
                }
            
            data = results[0]
            
            return {
                "totalResults": data["totalResults"],
                "averagePrice": round(data["averagePrice"]),
                "priceRange": {"min": data["minPrice"], "max": data["maxPrice"]},
                "topBrands": list(set([item for sublist in data["brands"] for item in sublist]))[:5],
                "categories": list(set(data["categories"]))[:5]
            }
        except Exception as error:
            print(f"Search insights error: {error}")
            return {
                "totalResults": 0,
                "averagePrice": 0,
                "priceRange": {"min": 0, "max": 0},
                "topBrands": [],
                "categories": []
            }