import os
import json
from openai import OpenAI
from typing import List, Dict, Any
from app.models import Product

# Initialize OpenAI client with error handling
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    return OpenAI(api_key=api_key)

client = None

# Text normalization function with regex support
def normalize_text(text: str) -> str:
    import re
    
    # Apply regex-based normalization
    normalized = text
    
    # Notebook variations
    normalized = re.sub(r'โน้?[ดต๊]บุ๊?[คก]', 'โน้ตบุ๊ก', normalized)
    normalized = re.sub(r'โนต?บุ[๊ค]+', 'โน้ตบุ๊ก', normalized)
    normalized = re.sub(r'โน๊ตบุ[๊ค]+', 'โน้ตบุ๊ก', normalized)
    
    # Graphics card variations  
    normalized = re.sub(r'การ์[จด]อ', 'การ์ดจอ', normalized)
    normalized = re.sub(r'[วฟ]ีจีเอ', 'การ์ดจอ', normalized)
    normalized = re.sub(r'กราฟิ?[คกข]', 'การ์ดจอ', normalized)
    
    # Simple replacements
    replacements = {
        'ram': 'แรม',
        'memory': 'แรม', 
        'เม้าส์': 'เมาส์',
        'คีบอร์ด': 'คีย์บอร์ด',
        'คีบอด': 'คีย์บอร์ด',
        'cpu': 'ซีพียู'
    }
    
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    
    # Computer variations
    normalized = re.sub(r'คอมพิ?วเ?ตอร์', 'คอมพิวเตอร์', normalized)
    normalized = re.sub(r'โปรเซส[เซส]อร์', 'ซีพียู', normalized)
    
    return normalized

# Load real schema and category data
def load_real_schema_and_categories():
    """Load actual database schema and categories from files"""
    schema_data = {}
    categories_data = []
    
    # Load schema.json
    try:
        schema_paths = [
            'schema.json',
            '../schema.json', 
            '../../../schema.json',
        ]
        
        for path in schema_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
                    print(f"✅ Loaded schema from {path}")
                    break
            except FileNotFoundError:
                continue
    except Exception as e:
        print(f"Warning: Could not load schema.json: {e}")
    
    # Load navigation_attributes.json
    try:
        nav_paths = [
            'navigation_attributes.json',
            '../navigation_attributes.json', 
            '../../../navigation_attributes.json',
        ]
        
        for path in nav_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    nav_data = json.load(f)
                    categories_data = nav_data.get('cateName', [])
                    print(f"✅ Loaded {len(categories_data)} categories from {path}")
                    break
            except FileNotFoundError:
                continue
    except Exception as e:
        print(f"Warning: Could not load navigation_attributes.json: {e}")
    
    return schema_data, categories_data

# Thai-English category mapping for better understanding
def get_category_mapping() -> Dict[str, List[str]]:
    return {
        'โน้ตบุ๊ก': ['Notebooks', 'Gaming Notebooks', 'Ultrathin Notebooks', '2 in 1 Notebooks'],
        'โนตบุ๊ก': ['Notebooks', 'Gaming Notebooks', 'Ultrathin Notebooks', '2 in 1 Notebooks'], 
        'โน๊ตบุ๊ค': ['Notebooks', 'Gaming Notebooks', 'Ultrathin Notebooks', '2 in 1 Notebooks'],
        'โนคบุค': ['Notebooks', 'Gaming Notebooks', 'Ultrathin Notebooks', '2 in 1 Notebooks'],
        'การ์ดจอ': ['Graphics Cards'],
        'การ์จอ': ['Graphics Cards'],
        'กราฟิก': ['Graphics Cards'], 
        'การ์ด': ['Graphics Cards'],
        'วีจีเอ': ['Graphics Cards'],
        'คีย์บอร์ด': ['Keyboard', 'Mechanical & Gaming Keyboard', 'Wireless Keyboard'],
        'คีบอร์ด': ['Keyboard', 'Mechanical & Gaming Keyboard', 'Wireless Keyboard'],
        'คีบอด': ['Keyboard', 'Mechanical & Gaming Keyboard', 'Wireless Keyboard'], 
        'เมาส์': ['Mouse', 'Gaming Mouse', 'Wireless Mouse'],
        'เม้าส์': ['Mouse', 'Gaming Mouse', 'Wireless Mouse'],
        'จอ': ['Monitor'],
        'มอนิเตอร์': ['Monitor'],
        'จอมอนิเตอร์': ['Monitor'],
        'หน้าจอ': ['Monitor'],
        'ซีพียู': ['CPU'],
        'โปรเซสเซอร์': ['CPU'],
        'แรม': ['RAM'],
        'หน่วยความจำ': ['RAM'],
        'ความจำ': ['RAM'],
        'หูฟัง': ['Headphone', 'Headset', 'In Ear Headphone', 'True Wireless Headphone'],
        'เฮดโฟน': ['Headphone', 'Headset', 'In Ear Headphone', 'True Wireless Headphone'],
        'เฮดเซต': ['Headphone', 'Headset', 'In Ear Headphone', 'True Wireless Headphone'],
        'สปีกเกอร์': ['Speaker'],
        'คอม': ['Desktop PC', 'All in One PC (AIO)', 'Mini PC', 'Notebooks'],
        'คอมพิวเตอร์': ['Desktop PC', 'All in One PC (AIO)', 'Mini PC', 'Notebooks'],
        'เครื่อง': ['Desktop PC', 'All in One PC (AIO)', 'Mini PC', 'Notebooks'],
        'ฮาร์ดดิสก์': ['Hard Drive & Solid State Drive'],
        'ฮาร์ด': ['Hard Drive & Solid State Drive'],
        'เอสเอสดี': ['Hard Drive & Solid State Drive'],
        'ssd': ['Hard Drive & Solid State Drive']
    }

# LLM 1: Enhanced MongoDB Query Generator with Real Schema
async def generate_optimal_mongo_query_v3(user_input: str) -> Dict[str, Any]:
    normalized_input = normalize_text(user_input)
    
    # Load real schema and categories
    schema_data, categories_data = load_real_schema_and_categories()
    category_mapping = get_category_mapping()
    
    # Extract actual fields from schema
    actual_fields = []
    if schema_data and 'properties' in schema_data:
        actual_fields = list(schema_data['properties'].keys())
    
    prompt = f"""
คุณคือ MongoDB Query Expert AI ที่เชี่ยวชาญในการสร้าง Query ที่แม่นยำสำหรับร้านค้าไอที

INPUT: "{normalized_input}"

**ACTUAL DATABASE SCHEMA** (จากไฟล์จริง):
Collection: product_details
Available Fields: {actual_fields}

**KEY FIELDS TO USE:**
- title (string): ชื่อสินค้า
- description (string): รายละเอียดสินค้า  
- cateName (string): หมวดหมู่สินค้า (exact match เท่านั้น)
- price (number): ราคาปกติ
- salePrice (number): ราคาขาย (ใช้สำหรับการกรองราคา)
- stockQuantity (integer): จำนวนสต็อก (>0 = มีของ)
- rating (number): คะแนนรีวิว (0-5)
- totalReviews (integer): จำนวนรีวิว
- productView (integer): จำนวนผู้เข้าชม
- freeShipping (boolean): ส่งฟรี
- productCode (string): รหัสสินค้า
- cateId (integer): ID หมวดหมู่
- categoryId (integer): ID หมวดหมู่หลัก

**AVAILABLE CATEGORIES** (จากไฟล์จริง):
{json.dumps(categories_data, ensure_ascii=False)}

**CATEGORY MAPPING** (Thai → English):
{json.dumps(category_mapping, ensure_ascii=False, indent=2)}

**CRITICAL RULES:**
1. **NEVER use productActive field** - ไม่มีในฐานข้อมูล!
2. **Always use stockQuantity > 0** เพื่อกรองสินค้าที่มีสต็อก
3. **Use exact cateName** - ห้ามใช้ regex, ใช้ exact match หรือ $in array
4. **Use salePrice for budget** - ไม่ใช่ price
5. **Only use fields that exist** - ตรวจสอบกับ available fields
6. **Category must match exactly** - ใช้ชื่อจาก categories list เท่านั้น

**EXAMPLE CORRECT QUERIES:**

Budget + Category:
{{
  "stockQuantity": {{"$gt": 0}},
  "cateName": "Notebooks",
  "salePrice": {{"$lte": 15000}}
}}

Multiple Categories:
{{
  "stockQuantity": {{"$gt": 0}},
  "cateName": {{"$in": ["Notebooks", "Gaming Notebooks"]}},
  "salePrice": {{"$lte": 30000}}
}}

Text Search (when no exact category):
{{
  "stockQuantity": {{"$gt": 0}},
  "$or": [
    {{"title": {{"$regex": "search_term", "$options": "i"}}}},
    {{"description": {{"$regex": "search_term", "$options": "i"}}}}
  ]
}}

**BUDGET PARSING:**
- "งบ 15000" → {{"salePrice": {{"$lte": 15000}}}}
- "ไม่เกิน 20000" → {{"salePrice": {{"$lte": 20000}}}}  
- "ประมาณ 10000" → {{"salePrice": {{"$lte": 10000}}}}

ตอบในรูปแบบ JSON เท่านั้น:
{{
  "mongoQuery": {{
    "stockQuantity": {{"$gt": 0}}
    // เพิ่มเงื่อนไขอื่นที่จำเป็น (ใช้เฉพาะ fields ที่มีจริง)
  }},
  "entities": {{
    "category": "หมวดหมู่ที่ตรงที่สุด (ต้องมีใน categories list)",
    "budget": {{"min": number, "max": number}},
    "keywords": ["คำสำคัญที่สกัดได้"],
    "intent": "specific_product|category_browse|price_range|general_inquiry"
  }},
  "reasoning": "อธิบายเหตุผลการสร้าง query และการเลือก cateName",
  "confidence": 0.9
}}

**IMPORTANT:** ตรวจสอบให้แน่ใจว่าใช้เฉพาะ fields ที่มีอยู่จริงในฐานข้อมูล!
"""

    try:
        global client
        if client is None:
            client = get_openai_client()
            
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean JSON response
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
        elif content.startswith('```'):
            content = content.replace('```', '').strip()
        
        result = json.loads(content)
        
        # Validate query fields against actual schema
        query = result["mongoQuery"]
        validated_query = validate_query_fields(query, actual_fields)
        
        return {
            "query": validated_query,
            "entities": result["entities"],
            "reasoning": result.get("reasoning", "Query generated from user input"),
            "confidence": result.get("confidence", 0.8),
            "originalQuery": query,
            "validationWarnings": get_validation_warnings(query, actual_fields)
        }
    except Exception as error:
        print(f"Enhanced query generation error: {error}")
        return generate_fallback_query_v3(normalized_input, categories_data)

def validate_query_fields(query: Dict[str, Any], actual_fields: List[str]) -> Dict[str, Any]:
    """Validate and fix query fields against actual database schema"""
    validated_query = {}
    
    for key, value in query.items():
        if key in actual_fields or key in ['$or', '$and', '$nor']:
            validated_query[key] = value
        else:
            # Handle common field mapping issues
            if key == 'productActive':
                # Remove productActive - use stockQuantity > 0 instead
                print(f"[VALIDATION] Removed invalid field: {key}")
                continue
            else:
                print(f"[VALIDATION] Warning: Field '{key}' not found in schema")
                # Keep it anyway in case it's a valid MongoDB operator
                validated_query[key] = value
    
    # Ensure essential filters
    if 'stockQuantity' not in validated_query:
        validated_query['stockQuantity'] = {"$gt": 0}
    
    return validated_query

def get_validation_warnings(query: Dict[str, Any], actual_fields: List[str]) -> List[str]:
    """Get validation warnings for query"""
    warnings = []
    
    for key in query.keys():
        if key not in actual_fields and key not in ['$or', '$and', '$nor']:
            if key == 'productActive':
                warnings.append(f"Field '{key}' does not exist in database - removed")
            else:
                warnings.append(f"Field '{key}' not found in schema")
    
    return warnings

def generate_fallback_query_v3(input_text: str, categories_data: List[str]) -> Dict[str, Any]:
    """Improved fallback query generation with real schema"""
    entities = extract_entities_fallback_v3(input_text, categories_data)
    query = build_query_v3(entities)
    
    return {
        "query": query,
        "entities": entities,
        "reasoning": "Fallback query generated due to LLM parsing error",
        "confidence": 0.5,
        "originalQuery": query,
        "validationWarnings": []
    }

def extract_entities_fallback_v3(input_text: str, categories_data: List[str]) -> Dict[str, Any]:
    """Enhanced entity extraction fallback with real categories"""
    entities = {"keywords": []}
    
    # Normalize the input for better matching
    normalized_input = normalize_text(input_text.lower())
    
    # Enhanced category mapping
    category_mapping = get_category_mapping()
    
    # Find category using real categories data
    for thai_term, english_categories in category_mapping.items():
        # Check both original and normalized input
        if thai_term in input_text.lower() or thai_term in normalized_input:
            # Find the first category that exists in actual data
            for eng_cat in english_categories:
                if eng_cat in categories_data:
                    entities["category"] = eng_cat
                    entities["keywords"].append(thai_term)
                    print(f"[DEBUG] Matched '{thai_term}' → '{eng_cat}'")
                    break
            if entities.get("category"):
                break
    
    # If no exact match, try partial matching for common terms
    if not entities.get("category"):
        # Try finding partial matches
        for thai_term, english_categories in category_mapping.items():
            if len(thai_term) > 3:  # Only check longer terms
                if thai_term[:4] in normalized_input or thai_term[:3] in normalized_input:
                    for eng_cat in english_categories:
                        if eng_cat in categories_data:
                            entities["category"] = eng_cat
                            entities["keywords"].append(thai_term)
                            print(f"[DEBUG] Partial match '{thai_term}' → '{eng_cat}'")
                            break
                    if entities.get("category"):
                        break
    
    # Extract budget with better parsing
    import re
    budget_patterns = [
        r'งบ\s*(\d{1,3}(?:,\d{3})*)', 
        r'ไม่เกิน\s*(\d{1,3}(?:,\d{3})*)',
        r'ประมาณ\s*(\d{1,3}(?:,\d{3})*)',
        r'ราคา\s*(\d{1,3}(?:,\d{3})*)',
        r'(\d{1,3}(?:,\d{3})*)\s*บาท',
        r'(\d{1,3}(?:,\d{3})*)'  # จับตัวเลขทั่วไป
    ]
    
    for pattern in budget_patterns:
        matches = re.findall(pattern, input_text)
        if matches:
            budget = int(matches[0].replace(',', ''))
            if budget >= 1000:  # Reasonable minimum
                entities["budget"] = {"max": budget}
                break
    
    # Extract usage intent
    usage_keywords = {
        'เล่นเกม': 'Gaming',
        'เกม': 'Gaming', 
        'ทำงาน': 'Office',
        'งาน': 'Office',
        'เรียน': 'Student',
        'กราฟิก': 'Creative',
        'วิดีโอ': 'Creative'
    }
    
    for keyword, usage in usage_keywords.items():
        if keyword in input_text:
            entities["usage"] = usage
            entities["keywords"].append(keyword)
            break
    
    entities["keywords"].append(input_text)
    entities["intent"] = "category_browse" if entities.get("category") else "general_inquiry"
    
    return entities

def build_query_v3(entities: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced query building with real schema validation"""
    query = {
        "stockQuantity": {"$gt": 0}
    }
    
    # Category filter (exact match only)
    if entities.get("category"):
        query["cateName"] = entities["category"]
    
    # Budget filter (use salePrice)
    if entities.get("budget", {}).get("max"):
        budget = entities["budget"]
        query["salePrice"] = {"$lte": budget["max"]}
        if budget.get("min"):
            query["salePrice"]["$gte"] = budget["min"]
    
    # If no specific category but have keywords, use text search
    if not entities.get("category") and entities.get("keywords"):
        keywords = entities["keywords"]
        if len(keywords) > 0:
            # Create regex pattern for flexible text search
            search_terms = [kw for kw in keywords if len(kw) > 1]
            if search_terms:
                query["$or"] = [
                    {"title": {"$regex": "|".join(search_terms), "$options": "i"}},
                    {"description": {"$regex": "|".join(search_terms), "$options": "i"}}
                ]
    
    return query

# Export the new functions (keeping original names for compatibility)
generate_optimal_mongo_query_v2 = generate_optimal_mongo_query_v3
filter_and_rank_products_v2 = None  # Will import from improved version
generate_natural_product_recommendation_v2 = None  # Will import from improved version