from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any, Optional
from app.models import Product, ExtractedEntities
from app.services.two_stage_llm import (
    stage1_context_analysis_and_query_builder,
    stage2_content_analyzer,
    stage3_question_answerer,
    generate_two_stage_response,
    normalize_text_advanced,
    extract_question_phrases
)
from app.services.conversation_manager import (
    conversation_memory,
    input_consolidator
)
from app.services.spec_comparison_manager import (
    spec_manager,
    comparison_manager,
    troubleshooting_manager
)

class ITStoreChatbot:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["products"]  # Fixed to use correct collection name
    
    async def process_user_input(self, user_input: str, session_id: str = "default"):
        try:
            # 1. Check for input consolidation (handle multiple messages)
            should_consolidate = input_consolidator.should_consolidate(session_id, user_input)
            if should_consolidate:
                consolidated_input = input_consolidator.consolidate_input(session_id, user_input)
                print(f"[Consolidated] '{user_input}' + previous → '{consolidated_input}'")
                user_input = consolidated_input
            
            # 2. Get conversation context
            conversation_context = conversation_memory.get_context(session_id)
            recent_messages = conversation_memory.get_recent_messages(session_id, 3)
            
            # 3. Check for advanced question types first
            spec_request = spec_manager.detect_spec_request(user_input)
            comparison_request = comparison_manager.detect_comparison_request(user_input) 
            trouble_request = troubleshooting_manager.detect_troubleshooting_request(user_input)
            
            # 4. Normalize text with advanced Thai language processing
            normalized_input = normalize_text_advanced(user_input)
            
            # 5. Stage 1: Context analysis and query building for initial filtering
            stage1_result = await stage1_context_analysis_and_query_builder(user_input)
            
            # 6. Search products with Stage 1 query
            raw_products = await self.search_products_precise(stage1_result["query"])
            
            # 7. If no results, try progressive fallback
            if len(raw_products) == 0:
                raw_products = await self.search_with_fallback_two_stage(
                    stage1_result["processedTerms"], 
                    stage1_result["query"]
                )
            
            # 8. Stage 2: Deep content analysis and product matching
            filtered_products = await stage2_content_analyzer(
                user_input,
                stage1_result,
                raw_products
            )
            
            # 9. Stage 3: Enhanced question answering with conversation context
            stage_assignments = stage1_result.get("stageAssignments", {})
            question_phrases = stage_assignments.get("stage3_questions", [])
            stage3_answer = ""
            
            print(f"[Main] Stage 3 question phrases: {question_phrases}")
            print(f"[Main] Advanced requests: spec={bool(spec_request)}, comparison={bool(comparison_request)}, trouble={bool(trouble_request)}")
            
            # Enhanced Stage 3 with conversation context
            if question_phrases or spec_request or comparison_request or trouble_request:
                stage3_answer = await stage3_question_answerer(
                    user_input,
                    stage1_result,
                    filtered_products,
                    question_phrases,
                    conversation_context
                )
            
            # 10. Generate comprehensive response (now three-stage)
            response = await generate_two_stage_response(
                user_input,
                stage1_result,
                filtered_products
            )
            
            # Append Stage 3 answer if available
            if stage3_answer:
                response += f"\n\n**💬 คำตอบเพิ่มเติม:**\n{stage3_answer}"
            
            # 11. Store conversation in memory
            conversation_memory.add_message(
                session_id=session_id,
                user_input=user_input,
                bot_response=response,
                query_type=stage1_result.get("queryType", "unknown"),
                categories=stage1_result.get("processedTerms", {}).get("categories", []),
                budget=stage1_result.get("processedTerms", {}).get("budget")
            )
            
            # 12. Determine query method for response
            query_method = "three_stage_llm"
            if spec_request:
                query_method = "spec_building"
            elif comparison_request:
                query_method = "comparison"  
            elif trouble_request:
                query_method = "troubleshooting"
            
            return {
                "products": filtered_products,
                "response": response,
                "reasoning": self.explain_three_stage_selection(stage1_result, filtered_products, question_phrases, stage3_answer),
                "stage1": stage1_result,
                "stage3Questions": question_phrases,
                "stage3Answer": stage3_answer,
                "queryReasoning": stage1_result["reasoning"],
                "mongoQuery": stage1_result["query"],
                "confidence": stage1_result.get("confidence", 0.8),
                "rawProductCount": len(raw_products),
                "filteredProductCount": len(filtered_products),
                "searchMethod": query_method,
                "conversationContext": {
                    "session_id": session_id,
                    "consolidated_input": user_input if should_consolidate else None,
                    "recent_messages_count": len(recent_messages)
                },
                "advancedRequests": {
                    "spec_building": bool(spec_request),
                    "comparison": bool(comparison_request), 
                    "troubleshooting": bool(trouble_request)
                }
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
    
    def explain_three_stage_selection(self, stage1_result: Dict[str, Any], products: List[Product], question_phrases: List[str], stage3_answer: str) -> str:
        """Explain three-stage selection process"""
        if len(products) == 0:
            return None
        
        top_product = products[0]
        processed_terms = stage1_result.get("processedTerms", {})
        used_terms = processed_terms.get("used", [])
        remaining_terms = processed_terms.get("remaining", [])
        
        reasoning = f"💭 **Three-Stage Analysis - \"{top_product.title}\":**\n"
        
        reasons = []
        
        # Stage 1 filtering info
        if used_terms:
            reasons.append(f"🔍 Stage 1 กรอง: {', '.join(used_terms)}")
        
        # Stage 2 analysis info
        non_question_remaining = [t for t in remaining_terms if t not in question_phrases]
        if non_question_remaining:
            reasons.append(f"🎯 Stage 2 วิเคราะห์: {', '.join(non_question_remaining)}")
        
        # Stage 3 question answering
        if question_phrases:
            reasons.append(f"💬 Stage 3 ตอบคำถาม: {', '.join(question_phrases)}")
        
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