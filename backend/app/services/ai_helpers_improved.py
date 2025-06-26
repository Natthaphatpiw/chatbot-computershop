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

# Text normalization function
def normalize_text(text: str) -> str:
    return text.replace('โน้?[ดต๊]บุ๊?[คก]', 'โน้ตบุ๊ก') \
               .replace('การ์[จด]อ', 'การ์ดจอ') \
               .replace('[วฟ]ีจีเอ', 'การ์ดจอ') \
               .replace('กราฟิ?[คกข]', 'การ์ดจอ') \
               .replace('แรม', 'แรม') \
               .replace('ram', 'แรม') \
               .replace('memory', 'แรม') \
               .replace('หน่วยความจำ', 'แรม') \
               .replace('คอมพิ?วเ?ตอร์', 'คอมพิวเตอร์') \
               .replace('เม้าส์', 'เมาส์') \
               .replace('คีบอร์ด', 'คีย์บอร์ด') \
               .replace('คีบอด', 'คีย์บอร์ด') \
               .replace('ซีพียู', 'ซีพียู') \
               .replace('cpu', 'ซีพียู') \
               .replace('โปรเซส[เซส]อร์', 'ซีพียู')

# Load category data from navigation_attributes.json  
def load_categories() -> List[str]:
    try:
        # Try multiple possible locations
        possible_paths = [
            'navigation_attributes.json',
            '../navigation_attributes.json', 
            '../../../navigation_attributes.json',
            os.path.join(os.path.dirname(__file__), '../../../../navigation_attributes.json')
        ]
        
        for nav_file in possible_paths:
            try:
                with open(nav_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    categories = data.get('cateName', [])
                    print(f"✅ Loaded {len(categories)} categories from {nav_file}")
                    return categories
            except FileNotFoundError:
                continue
        
        # If no file found, use fallback
        raise FileNotFoundError("navigation_attributes.json not found in any location")
        
    except Exception as e:
        print(f"Warning: Could not load navigation_attributes.json: {e}")
        # Fallback categories based on actual data
        return [
            "Notebooks", "Gaming Notebooks", "Ultrathin Notebooks", "2 in 1 Notebooks",
            "Desktop PC", "All in One PC (AIO)", "Mini PC",
            "CPU", "Graphics Cards", "RAM", "Mainboards", "Case & Power Supply",
            "Keyboard", "Mouse", "Gaming Mouse", "Mechanical & Gaming Keyboard", "Wireless Keyboard", "Wireless Mouse",
            "Monitor", "Headphone", "Headset", "Speaker", "In Ear Headphone", "True Wireless Headphone",
            "Hard Drive & Solid State Drive", "External & Portable Drive", "Memory Card", "NAS Storage"
        ]

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

# LLM 1: Enhanced MongoDB Query Generator  
async def generate_optimal_mongo_query_v2(user_input: str) -> Dict[str, Any]:
    normalized_input = normalize_text(user_input)
    categories = load_categories()
    category_mapping = get_category_mapping()
    
    prompt = f"""
คุณคือ MongoDB Query Expert AI ที่เชี่ยวชาญในการสร้าง Query ที่แม่นยำสำหรับร้านค้าไอที

INPUT: "{normalized_input}"

Database Schema (MongoDB Collection: products):
- title (string): ชื่อสินค้า
- description (string): รายละเอียดสินค้า  
- cateName (string): หมวดหมู่สินค้า (exact match จากรายการด้านล่าง)
- price (number): ราคาปกติ
- salePrice (number): ราคาขาย (ใช้สำหรับการกรองราคา)
- stockQuantity (integer): จำนวนสต็อก
- productActive (boolean): สถานะเปิดขาย
- rating (number): คะแนนรีวิว
- totalReviews (integer): จำนวนรีวิว
- productView (integer): จำนวนผู้เข้าชม
- freeShipping (boolean): ส่งฟรี
- product_warranty_2_year, product_warranty_3_year (string/null): การรับประกัน

หมวดหมู่สินค้า (cateName) ที่มีในระบบ:
{', '.join(categories)}

การแมปคำไทย-อังกฤษ:
{json.dumps(category_mapping, ensure_ascii=False, indent=2)}

หลักการสร้าง Query:
1. **ฟิลเตอร์พื้นฐาน**: ต้องมี stockQuantity > 0 และ productActive = true เสมอ
2. **หมวดหมู่**: ใช้ cateName แบบ exact match หรือ $in array สำหรับหลายหมวด
3. **ราคา**: ใช้ salePrice สำหรับการกรอง (ไม่ใช่ price)  
4. **คำค้นหา**: หากไม่พบหมวดหมู่ที่ตรง ให้ใช้ $regex ใน title, description
5. **งบประมาณ**: จับคำว่า "งบ", "ไม่เกิน", "ประมาณ", "ต่ำกว่า" แล้วแปลงเป็น salePrice filter

ตัวอย่าง Query ที่ถูกต้อง:
{{
  "stockQuantity": {{"$gt": 0}},
  "productActive": true,
  "cateName": "Notebooks",
  "salePrice": {{"$lte": 15000}}
}}

ตอบในรูปแบบ JSON:
{{
  "mongoQuery": {{
    "stockQuantity": {{"$gt": 0}},
    "productActive": true
    // เพิ่ม conditions อื่นๆ ตาม input
  }},
  "entities": {{
    "category": "หมวดหมู่หลักที่แม่นยำ",
    "budget": {{"min": number, "max": number}},
    "keywords": ["คำสำคัญที่สกัดได้"],
    "intent": "specific_product|category_browse|price_range|general_inquiry"
  }},
  "reasoning": "อธิบายเหตุผลการสร้าง query นี้",
  "confidence": 0.9
}}

ตอบเฉพาะ JSON เท่านั้น
"""

    try:
        global client
        if client is None:
            client = get_openai_client()
            
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
        
        return {
            "query": result["mongoQuery"],
            "entities": result["entities"],
            "reasoning": result.get("reasoning", "Query generated from user input"),
            "confidence": result.get("confidence", 0.8)
        }
    except Exception as error:
        print(f"Enhanced query generation error: {error}")
        return generate_fallback_query_v2(normalized_input)

def generate_fallback_query_v2(input_text: str) -> Dict[str, Any]:
    """Improved fallback query generation"""
    entities = extract_entities_fallback_v2(input_text)
    query = build_query_v2(entities)
    
    return {
        "query": query,
        "entities": entities,
        "reasoning": "Fallback query generated due to LLM parsing error",
        "confidence": 0.5
    }

def extract_entities_fallback_v2(input_text: str) -> Dict[str, Any]:
    """Enhanced entity extraction fallback"""
    entities = {"keywords": []}
    
    # Enhanced category mapping
    category_mapping = get_category_mapping()
    
    # Find category
    for thai_term, english_categories in category_mapping.items():
        if thai_term in input_text.lower():
            entities["category"] = english_categories[0]  # Use primary category
            entities["keywords"].append(thai_term)
            break
    
    # Extract budget with better parsing
    import re
    budget_patterns = [
        r'งบ\s*(\d{1,3}(?:,\d{3})*)', 
        r'ไม่เกิน\s*(\d{1,3}(?:,\d{3})*)',
        r'ประมาณ\s*(\d{1,3}(?:,\d{3})*)',
        r'ราคา\s*(\d{1,3}(?:,\d{3})*)',
        r'(\d{1,3}(?:,\d{3})*)\s*บาท'
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

def build_query_v2(entities: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced query building"""
    query = {
        "stockQuantity": {"$gt": 0},
        "productActive": True
    }
    
    # Category filter
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

# LLM 2: Enhanced Product Result Filtering and Ranking
async def filter_and_rank_products_v2(
    user_input: str,
    entities: Dict[str, Any], 
    products: List[Product],
    mongo_query: Dict[str, Any] = None
) -> List[Product]:
    """
    LLM 2: Intelligently filter and rank products based on user intent
    """
    if len(products) == 0:
        return []
        
    if len(products) <= 3:
        return products  # No need to filter if already few results
    
    products_info = ""
    for i, p in enumerate(products[:10]):  # Analyze top 10
        products_info += f"""
{i + 1}. {p.title}
   - ราคา: ฿{p.salePrice:,}
   - หมวด: {p.cateName or 'N/A'}
   - คะแนน: {p.rating}/5 ({p.totalReviews} รีวิว)
   - ยอดนิยม: {p.productView:,} ครั้ง
   - คำอธิบาย: {p.description[:100]}...
   - สต็อก: {p.stockQuantity}"""
    
    prompt = f"""
คุณคือ Product Ranking Expert AI ที่เชี่ยวชาญในการคัดกรองและเรียงลำดับสินค้า

User Input: "{user_input}"
User Intent Analysis:
- หมวดหมู่: {entities.get('category', 'ไม่ระบุ')}
- งบประมาณ: {entities.get('budget', 'ไม่ระบุ')}
- การใช้งาน: {entities.get('usage', 'ไม่ระบุ')}
- คำสำคัญ: {', '.join(entities.get('keywords', []))}

MongoDB Query ที่ใช้:
{json.dumps(mongo_query, ensure_ascii=False, indent=2) if mongo_query else "ไม่มีข้อมูล"}

สินค้าที่พบ ({len(products)} รายการ):{products_info}

**ภารกิจ:**
1. วิเคราะห์ User Input ให้เข้าใจความต้องการจริงๆ
2. ให้คะแนนแต่ละสินค้าตาม relevance กับ User Input (0-100)
3. พิจารณาปัจจัย: ความตรงกับหมวดหมู่, ราคา, คุณสมบัติ, ความนิยม, คะแนนรีวิว
4. คัดกรองเฉพาะสินค้าที่ score >= 70 หรือสินค้าที่เหมาะสมจริงๆ
5. เรียงลำดับตาม relevance แล้วตาม popularity

ตอบในรูปแบบ JSON Array ของ product indices ที่ควรแสดง:
{{
  "selected_indices": [0, 2, 5],  // indices ของสินค้าที่คัดเลือก (เรียงตาม relevance)
  "reasoning": {{
    "0": "เหตุผลที่เลือกสินค้าชิ้นที่ 1",
    "2": "เหตุผลที่เลือกสินค้าชิ้นที่ 3", 
    "5": "เหตุผลที่เลือกสินค้าชิ้นที่ 6"
  }},
  "summary": "สรุปการคัดเลือกโดยรวม"
}}

ตอบเฉพาะ JSON เท่านั้น
"""

    try:
        global client
        if client is None:
            client = get_openai_client()
            
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
        selected_indices = result.get("selected_indices", [])
        
        # Return filtered and ranked products
        filtered_products = []
        for idx in selected_indices:
            if 0 <= idx < len(products):
                filtered_products.append(products[idx])
        
        return filtered_products[:8]  # Limit to top 8
        
    except Exception as error:
        print(f"Product filtering error: {error}")
        # Fallback: return products sorted by popularity and rating
        return sorted(products, 
                     key=lambda p: (p.productView, p.rating, -p.salePrice), 
                     reverse=True)[:8]

# Enhanced natural language response generation
async def generate_natural_product_recommendation_v2(
    user_input: str,
    entities: Dict[str, Any],
    products: List[Product],
    search_reasoning: str,
    mongo_query: Dict[str, Any] = None
) -> str:
    """Enhanced response generation with better product presentation"""
    if len(products) == 0:
        return await generate_no_results_response_v2(user_input, entities)

    top_products = products[:3]
    total_results = len(products) 
    
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
Search Query ที่ใช้:
```json
{json.dumps(mongo_query, ensure_ascii=False, indent=2) if mongo_query else "ไม่มีข้อมูล"}
```

Search Reasoning: {search_reasoning}
Total Results: {total_results} รายการ

Top Products:{products_info}

User Context:
- หมวดหมู่: {entities.get('category', 'ไม่ระบุ')}
- การใช้งาน: {entities.get('usage', 'ไม่ระบุ')}
- งบประมาณ: {entities.get('budget', 'ไม่ระบุ')}
- คำสำคัญ: {', '.join(entities.get('keywords', []))}

**Instructions:**
1. สร้างการแนะนำที่เป็นธรรมชาติ เหมือนพนักงานขายมืออาชีพ
2. อธิบายว่าทำไมแนะนำสินค้านี้ (highlight key selling points)
3. เปรียบเทียบตัวเลือกหากมีหลายตัว
4. ระบุข้อดี: ราคา, คะแนน, ความนิยม, ส่วนลด, สต็อก
5. ใช้ emoji เพื่อให้น่าสนใจ แต่ไม่มากเกินไป
6. **สำคัญ: แสดง MongoDB Query ที่ใช้ค้นหาในส่วนท้าย เพื่อความโปร่งใส (สำหรับ development)**
7. ไม่ต้องแสดงข้อมูล JSON หรือข้อมูลดิบอื่นๆ

สร้างการแนะนำที่เป็นธรรมชาติ เป็นกันเอง และมีประโยชน์!
"""

    try:
        global client
        if client is None:
            client = get_openai_client()
            
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        
        return response.choices[0].message.content.strip()
    except Exception as error:
        print(f"Enhanced response generation error: {error}")
        return generate_fallback_response_v2(user_input, products, mongo_query)

async def generate_no_results_response_v2(user_input: str, entities: Dict[str, Any]) -> str:
    """Enhanced no results response"""
    category = entities.get('category', 'ไม่ระบุ')
    budget = entities.get('budget', {})
    
    response = "ขออภัย ไม่พบสินค้าที่ตรงกับความต้องการของคุณ 🔍\n\n"
    
    if category != 'ไม่ระบุ':
        response += f"🏷️ หมวด: {category}\n"
    if budget.get('max'):
        response += f"💰 งบประมาณ: ฿{budget['max']:,}\n"
    
    response += "\n💡 ข้อเสนอแนะ:\n"
    response += "• ลองเพิ่มงบประมาณ\n"
    response += "• ค้นหาด้วยชื่อสินค้าโดยตรง\n"
    response += "• ระบุความต้องการให้ชัดเจนมากขึ้น\n"
    response += "• ลองหมวดหมู่ที่เกี่ยวข้อง\n\n"
    response += f"🔧 **Debug Info - Query ที่ใช้:**\nUser Input: \"{user_input}\""
    
    return response

def generate_fallback_response_v2(user_input: str, products: List[Product], mongo_query: Dict[str, Any] = None) -> str:
    """Enhanced fallback response"""
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
    
    # Add debug info
    response += f"\n\n🔧 **Debug - MongoDB Query:**\n```json\n{json.dumps(mongo_query, ensure_ascii=False, indent=2) if mongo_query else 'ไม่มีข้อมูล'}\n```"
    
    return response