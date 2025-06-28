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

# LLM 1: Simple Query Generator (NO description regex)
async def generate_simple_mongo_query(user_input: str) -> Dict[str, Any]:
    """
    LLM1: Generate simple, clean MongoDB queries for basic filtering only
    NO description regex - focus only on category, price, and basic fields
    """
    normalized_input = normalize_text(user_input)
    
    # Load real schema and categories
    schema_data, categories_data = load_real_schema_and_categories()
    category_mapping = get_category_mapping()
    
    # Extract actual fields from schema
    actual_fields = []
    if schema_data and 'properties' in schema_data:
        actual_fields = list(schema_data['properties'].keys())
    
    prompt = f"""
คุณคือ MongoDB Query Generator ที่เชี่ยวชาญในการสร้าง Query อย่างง่ายและแม่นยำ

INPUT: "{normalized_input}"

**DATABASE SCHEMA** (fields ที่มีจริง):
{actual_fields}

**AVAILABLE CATEGORIES** (ต้องใช้ชื่อเหล่านี้เท่านั้น):
{json.dumps(categories_data, ensure_ascii=False)}

**CATEGORY MAPPING** (Thai → English):
{json.dumps(category_mapping, ensure_ascii=False, indent=2)}

**CRITICAL RULES - LLM1:**
1. **SIMPLE QUERIES ONLY** - สร้าง query ง่ายๆ สำหรับกรองพื้นฐานเท่านั้น
2. **NO DESCRIPTION REGEX** - ห้ามใช้ description ใน query เด็ดขาด
3. **NO TITLE REGEX** - ห้ามใช้ title regex เด็ดขาด  
4. **BASIC FILTERS ONLY**: stockQuantity, cateName, salePrice เท่านั้น
5. **EXACT CATEGORY MATCH** - ใช้ cateName exact match หรือ $in array
6. **USE REAL FIELDS** - ใช้เฉพาะ fields ที่มีจริงเท่านั้น
7. **ALWAYS stockQuantity > 0** - กรองสินค้าที่มีสต็อกเสมอ

**EXAMPLE SIMPLE QUERIES:**

Basic Category + Budget:
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

Category Only (no budget):
{{
  "stockQuantity": {{"$gt": 0}},
  "cateName": "Graphics Cards"
}}

**หลักการ:**
- ถ้ามี category → ใช้ cateName
- ถ้ามี budget → ใช้ salePrice
- ถ้าไม่มี category ชัดเจน → ใช้ stockQuantity อย่างเดียว
- **ห้ามใช้ $or, $regex ใน title/description**

ตอบใน JSON:
{{
  "mongoQuery": {{
    "stockQuantity": {{"$gt": 0}}
    // เพิ่มเฉพาะ cateName และ salePrice ถ้าจำเป็น
  }},
  "entities": {{
    "category": "หมวดหมู่ที่แน่ใจ (จาก categories list)",
    "budget": {{"max": number}},
    "complexity": "simple|complex",
    "intent": "basic_browse|specific_product"
  }},
  "reasoning": "อธิบายว่าทำไมเลือก query นี้"
}}

**สำคัญ:** LLM1 ทำหน้าที่กรองพื้นฐานเท่านั้น ไม่ต้องเจาะลึก!
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
        validated_query = validate_query_fields_simple(query, actual_fields)
        
        return {
            "query": validated_query,
            "entities": result["entities"],
            "reasoning": result.get("reasoning", "Simple query generated"),
            "confidence": 0.8
        }
    except Exception as error:
        print(f"Simple query generation error: {error}")
        return generate_fallback_query_simple(normalized_input, categories_data)

def validate_query_fields_simple(query: Dict[str, Any], actual_fields: List[str]) -> Dict[str, Any]:
    """Validate and ensure simple query structure"""
    validated_query = {"stockQuantity": {"$gt": 0}}
    
    # Only allow basic fields
    allowed_fields = ['stockQuantity', 'cateName', 'salePrice', 'cateId', 'categoryId']
    
    for key, value in query.items():
        if key in allowed_fields and key in actual_fields:
            validated_query[key] = value
        elif key == 'stockQuantity':  # Always keep this
            validated_query[key] = value
    
    return validated_query

def generate_fallback_query_simple(input_text: str, categories_data: List[str]) -> Dict[str, Any]:
    """Simple fallback query generation"""
    entities = extract_entities_simple(input_text, categories_data)
    query = build_simple_query(entities)
    
    return {
        "query": query,
        "entities": entities,
        "reasoning": "Simple fallback query generated",
        "confidence": 0.6
    }

def extract_entities_simple(input_text: str, categories_data: List[str]) -> Dict[str, Any]:
    """Simple entity extraction for basic queries"""
    entities = {"complexity": "simple", "intent": "basic_browse"}
    
    # Normalize the input for better matching
    normalized_input = normalize_text(input_text.lower())
    
    # Enhanced category mapping
    category_mapping = get_category_mapping()
    
    # Find category using real categories data
    for thai_term, english_categories in category_mapping.items():
        if thai_term in input_text.lower() or thai_term in normalized_input:
            for eng_cat in english_categories:
                if eng_cat in categories_data:
                    entities["category"] = eng_cat
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
        r'(\d{1,3}(?:,\d{3})*)'
    ]
    
    for pattern in budget_patterns:
        matches = re.findall(pattern, input_text)
        if matches:
            budget = int(matches[0].replace(',', ''))
            if budget >= 1000:
                entities["budget"] = {"max": budget}
                break
    
    # Analyze complexity
    complex_keywords = [
        'ทำงาน', 'เล่นเกม', 'เกม', 'gaming', 'office', 'work',
        'photoshop', 'video', 'streaming', 'design', 'program',
        'excel', 'powerpoint', 'autocad', 'valorant', 'pubg',
        'รีสอร์ส', 'สเปค', 'performance', 'fps', 'render'
    ]
    
    if any(keyword in input_text.lower() for keyword in complex_keywords):
        entities["complexity"] = "complex"
        entities["intent"] = "specific_product"
    
    return entities

def build_simple_query(entities: Dict[str, Any]) -> Dict[str, Any]:
    """Build simple query with basic filters only"""
    query = {"stockQuantity": {"$gt": 0}}
    
    # Category filter (exact match only)
    if entities.get("category"):
        query["cateName"] = entities["category"]
    
    # Budget filter (use salePrice)
    if entities.get("budget", {}).get("max"):
        budget = entities["budget"]
        query["salePrice"] = {"$lte": budget["max"]}
    
    return query

# LLM 2: Intelligent Product Analyzer and Ranker
async def analyze_and_rank_products_advanced(
    user_input: str,
    entities: Dict[str, Any],
    products: List[Product],
    mongo_query: Dict[str, Any] = None
) -> List[Product]:
    """
    LLM2: Intelligent analysis of products based on user intent
    Analyzes description, title, specs, and other fields to match user needs
    """
    if len(products) == 0:
        return []
    
    # Check complexity from LLM1
    complexity = entities.get("complexity", "simple")
    
    if complexity == "simple":
        # For simple queries, just sort by popularity and rating
        print(f"[LLM2] Simple query detected - using basic sorting")
        return sorted(products, 
                     key=lambda p: (p.productView, p.rating, -p.salePrice), 
                     reverse=True)[:8]
    
    # For complex queries, use LLM2 analysis
    print(f"[LLM2] Complex query detected - analyzing {len(products)} products")
    
    products_info = ""
    for i, p in enumerate(products[:10]):  # Reduced from 15 to 10 to save tokens
        discount = p.price - p.salePrice
        discount_text = ""
        if discount > 0:
            discount_percent = round((discount / p.price) * 100)
            discount_text = f" (ลด {discount_percent}%)"
        
        # Optimized fields - only essential info for LLM2 analysis
        products_info += f"""
Product {i + 1}:
Title: {p.title}
Description: {p.description[:150]}...
Category: {p.cateName}
Price: ฿{p.salePrice:,}{discount_text}
Rating: {p.rating}/5 ({p.totalReviews})
Views: {p.productView:,}
Stock: {p.stockQuantity}
"""
    
    prompt = f"""
คุณคือ Product Analysis Expert ที่เชี่ยวชาญในการวิเคราะห์สินค้าไอทีให้ตรงกับความต้องการของลูกค้า

**USER INPUT:** "{user_input}"

**USER REQUIREMENTS ANALYSIS:**
- หมวดหมู่: {entities.get('category', 'ไม่ระบุ')}
- งบประมาณ: {entities.get('budget', 'ไม่ระบุ')}
- ความซับซ้อน: {entities.get('complexity', 'simple')}
- Intent: {entities.get('intent', 'basic_browse')}

**PRODUCTS TO ANALYZE:**
{products_info}

**ANALYSIS MISSION:**
1. **เข้าใจ User Intent** - วิเคราะห์ความต้องการจริงๆ จาก input
2. **Analyze Product Descriptions** - อ่าน description ของแต่ละสินค้าอย่างละเอียด
3. **Analyze Titles** - ดูสเปคและข้อมูลใน title
4. **Match Requirements** - จับคู่สินค้าที่ตรงกับความต้องการ
5. **Score Products** - ให้คะแนน 0-100 ตามความเหมาะสม
6. **Consider All Factors** - ราคา, rating, ความนิยม, โปรโมชั่น

**SCORING CRITERIA:**
- Requirement Match (50%): ตรงกับความต้องการหรือไม่
- Value for Money (20%): คุณภาพต่อราคา
- Popularity (15%): rating และ reviews
- Availability (10%): stock และ shipping
- Promotions (5%): ส่วนลดและสิทธิพิเศษ

**ตัวอย่างการวิเคราะห์:**
- "โน้ตบุ๊คทำงาน excel" → ต้องการ CPU ดี, RAM เพียงพอ, ไม่จำเป็นต้องเล่นเกม
- "โน้ตบุ๊คเล่นเกม valorant" → ต้องการ GPU ดี, RAM สูง, CPU gaming
- "โน้ตบุ๊คงบ 15000" → ความคุ้มค่าในราคา, ไม่ซับซ้อน

ตอบใน JSON:
{{
  "selected_products": [
    {{
      "index": 0,
      "score": 95,
      "reasoning": "เหตุผลที่เลือกสินค้าชิ้นนี้"
    }},
    {{
      "index": 2,
      "score": 87,
      "reasoning": "เหตุผลที่เลือกสินค้าชิ้นนี้"
    }}
  ],
  "analysis_summary": "สรุปการวิเคราะห์โดยรวม",
  "recommendations": "คำแนะนำเพิ่มเติม"
}}

**สำคัญ:** วิเคราะห์ description อย่างละเอียดเพื่อหาสิ่งที่ user ต้องการจริงๆ
"""

    try:
        global client
        if client is None:
            client = get_openai_client()
            
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean JSON response
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
        elif content.startswith('```'):
            content = content.replace('```', '').strip()
        
        result = json.loads(content)
        selected_products_data = result.get("selected_products", [])
        
        # Build filtered and ranked products list
        filtered_products = []
        for item in selected_products_data:
            idx = item.get("index", -1)
            if 0 <= idx < len(products):
                filtered_products.append(products[idx])
        
        print(f"[LLM2] Selected {len(filtered_products)} products from {len(products)}")
        return filtered_products[:8]  # Limit to top 8
        
    except Exception as error:
        print(f"Product analysis error: {error}")
        # Fallback: return products sorted by popularity and rating
        return sorted(products, 
                     key=lambda p: (p.productView, p.rating, -p.salePrice), 
                     reverse=True)[:8]

# Enhanced natural language response generation
async def generate_natural_response_advanced(
    user_input: str,
    entities: Dict[str, Any],
    products: List[Product],
    llm1_reasoning: str,
    mongo_query: Dict[str, Any] = None
) -> str:
    """Generate natural language response with LLM1 query transparency"""
    if len(products) == 0:
        return await generate_no_results_response_advanced(user_input, entities, mongo_query)

    top_products = products[:3]
    total_results = len(products) 
    complexity = entities.get("complexity", "simple")
    
    products_info = ""
    for i, p in enumerate(top_products):
        discount = p.price - p.salePrice
        discount_text = ""
        if discount > 0:
            discount_percent = round((discount / p.price) * 100)
            discount_text = f" (ลด {discount_percent}% จาก ฿{p.price:,})"
        
        products_info += f"""
{i + 1}. {p.title}
   - ราคา: ฿{p.salePrice:,}{discount_text}
   - คะแนน: {p.rating}/5 ({p.totalReviews} รีวิว)
   - ยอดนิยม: {p.productView:,} ครั้งเข้าชม
   - สต็อก: {p.stockQuantity} ชิ้น
   - หมวด: {p.cateName or 'N/A'}
   - ส่งฟรี: {'✅' if p.freeShipping else '❌'}"""
    
    prompt = f"""
คุณคือ Professional IT Sales Assistant ที่เชี่ยวชาญในการแนะนำสินค้าไอที

User Input: "{user_input}"

Query Strategy Used (LLM1):
```json
{json.dumps(mongo_query, ensure_ascii=False, indent=2) if mongo_query else "ไม่มีข้อมูล"}
```

LLM1 Reasoning: {llm1_reasoning}

Analysis Method: {"Complex Analysis (LLM2)" if complexity == "complex" else "Simple Sorting"}
Total Results: {total_results} รายการ

Top Products:{products_info}

User Context:
- หมวดหมู่: {entities.get('category', 'ไม่ระบุ')}
- งบประมาณ: {entities.get('budget', 'ไม่ระบุ')}
- ความซับซ้อน: {entities.get('complexity', 'simple')}
- Intent: {entities.get('intent', 'basic_browse')}

**Instructions:**
1. สร้างการแนะนำที่เป็นธรรมชาติ เหมือนพนักงานขายมืออาชีพ
2. อธิบายว่าทำไมแนะนำสินค้านี้ (highlight key selling points)
3. เปรียบเทียบตัวเลือกหากมีหลายตัว
4. ระบุข้อดี: ราคา, คะแนน, ความนิยม, ส่วนลด, สต็อก
5. ใช้ emoji เพื่อให้น่าสนใจ แต่ไม่มากเกินไป
6. **แสดง MongoDB Query ในส่วนท้าย เพื่อความโปร่งใส (สำหรับ development)**
7. อธิบายกลยุทธ์การค้นหาที่ใช้ (Simple vs Complex)

สร้างการแนะนำที่เป็นธรรมชาติ เป็นกันเอง และมีประโยชน์!
"""

    try:
        global client
        if client is None:
            client = get_openai_client()
            
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        
        return response.choices[0].message.content.strip()
    except Exception as error:
        print(f"Response generation error: {error}")
        return generate_fallback_response_advanced(user_input, products, mongo_query, complexity)

async def generate_no_results_response_advanced(user_input: str, entities: Dict[str, Any], mongo_query: Dict[str, Any] = None) -> str:
    """Enhanced no results response with query transparency"""
    category = entities.get('category', 'ไม่ระบุ')
    budget = entities.get('budget', {})
    complexity = entities.get('complexity', 'simple')
    
    response = "ขออภัย ไม่พบสินค้าที่ตรงกับความต้องการของคุณ 🔍\n\n"
    
    if category != 'ไม่ระบุ':
        response += f"🏷️ หมวด: {category}\n"
    if budget.get('max'):
        response += f"💰 งบประมาณ: ฿{budget['max']:,}\n"
    if complexity == "complex":
        response += f"🎯 ความต้องการ: ซับซ้อน (ใช้ LLM2 analysis)\n"
    else:
        response += f"🎯 ความต้องการ: ทั่วไป (ใช้ basic sorting)\n"
    
    response += "\n💡 ข้อเสนอแนะ:\n"
    response += "• ลองเพิ่มงบประมาณ\n"
    response += "• ค้นหาด้วยชื่อสินค้าโดยตรง\n"
    response += "• ระบุความต้องการให้ชัดเจนมากขึ้น\n"
    response += "• ลองหมวดหมู่ที่เกี่ยวข้อง\n\n"
    
    # Add query transparency
    response += f"🔧 **Debug Info - Query Strategy:**\n"
    response += f"```json\n{json.dumps(mongo_query, ensure_ascii=False, indent=2) if mongo_query else 'ไม่มีข้อมูล'}\n```"
    
    return response

def generate_fallback_response_advanced(user_input: str, products: List[Product], mongo_query: Dict[str, Any] = None, complexity: str = "simple") -> str:
    """Enhanced fallback response with strategy explanation"""
    if len(products) == 0:
        return f"ไม่พบสินค้าจาก query: {user_input} 🔍"
    
    top_product = products[0]
    total_results = len(products)
    
    response = f"พบสินค้าที่ตรงกับความต้องการ {total_results} รายการ 🛍️\n\n"
    response += f"⭐ **แนะนำ:** {top_product.title}\n"
    response += f"💰 **ราคา:** ฿{top_product.salePrice:,}"
    
    discount = top_product.price - top_product.salePrice
    if discount > 0:
        discount_percent = round((discount / top_product.price) * 100)
        response += f" (ลด {discount_percent}% จาก ฿{top_product.price:,})"
    
    response += f"\n📦 **คงเหลือ:** {top_product.stockQuantity} ชิ้น"
    response += f"\n⭐ **คะแนน:** {top_product.rating}/5 ({top_product.totalReviews} รีวิว)"
    response += f"\n🔥 **ยอดนิยม:** {top_product.productView:,} ครั้งเข้าชม"
    
    if top_product.freeShipping:
        response += "\n🚚 **ส่งฟรี**"
    
    if total_results > 1:
        response += f"\n\n📋 มีทั้งหมด {total_results} รายการให้เลือก!"
    
    # Add strategy explanation
    strategy = "Complex Analysis (LLM2)" if complexity == "complex" else "Simple Sorting"
    response += f"\n\n🎯 **Search Strategy:** {strategy}"
    
    # Add debug info
    response += f"\n\n🔧 **Debug - MongoDB Query:**\n```json\n{json.dumps(mongo_query, ensure_ascii=False, indent=2) if mongo_query else 'ไม่มีข้อมูล'}\n```"
    
    return response

# Export functions with backwards compatibility
generate_optimal_mongo_query_v2 = generate_simple_mongo_query
filter_and_rank_products_v2 = analyze_and_rank_products_advanced
generate_natural_product_recommendation_v2 = generate_natural_response_advanced