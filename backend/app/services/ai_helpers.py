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

# Category keyword mapping
def get_category_keywords(category_input: str) -> List[str]:
    category_map = {
        'โน้ตบุ๊ก': ['notebook', 'laptop', 'โน้ตบุ๊ก', 'โน้ตบุ้ค', 'โน๊ตบุ๊ค', 'โน้ดบุ๊ค', 'โนตบุ๊ก', 'โน้ต', 'โนต'],
        'คีย์บอร์ด': ['keyboard', 'คีย์บอร์ด', 'คีบอร์ด', 'คีบอด', 'คีย์', 'คี', 'บอร์ด'],
        'เมาส์': ['mouse', 'เมาส์', 'เม้าส์', 'เมาท์', 'เมาส', 'เม้าส'],
        'จอมอนิเตอร์': ['monitor', 'display', 'จอ', 'จอมอนิเตอร์', 'มอนิเตอร์', 'จอคอม', 'หน้าจอ'],
        'การ์ดจอ': ['vga', 'graphics', 'การ์ดจอ', 'การ์จอ', 'กราฟฟิค', 'การ์ดกราฟิก', 'วีจีเอ', 'กราฟิก', 'การ์ด', 'จอ'],
        'ซีพียู': ['cpu', 'processor', 'ซีพียู', 'โปรเซสเซอร์', 'ตัวประมวลผล', 'ซีพี', 'cpu', 'โปรเซส'],
        'หูฟัง': ['headphone', 'headset', 'หูฟัง', 'เฮดโฟน', 'เฮดเซต', 'หู', 'ฟัง'],
        'เมนบอร์ด': ['mainboard', 'motherboard', 'เมนบอร์ด', 'แม่บอร์ด', 'เมน', 'บอร์ด'],
        'แรม': ['ram', 'memory', 'แรม', 'หน่วยความจำ', 'ความจำ', 'แรมม์', 'แรมมี่', 'ram', 'memory'],
        'เคส': ['case', 'casing', 'เคส', 'กล่องเครื่อง', 'case', 'เคสคอม'],
        'พาวเวอร์': ['power', 'psu', 'พาวเวอร์', 'แหล่งจ่ายไฟ', 'พาว', 'เวอร์', 'จ่ายไฟ'],
        'ฮาร์ดดิสก์': ['hdd', 'harddisk', 'storage', 'ฮาร์ดดิสก์', 'หน่วยเก็บข้อมูล', 'ฮาร์ด', 'ดิสก์'],
        'เอสเอสดี': ['ssd', 'solid state', 'เอสเอสดี', 'ssd', 'เอส']
    }
    
    for keywords in category_map.values():
        if any(keyword.lower() in category_input.lower() for keyword in keywords):
            return keywords
    
    return [category_input]

# Enhanced search terms with variations
def enhance_search_terms(original_terms: List[str]) -> List[str]:
    enhanced = list(original_terms)
    
    for term in original_terms:
        if 'โน้ต' in term:
            enhanced.extend(['laptop', 'notebook'])
        if 'การ์ด' in term:
            enhanced.extend(['card', 'vga', 'graphics'])
        if 'คีย์' in term:
            enhanced.extend(['keyboard', 'key'])
        if 'เมาส์' in term:
            enhanced.append('mouse')
    
    return list(set(enhanced))

# LLM 1: Generate optimal MongoDB query
async def generate_optimal_mongo_query(user_input: str) -> Dict[str, Any]:
    normalized_input = normalize_text(user_input)
    
    # Category data from navigation_attributes.json
    categories = [
        "Notebooks", "Gaming Notebooks", "Ultrathin Notebooks", "2 in 1 Notebooks",
        "Desktop PC", "All in One PC (AIO)", "Mini PC",
        "CPU", "Graphics Cards", "RAM", "Mainboards", "Case & Power Supply",
        "Keyboard", "Mouse", "Gaming Mouse", "Mechanical & Gaming Keyboard", "Wireless Keyboard", "Wireless Mouse",
        "Keyboard & Mouse Combo", "Keyboard Accessories", "Mouse Accessories", "Mouse Pad",
        "Monitor", "Monitor Arm / Mount",
        "Headphone", "Headset", "Speaker", "In Ear Headphone", "True Wireless Headphone",
        "Hard Drive & Solid State Drive", "External & Portable Drive", "Memory Card", "NAS Storage",
        "Printer", "Scanner", "Ink / Toner / Tape / Drum",
        "Gaming Accessories", "Gaming Chair", "Gaming Desk", "Gaming Mouse",
        "Webcam", "Microphone", "Camera", "Camera Accessories",
        "Network Device", "Network Accessories", "Cable", "Cables",
        "UPS", "Power Strip / Extension Cord", "Battery",
        "Apple Watch", "AirPods", "iPhone", "iPad", "Apple Accessories",
        "Smartphone", "Tablet", "Smartphone / Tablet Accessories"
    ]
    
    prompt = f"""
คุณคือ MongoDB Query Expert AI ที่เชี่ยวชาญในการสร้าง Query ให้ตรงกับความต้องการของผู้ใช้มากที่สุด

INPUT: "{normalized_input}"

ฐานข้อมูล MongoDB Schema:
- Collection: products
- Fields: title, description, cateName, price, salePrice, stockQuantity, rating, totalReviews, productView, images, freeShipping, product_warranty_2_year, product_warranty_3_year

หมวดหมู่สินค้า (cateName) ที่มีในระบบ:
{', '.join(categories)}

**หลักการสำคัญ:**
1. **จัดการคำกำกวม**: เช่น "โน้ตบุ๊ค", "การ์ดจอมีอะไรบ้าง", "คอมมีอะไรบ้าง" - ต้องเข้าใจและสร้าग query ที่เหมาะสม
2. **Budget Parsing**: "งบ 15000", "เกิน 15000 แต่ไม่ถึง 20000", "ไม่เกิน 30000"
3. **Stock Filter**: ต้องกรอง stockQuantity > 0 เสมอ
4. **Category Matching**: ใช้ cateName แทน navigation fields
5. **Text Search**: ค้นหาใน title, description, cateName
6. **Special Features**: สนใจ freeShipping, product_warranty_2_year, product_warranty_3_year
7. **Predictive Intent**: ถ้า input ไม่ชัดเจน ให้คาดเดาความต้องการ

ให้ตอบในรูปแบบ JSON:
{{
  "mongoQuery": {{
    "stockQuantity": {{"$gt": 0}}
    // ... MongoDB query conditions
  }},
  "entities": {{
    "category": "หมวดหมู่หลัก",
    "subCategory": "หมวดหมู่ย่อย",
    "usage": "Gaming|Office|Student|Creative|Programming",
    "budget": {{"min": number, "max": number}},
    "brand": "แบรนด์",
    "specs": ["รายการสเปค"],
    "keywords": ["คำสำคัญ"],
    "features": ["คุณสมบัติ"],
    "intent": "ประเภทความต้องการ: specific_product|category_browse|price_range|comparison"
  }},
  "reasoning": "อธิบายเหตุผลการสร้าง query นี้",
  "confidence": 0.8,
  "suggestions": ["คำถามเพิ่มเติมหากความมั่นใจต่ำ"]
}}

ตอบเฉพาะ JSON เท่านั้น
"""

    try:
        # Get client lazily
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
            "reasoning": result.get("reasoning", "Query generated from user input")
        }
    except Exception as error:
        print(f"Query generation error: {error}")
        return generate_fallback_query(normalized_input)

def generate_fallback_query(input_text: str) -> Dict[str, Any]:
    entities = extract_entities_fallback(input_text)
    query = build_query(entities)
    
    return {
        "query": query,
        "entities": entities,
        "reasoning": "Fallback query generated due to parsing error"
    }

def extract_entities_fallback(input_text: str) -> Dict[str, Any]:
    entities = {"keywords": []}
    
    category_map = {
        'แรม': {'cat': 'RAM', 'usage': 'Office'},
        'การ์ดจอ': {'cat': 'Graphics Cards', 'usage': 'Gaming'},
        'โน้ตบุ๊ก': {'cat': 'Notebooks', 'usage': 'Student'},
        'คีย์บอร์ด': {'cat': 'Keyboard', 'usage': 'Office'},
        'เมาส์': {'cat': 'Mouse', 'usage': 'Office'},
        'ซีพียู': {'cat': 'CPU', 'usage': 'Office'},
        'หูฟัง': {'cat': 'Headphone', 'usage': 'Gaming'},
        'จอ': {'cat': 'Monitor', 'usage': 'Office'},
        'สปีกเกอร์': {'cat': 'Speaker', 'usage': 'Entertainment'}
    }
    
    for keyword, config in category_map.items():
        if keyword in input_text:
            entities["category"] = config['cat']
            entities["usage"] = config['usage']
            entities["keywords"].append(keyword)
            break
    
    # Extract budget
    import re
    budget_match = re.findall(r'(\d+(?:,\d+)*)', input_text)
    if budget_match:
        budget = int(budget_match[0].replace(',', ''))
        if budget > 1000:
            entities["budget"] = {"max": budget}
    
    entities["keywords"].append(input_text)
    
    return entities

def build_query(entities: Dict[str, Any]) -> Dict[str, Any]:
    query = {
        "stockQuantity": {"$gt": 0}
    }
    
    if entities.get("budget", {}).get("max"):
        budget = entities["budget"]
        query["salePrice"] = {"$lte": budget["max"]}
        if budget.get("min"):
            query["salePrice"]["$gte"] = budget["min"]
    
    if entities.get("category"):
        query["cateName"] = {"$regex": entities["category"], "$options": "i"}
    
    return query

# LLM 2: Generate natural product recommendations
async def generate_natural_product_recommendation(
    user_input: str,
    entities: Dict[str, Any],
    query_result: List[Product],
    search_reasoning: str,
    mongo_query: Dict[str, Any] = None
) -> str:
    if len(query_result) == 0:
        return await generate_no_results_response(user_input, entities)

    top_products = query_result[:3]
    total_results = len(query_result)
    
    products_info = ""
    for i, p in enumerate(top_products):
        products_info += f"""
{i + 1}. {p.title}
   - ราคา: ฿{p.salePrice:,} (ราคาเต็ม: ฿{p.price:,})
   - คะแนน: {p.rating}/5 ({p.totalReviews} รีวิว)
   - ยอดนิยม: {p.productView:,} ครั้งเข้าชม
   - สต็อก: {p.stockQuantity} ชิ้น
   - หมวด: {p.cateName or ''}"""
    
    prompt = f"""
คุณคือ AI Sales Assistant ที่เชี่ยวชาญในการแนะนำสินค้าไอทีให้ลูกค้า

User Input: "{user_input}"
Search Reasoning: {search_reasoning}
Total Results: {total_results}

MongoDB Query ที่ใช้ค้นหา:
```json
{json.dumps(mongo_query, ensure_ascii=False, indent=2) if mongo_query else "ไม่มีข้อมูล"}
```

Top Products Found:{products_info}

User Entities:
- หมวดหมู่: {entities.get('category', 'ไม่ระบุ')}
- การใช้งาน: {entities.get('usage', 'ไม่ระบุ')}
- งบประมาณ: {entities.get('budget', 'ไม่ระบุ')}
- แบรนด์: {entities.get('brand', 'ไม่ระบุ')}
- สเปค: {', '.join(entities.get('specs', [])) if entities.get('specs') else 'ไม่ระบุ'}
- คุณสมบัติ: {', '.join(entities.get('features', [])) if entities.get('features') else 'ไม่ระบุ'}

**Instructions:**
1. สร้างการแนะนำที่เป็นธรรมชาติ เหมือนพนักงานขายมืออาชีพ
2. อธิบายว่าทำไมแนะนำสินค้านี้ (highlight key selling points)
3. เปรียบเทียบตัวเลือกหากมีหลายตัว
4. ระบุข้อดี: ราคา, คะแนน, ความนิยม, ส่วนลด, สต็อก
5. แนะนำเพิ่มเติมหากเป็นคำถามกำกวม
6. ใช้ emoji เพื่อให้น่าสนใจ
7. **สำคัญ: แสดง MongoDB Query ที่ใช้ค้นหาในส่วนท้ายของการตอบกลับ เพื่อความโปร่งใส**
8. ไม่ต้องแสดง JSON หรือข้อมูลดิบอื่นๆ นอกจาก MongoDB Query

สร้างการแนะนำที่เป็นธรรมชาติ เป็นกันเอง และมีประโยชน์!
"""

    try:
        # Get client lazily
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
        print(f"Response generation error: {error}")
        return generate_fallback_response(user_input, query_result)

async def generate_no_results_response(user_input: str, entities: Dict[str, Any]) -> str:
    prompt = f"""
คุณคือ AI Assistant ที่ช่วยลูกค้าเมื่อไม่พบสินค้าที่ต้องการ

User Input: "{user_input}"
Entities: {json.dumps(entities, ensure_ascii=False, indent=2)}

สร้างข้อความที่:
1. แสดงความเสียใจที่ไม่พบสินค้า
2. วิเคราะห์สาเหตุที่เป็นไปได้
3. เสนอทางเลือก: ขยายงบ, เปลี่ยนแบรนด์, เปลี่ยนสเปค
4. เสนอหมวดหมู่ที่เกี่ยวข้อง
5. ให้คำแนะนำในการค้นหาใหม่

ใช้ emoji และโทนเป็นกันเอง ช่วยเหลือ
"""

    try:
        # Get client lazily
        global client
        if client is None:
            client = get_openai_client()
            
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        return response.choices[0].message.content.strip()
    except Exception as error:
        print(f"No results response error: {error}")
        return generate_basic_no_results_message(user_input, entities)

def generate_fallback_response(user_input: str, products: List[Product]) -> str:
    top_product = products[0]
    total_results = len(products)
    
    response = f"พบสินค้าที่ตรงกับความต้องการ {total_results} รายการ 🛍️\n\n"
    response += f"⭐ แนะนำ: {top_product.title}\n"
    response += f"💰 ราคา: ฿{top_product.salePrice:,}"
    
    discount = top_product.price - top_product.salePrice
    if discount > 0:
        discount_percent = round((discount / top_product.price) * 100)
        response += f" (ลด {discount_percent}% จาก ฿{top_product.price:,})"
    
    response += f"\n📦 คงเหลือ: {top_product.stockQuantity} ชิ้น"
    response += f"\n⭐ คะแนน: {top_product.rating}/5 ({top_product.totalReviews} รีวิว)"
    
    if total_results > 1:
        response += f"\n\n📋 ดูสินค้าทั้งหมด {total_results} รายการเพื่อเลือกที่ใช่สำหรับคุณ!"
    
    return response

def generate_basic_no_results_message(user_input: str, entities: Dict[str, Any]) -> str:
    response = "ขออภัย ไม่พบสินค้าที่ตรงกับความต้องการของคุณ 🔍\n\n"
    
    if entities.get("category"):
        response += f"หมวด: {entities['category']}\n"
    if entities.get("budget", {}).get("max"):
        response += f"งบประมาณ: ฿{entities['budget']['max']:,}\n"
    if entities.get("usage"):
        response += f"การใช้งาน: {entities['usage']}\n"
    
    response += "\n💡 ข้อเสนอแนะ:\n"
    response += "• ลองเพิ่มงบประมาณ\n"
    response += "• ค้นหาด้วยคำอื่น\n"
    response += "• ระบุความต้องการให้ชัดเจนมากขึ้น"
    
    return response