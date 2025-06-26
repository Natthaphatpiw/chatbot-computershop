import os
import json
import re
from openai import OpenAI
from typing import List, Dict, Any, Tuple
from app.models import Product

# Initialize OpenAI client with error handling
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    return OpenAI(api_key=api_key)

client = None

# Enhanced text normalization for better Thai language processing
def normalize_text_advanced(text: str) -> str:
    """Advanced text normalization with comprehensive Thai language support"""
    normalized = text.lower()
    
    # Notebook variations - comprehensive patterns
    notebook_patterns = [
        (r'โน้?[ดต๊]บุ๊?[คก]', 'โน้ตบุ๊ก'),
        (r'โนต?บุ[๊ค]+', 'โน้ตบุ๊ก'),
        (r'โน๊ตบุ[๊ค]+', 'โน้ตบุ๊ก'),
        (r'โนคบุค', 'โน้ตบุ๊ก'),
        (r'โน้ตบุค', 'โน้ตบุ๊ก'),
        (r'laptop', 'โน้ตบุ๊ก'),
        (r'notebook', 'โน้ตบุ๊ก')
    ]
    
    # Graphics card variations
    graphics_patterns = [
        (r'การ์[จด]อ', 'การ์ดจอ'),
        (r'[วฟ]ีจีเอ', 'การ์ดจอ'),
        (r'กราฟิ?[คกข]', 'การ์ดจอ'),
        (r'vga', 'การ์ดจอ'),
        (r'graphics', 'การ์ดจอ')
    ]
    
    # Computer variations - important for Thai context
    computer_patterns = [
        (r'คอมพิ?วเ?ตอร์', 'คอมพิวเตอร์'),
        (r'คอม(?!พิ)', 'คอมพิวเตอร์'),  # "คอม" but not "คอมพิ"
        (r'เครื่อง(?=.*คอม|.*pc)', 'คอมพิวเตอร์'),
        (r'desktop', 'คอมตั้งโต๊ะ'),
        (r'pc', 'คอมพิวเตอร์')
    ]
    
    # Other components
    component_patterns = [
        (r'คีบอร์?ด', 'คีย์บอร์ด'),
        (r'เม้าส์', 'เมาส์'),
        (r'ซีพียู', 'ซีพียู'),
        (r'cpu', 'ซีพียู'),
        (r'แรม', 'แรม'),
        (r'ram', 'แรม'),
        (r'memory', 'แรม'),
        (r'หูฟัง', 'หูฟัง'),
        (r'headphone', 'หูฟัง'),
        (r'จอ(?!คอม)', 'มอนิเตอร์'),
        (r'monitor', 'มอนิเตอร์'),
        (r'โปรเซส[เซส]อร์', 'ซีพียู')
    ]
    
    # Apply all patterns
    all_patterns = notebook_patterns + graphics_patterns + computer_patterns + component_patterns
    
    for pattern, replacement in all_patterns:
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
    
    return normalized

# Enhanced contextual phrase segmentation
def contextual_phrase_segmentation(text: str) -> List[str]:
    """
    Segment input text into meaningful phrases based on context
    Example: "อยากได้คอมทำงานกราฟิก แนะนำหน่อย" → ["อยากได้คอม", "ทำงานกราฟิก", "แนะนำหน่อย"]
    """
    import re
    
    # Normalize first
    normalized = normalize_text_advanced(text)
    
    # Define phrase patterns with context awareness
    phrase_patterns = [
        # Specific product names (highest priority)
        (r'Ryzen\s*\d+\s*\d+\w*', 'PRODUCT_NAME'),     # Ryzen 5 5600G
        (r'Intel\s*Core\s*i\d+', 'PRODUCT_NAME'),       # Intel Core i5
        (r'RTX\s*\d+\w*', 'PRODUCT_NAME'),              # RTX 4060
        (r'GTX\s*\d+\w*', 'PRODUCT_NAME'),              # GTX 1660
        (r'AMD\s*\w*\d+\w*', 'PRODUCT_NAME'),           # AMD 5600G
        
        # Product desire phrases (keep product and desire together)
        (r'อยากได้(โน้ตบุ๊ก|คอมพิวเตอร์|คอม|การ์ดจอ|เมาส์|คีย์บอร์ด|หูฟัง)', 'PRODUCT_DESIRE'),
        (r'ต้องการ(โน้ตบุ๊ก|คอมพิวเตอร์|คอม|การ์ดจอ|เมาส์|คีย์บอร์ด|หูฟัง)', 'PRODUCT_DESIRE'),
        (r'หา(โน้ตบุ๊ก|คอมพิวเตอร์|คอม|การ์ดจอ|เมาส์|คีย์บอร์ด|หูฟัง)', 'PRODUCT_DESIRE'),
        
        # Product categories as standalone phrases
        (r'โน้ตบุ๊ก', 'PRODUCT'),
        (r'คอมพิวเตอร์', 'PRODUCT'),
        (r'คอม(?!พิ)', 'PRODUCT'),  # "คอม" but not "คอมพิ"
        (r'การ์ดจอ', 'PRODUCT'),
        (r'เมาส์', 'PRODUCT'),
        (r'คีย์บอร์ด', 'PRODUCT'),
        (r'หูฟัง', 'PRODUCT'),
        
        # Usage phrases (more specific patterns)
        (r'ทำงานกราฟิก', 'USAGE'),
        (r'ทำงานออฟฟิศ', 'USAGE'),
        (r'ทำงานเอกสาร', 'USAGE'),
        (r'ทำงาน(?!กราฟิก|ออฟฟิศ)', 'USAGE'),  # General work
        (r'เล่นเกมได้ไหม', 'QUESTION'),         # Specific gaming question - higher priority
        (r'เล่นเกม\s*[\w\s]*', 'USAGE'),
        (r'ใช้งาน[\w\s]*', 'USAGE'),
        (r'สำหรับ[\w\s]*(?=\s|$)', 'USAGE'),
        
        # Budget phrases
        (r'งบ\s*\d+(?:,\d+)*', 'BUDGET'),
        (r'ไม่เกิน\s*\d+(?:,\d+)*', 'BUDGET'),
        (r'ประมาณ\s*\d+(?:,\d+)*', 'BUDGET'),
        (r'ราคา[\s\w]*\d+(?:,\d+)*', 'BUDGET'),
        
        # Brand phrases
        (r'(ASUS|HP|Dell|MSI|Acer|Lenovo|Apple|Razer|Logitech|Corsair)', 'BRAND'),
        (r'ยี่ห้อ\s*\w+', 'BRAND'),
        
        # Request phrases (NON-FILTER - should be skipped in Stage 1)
        (r'แนะนำหน่อย', 'REQUEST'),
        (r'รุ่นไหนดี', 'REQUEST'),
        (r'มีอะไรบ้าง', 'REQUEST'),
        (r'แนะนำ\w*', 'REQUEST'),
        
        # Question phrases (NON-FILTER - should be skipped in Stage 1)
        (r'เล่นเกมได้ไหม', 'QUESTION'),       # เล่นเกมได้ไหม
        (r'\w+ได้ไหม', 'QUESTION'),          # ใช้งานได้ไหม, ทำงานได้ไหม
        (r'ดีไหม', 'QUESTION'),              # ดีไหม
        (r'\w+ดีไหม', 'QUESTION'),           # ใช้ดีไหม
        (r'เป็นอย่างไร', 'QUESTION'),         # เป็นอย่างไร
        
        # Spec phrases
        (r'RTX\s*\d+', 'SPEC'),
        (r'GTX\s*\d+', 'SPEC'),
        (r'\d+GB\s*(RAM|แรม)', 'SPEC'),
        (r'mechanical', 'SPEC'),
        (r'ไร้สาย', 'SPEC'),
        (r'RGB', 'SPEC'),
    ]
    
    phrases = []
    processed_text = normalized.lower()
    
    # Extract phrases using patterns
    for pattern, phrase_type in phrase_patterns:
        matches = re.finditer(pattern, processed_text, re.IGNORECASE)
        for match in matches:
            phrase = match.group().strip()
            if phrase and phrase not in phrases:
                phrases.append(phrase)
                # Remove matched phrase to avoid overlap
                processed_text = processed_text.replace(phrase.lower(), ' ', 1)
    
    # Handle remaining single words that might be important
    remaining_words = re.findall(r'\b\w{2,}\b', processed_text)
    category_keywords = ['โน้ตบุ๊ก', 'คอมพิวเตอร์', 'คอม', 'การ์ดจอ', 'เมาส์', 'คีย์บอร์ด', 'หูฟัง']
    
    for word in remaining_words:
        if any(keyword in word for keyword in category_keywords) and word not in phrases:
            phrases.append(word)
    
    # If no phrases found, fallback to simple splitting
    if not phrases:
        phrases = [text]
    
    return phrases

# Load database schema and categories
def load_database_schema():
    """Load actual database schema and categories"""
    schema_data = {}
    categories_data = []
    
    # Load schema.json
    try:
        schema_paths = ['../../../schema.json', '../../schema.json', '../schema.json', 'schema.json']
        
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
        nav_paths = ['../../../navigation_attributes.json', '../../navigation_attributes.json', '../navigation_attributes.json', 'navigation_attributes.json']
        
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

# Comprehensive Thai-English category mapping
def get_comprehensive_category_mapping() -> Dict[str, List[str]]:
    """Enhanced category mapping with comprehensive Thai terms"""
    return {
        # Notebook/Laptop categories
        'โน้ตบุ๊ก': ['Notebooks', 'Gaming Notebooks', 'Ultrathin Notebooks', '2 in 1 Notebooks'],
        'โนตบุ๊ก': ['Notebooks', 'Gaming Notebooks', 'Ultrathin Notebooks', '2 in 1 Notebooks'],  
        'โน๊ตบุ๊ค': ['Notebooks', 'Gaming Notebooks', 'Ultrathin Notebooks', '2 in 1 Notebooks'],
        'โนคบุค': ['Notebooks', 'Gaming Notebooks', 'Ultrathin Notebooks', '2 in 1 Notebooks'],
        'laptop': ['Notebooks', 'Gaming Notebooks', 'Ultrathin Notebooks', '2 in 1 Notebooks'],
        
        # Computer categories - crucial for Thai context
        'คอมพิวเตอร์': ['Desktop PC', 'All in One PC (AIO)', 'Mini PC', 'Notebooks'],
        'คอม': ['Desktop PC', 'All in One PC (AIO)', 'Mini PC', 'Notebooks'],
        'คอมตั้งโต๊ะ': ['Desktop PC', 'All in One PC (AIO)', 'Mini PC'],
        'เครื่อง': ['Desktop PC', 'All in One PC (AIO)', 'Mini PC', 'Notebooks'],
        'desktop': ['Desktop PC', 'All in One PC (AIO)', 'Mini PC'],
        'pc': ['Desktop PC', 'All in One PC (AIO)', 'Mini PC', 'Notebooks'],
        
        # Graphics cards
        'การ์ดจอ': ['Graphics Cards'],
        'การ์จอ': ['Graphics Cards'],
        'กราฟิก': ['Graphics Cards'], 
        'การ์ด': ['Graphics Cards'],
        'วีจีเอ': ['Graphics Cards'],
        'vga': ['Graphics Cards'],
        'graphics': ['Graphics Cards'],
        
        # Input devices
        'คีย์บอร์ด': ['Keyboard', 'Mechanical & Gaming Keyboard', 'Wireless Keyboard'],
        'คีบอร์ด': ['Keyboard', 'Mechanical & Gaming Keyboard', 'Wireless Keyboard'],
        'คีบอด': ['Keyboard', 'Mechanical & Gaming Keyboard', 'Wireless Keyboard'],
        'keyboard': ['Keyboard', 'Mechanical & Gaming Keyboard', 'Wireless Keyboard'],
        
        'เมาส์': ['Mouse', 'Gaming Mouse', 'Wireless Mouse'],
        'เม้าส์': ['Mouse', 'Gaming Mouse', 'Wireless Mouse'],
        'mouse': ['Mouse', 'Gaming Mouse', 'Wireless Mouse'],
        
        # Display
        'จอ': ['Monitor'],
        'มอนิเตอร์': ['Monitor'],
        'จอมอนิเตอร์': ['Monitor'],
        'หน้าจอ': ['Monitor'],
        'monitor': ['Monitor'],
        
        # Components
        'ซีพียู': ['CPU'],
        'โปรเซสเซอร์': ['CPU'],
        'cpu': ['CPU'],
        'processor': ['CPU'],
        
        'แรม': ['RAM'],
        'หน่วยความจำ': ['RAM'],
        'ความจำ': ['RAM'],
        'ram': ['RAM'],
        'memory': ['RAM'],
        
        # Audio
        'หูฟัง': ['Headphone', 'Headset', 'In Ear Headphone', 'True Wireless Headphone'],
        'เฮดโฟน': ['Headphone', 'Headset', 'In Ear Headphone', 'True Wireless Headphone'],
        'เฮดเซต': ['Headphone', 'Headset', 'In Ear Headphone', 'True Wireless Headphone'],
        'headphone': ['Headphone', 'Headset', 'In Ear Headphone', 'True Wireless Headphone'],
        'headset': ['Headphone', 'Headset', 'In Ear Headphone', 'True Wireless Headphone'],
        
        'สปีกเกอร์': ['Speaker'],
        'speaker': ['Speaker'],
        
        # Storage
        'ฮาร์ดดิสก์': ['Hard Drive & Solid State Drive'],
        'ฮาร์ด': ['Hard Drive & Solid State Drive'],
        'เอสเอสดี': ['Hard Drive & Solid State Drive'],
        'ssd': ['Hard Drive & Solid State Drive'],
        'hdd': ['Hard Drive & Solid State Drive']
    }

# LLM Stage 1: Basic Query Builder - NO content analysis
async def stage1_basic_query_builder(user_input: str) -> Dict[str, Any]:
    """
    Stage 1 LLM: Build basic MongoDB query for initial filtering only
    Focuses ONLY on: category, price, stock - NO title/description analysis
    """
    normalized_input = normalize_text_advanced(user_input)
    
    # Load database information
    schema_data, categories_data = load_database_schema()
    category_mapping = get_comprehensive_category_mapping()
    
    # Get actual database fields
    actual_fields = []
    if schema_data and 'properties' in schema_data:
        actual_fields = list(schema_data['properties'].keys())
    
    # Convert data to strings to avoid f-string issues
    fields_str = str(actual_fields)
    categories_str = json.dumps(categories_data, ensure_ascii=False)
    mapping_str = json.dumps(category_mapping, ensure_ascii=False, indent=2)
    
    prompt = f"""
คุณคือ Stage 1 Query Builder - มีหน้าที่สร้าง MongoDB Query พื้นฐานเท่านั้น

**USER INPUT:** "{user_input}"
**NORMALIZED:** "{normalized_input}"

**DATABASE FIELDS:** {fields_str}
**AVAILABLE CATEGORIES:** {categories_str}
**CATEGORY MAPPING:** {mapping_str}

**STAGE 1 RESPONSIBILITIES (จำกัดเฉพาะนี้):**
1. **CONTEXTUAL INPUT ANALYSIS** - วิเคราะห์บริบทของประโยคก่อนแยกคำ
2. **SEMANTIC PHRASE SEGMENTATION** - แยกวลีตามความหมาย ไม่ใช่แยกคำเดี่ยว
3. **BASIC CATEGORY IDENTIFICATION** - หาหมวดหมู่หลักจาก input หรืออนุมานจากบริบท
4. **BUDGET EXTRACTION** - หาราคาที่ผู้ใช้ระบุ  
5. **BASIC FIELD MAPPING** - แปลงเป็น MongoDB query ง่ายๆ
6. **NO CONTENT ANALYSIS** - ห้ามวิเคราะห์ title/description/brand/specs
7. **SMART CATEGORY INFERENCE** - หากไม่มีหมวดหมู่ชัดเจน ให้อนุมานจากบริบท

**STRICT RULES - STAGE 1:**
- ใช้เฉพาะ: stockQuantity, cateName, salePrice
- ห้ามใช้: title, description, $regex, $or สำหรับ content
- ห้ามวิเคราะห์: แบรนด์, สเปค, การใช้งานเฉพาะ, ชื่อเกม
- **CONTEXTUAL UNDERSTANDING**: อ่านบริบทประโยคก่อนแยกส่วน
- ถ้าไม่แน่ใจ = ไม่ใส่ใน query (ให้ Stage 2 จัดการ)
- **CATEGORY INFERENCE**: หากไม่มีหมวดหมู่ชัดเจน แต่มีชื่อผลิตภัณฑ์เฉพาะ ให้อนุมานหมวดหมู่ที่เกี่ยวข้อง
- **NON-FILTER PHRASES**: คำขอ/คำถาม เช่น "แนะนำหน่อย", "รุ่นไหนดี", "เล่นเกมได้ไหม" ไม่ใช่ filter - ข้ามไป

**CONTEXTUAL ANALYSIS EXAMPLES:**

Input: "โน้ตบุ๊ค ASUS งบ 20000"
CONTEXT ANALYSIS:
- "โน้ตบุ๊ก" = หมวดหมู่สินค้า → cateName: "Notebooks" ✅ (can filter)
- "ASUS" = ชื่อแบรนด์ → ❌ (cannot filter in Stage 1 - leave for Stage 2)  
- "งบ 20000" = งบประมาณ → salePrice: max 20000 ✅ (can filter)

Input: "อยากได้คอมทำงานกราฟิก แนะนำหน่อย"
CONTEXT ANALYSIS:
- "อยากได้คอม" = ต้องการคอมพิวเตอร์ → cateName: ["Desktop PC", "Notebooks"] ✅ (can filter)
- "ทำงานกราฟิก" = การใช้งานเฉพาะ → ❌ (usage analysis - leave for Stage 2)
- "แนะนำหน่อย" = คำขอคำแนะนำ → ❌ (NON-FILTER request phrase - skip completely)

Input: "คอมเล่นเกม valorant ไม่เกิน 30000"
CONTEXT ANALYSIS:
- "คอม" = ประเภทสินค้า → cateName: ["Desktop PC", "Gaming Notebooks"] ✅ (can filter)
- "เล่นเกม valorant" = การใช้งานและเกมเฉพาะ → ❌ (usage + game analysis - leave for Stage 2)
- "ไม่เกิน 30000" = งบประมาณ → salePrice: max 30000 ✅ (can filter)

Input: "Ryzen 5 5600G เล่นเกมได้ไหม"
CONTEXT ANALYSIS:
- "Ryzen 5 5600G" = ชื่อ CPU รุ่นเฉพาะ → ❌ (specific product name - leave for Stage 2)
- "เล่นเกมได้ไหม" = คำถามการใช้งาน → ❌ (usage question - leave for Stage 2)
- ไม่มีหมวดหมู่ชัดเจน → ต้องให้ Stage 1 อนุมาน CPU, Notebooks → cateName: ["CPU", "Notebooks"] ✅ (inferred category)

**BUDGET PATTERNS:**
- "งบ X", "ไม่เกิน X", "ประมาณ X", "ราคา X บาท" → max budget
- "X-Y บาท", "ระหว่าง X ถึง Y" → price range

**PHRASE SEGMENTATION RULES:**

**การแยกวลีตามบริบท (ไม่ใช่แยกคำเดี่ยว):**
1. **Product Category Phrases**: "อยากได้คอม", "ต้องการโน้ตบุ๊ก", "หาการ์ดจอ"
2. **Usage Phrases**: "ทำงานกราฟิก", "เล่นเกม valorant", "ใช้งานออฟฟิศ"
3. **Budget Phrases**: "งบ 15000", "ไม่เกิน 20000", "ราคาประมาณ 30000"
4. **Brand Phrases**: "ยี่ห้อ ASUS", "HP หรือ Dell", "MSI gaming"
5. **Request Phrases**: "แนะนำหน่อย", "รุ่นไหนดี", "มีอะไรบ้าง"

**ตัวอย่างการแยกวลีที่ถูกต้อง:**
- "อยากได้คอมทำงานกราฟิก แนะนำหน่อย" 
  → ["อยากได้คอม", "ทำงานกราฟิก", "แนะนำหน่อย"]
- "โน้ตบุ๊ค ASUS งบ 20000"
  → ["โน้ตบุ๊ก", "ASUS", "งบ 20000"]
- "การ์ดจอเล่นเกม RTX 4060"
  → ["การ์ดจอ", "เล่นเกม", "RTX 4060"]

**THAI COMPUTER CONTEXT:**
- "คอม" = อาจหมายถึง Desktop PC, All in One PC, Mini PC, หรือแม้แต่ Notebooks
- "เครื่อง" = คอมพิวเตอร์ทั่วไป

**CRITICAL MONGODB SYNTAX:**
- **Single category**: "cateName": "Notebooks"
- **Multiple categories**: "cateName": {{"$in": ["Desktop PC", "Notebooks"]}}
- **NEVER**: "cateName": ["Desktop PC", "Notebooks"] (ผิด!)
- **ALWAYS use $in for arrays!**

ตอบใน JSON:
{{
  "mongoQuery": {{
    "stockQuantity": {{"$gt": 0}}
    // เพิ่มเฉพาะ cateName และ salePrice ตามที่วิเคราะห์ได้
  }},
  "processedTerms": {{
    "category": "หมวดหมู่ที่ระบุได้",
    "budget": {{"max": number}},
    "segmentedPhrases": ["วลีที่แยกตามบริบท"],
    "used": ["วลีที่ใช้ใน query แล้ว"],
    "remaining": ["วลีที่เหลือให้ Stage 2 วิเคราะห์"],
    "analysis": "อธิบายการแยกวลีและเหตุผล"
  }},
  "reasoning": "อธิบายว่าใช้คำไหนทำ query และคำไหนปล่อยให้ Stage 2",
  "queryType": "basic_filter"
}}

**สำคัญ:** Stage 1 ทำหน้าที่กรองพื้นฐานเท่านั้น - ห้ามเก่ง!
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
        
        # Validate query structure
        query = result["mongoQuery"]
        validated_query = validate_stage1_query(query, actual_fields)
        
        return {
            "query": validated_query,
            "processedTerms": result["processedTerms"],
            "reasoning": result.get("reasoning", "Stage 1 basic filtering"),
            "queryType": result.get("queryType", "basic_filter"),
            "confidence": 0.8
        }
        
    except Exception as error:
        print(f"Stage 1 query generation error: {error}")
        return generate_stage1_fallback(normalized_input, categories_data)

def validate_stage1_query(query: Dict[str, Any], actual_fields: List[str]) -> Dict[str, Any]:
    """Validate Stage 1 query - only allow basic fields"""
    validated_query = {"stockQuantity": {"$gt": 0}}
    
    # Only allow these fields in Stage 1
    allowed_fields = ['stockQuantity', 'cateName', 'salePrice', 'cateId', 'categoryId']
    
    for key, value in query.items():
        if key in allowed_fields:
            validated_query[key] = value
    
    return validated_query

def generate_stage1_fallback(input_text: str, categories_data: List[str]) -> Dict[str, Any]:
    """Fallback for Stage 1 when LLM fails"""
    processed_terms = extract_basic_entities(input_text, categories_data)
    query = build_basic_query(processed_terms)
    
    return {
        "query": query,
        "processedTerms": processed_terms,
        "reasoning": "Stage 1 fallback - basic pattern matching",
        "queryType": "basic_filter",
        "confidence": 0.6
    }

def extract_basic_entities(input_text: str, categories_data: List[str]) -> Dict[str, Any]:
    """Extract basic entities for Stage 1 fallback with improved phrase segmentation"""
    normalized_input = normalize_text_advanced(input_text.lower())
    category_mapping = get_comprehensive_category_mapping()
    
    # Improved contextual phrase segmentation
    segmented_phrases = contextual_phrase_segmentation(input_text)
    
    processed_terms = {
        "segmentedPhrases": segmented_phrases,
        "used": [],
        "remaining": segmented_phrases.copy(),  # Start with all phrases, filter as we process
        "analysis": "Fallback segmentation using pattern matching"
    }
    
    # Find category from segmented phrases
    found_categories = []
    inferred_categories = []
    
    for phrase in segmented_phrases:
        phrase_lower = phrase.lower()
        
        # Skip non-filter phrases (requests and questions)
        if is_non_filter_phrase(phrase):
            continue  # Skip completely - don't use for filtering
        
        # Direct category matching first
        for thai_term, english_categories in category_mapping.items():
            if thai_term in phrase_lower:
                # Collect all matching categories
                matching_cats = [cat for cat in english_categories if cat in categories_data]
                if matching_cats:
                    found_categories.extend(matching_cats)
                    processed_terms["used"].append(phrase)
                    # Remove from remaining
                    if phrase in processed_terms["remaining"]:
                        processed_terms["remaining"].remove(phrase)
                    break
        else:
            # If no direct category match, try to infer from product names
            if is_specific_product_name(phrase):
                inferred_cats = infer_categories_from_product_name(phrase, categories_data)
                if inferred_cats:
                    inferred_categories.extend(inferred_cats)
                    if phrase not in processed_terms["used"]:
                        processed_terms["used"].append(phrase)  # Mark as used for inference
                    # Keep in remaining for Stage 2 analysis - specific product names need Stage 2
    
    # Set category - prioritize direct matches, then inferred
    all_categories = found_categories + inferred_categories
    if all_categories:
        unique_categories = list(set(all_categories))
        if len(unique_categories) == 1:
            processed_terms["category"] = unique_categories[0]
        else:
            processed_terms["categories"] = unique_categories  # Multiple categories
    
    # Extract budget from segmented phrases  
    budget_patterns = [
        r'งบ\s*(\d+(?:,\d{3})*)',
        r'ไม่เกิน\s*(\d+(?:,\d{3})*)',
        r'ประมาณ\s*(\d+(?:,\d{3})*)',
        r'(\d+(?:,\d{3})*)\s*บาท'
    ]
    
    for phrase in processed_terms["remaining"].copy():  # Use copy to avoid modification during iteration
        for pattern in budget_patterns:
            matches = re.findall(pattern, phrase.lower())
            if matches:
                budget = int(matches[0].replace(',', ''))
                if budget >= 1000:
                    processed_terms["budget"] = {"max": budget}
                    if phrase not in processed_terms["used"]:
                        processed_terms["used"].append(phrase)
                    # Remove from remaining - budget phrases don't need Stage 2
                    if phrase in processed_terms["remaining"]:
                        processed_terms["remaining"].remove(phrase)
                    break
    
    return processed_terms

def is_non_filter_phrase(phrase: str) -> bool:
    """Check if phrase is a non-filter phrase (request/question) that shouldn't be used for filtering"""
    phrase_lower = phrase.lower()
    
    # Request patterns
    request_patterns = [
        r'แนะนำ', r'รุ่นไหนดี', r'มีอะไรบ้าง', r'แนะนำหน่อย'
    ]
    
    # Question patterns  
    question_patterns = [
        r'\w+ได้ไหม',      # เล่นเกมได้ไหม, ใช้งานได้ไหม
        r'\w+ดีไหม',       # ดีไหม
        r'เป็นอย่างไร'      # เป็นอย่างไร
    ]
    
    all_patterns = request_patterns + question_patterns
    
    for pattern in all_patterns:
        if re.search(pattern, phrase_lower):
            return True
    
    return False

def is_specific_product_name(phrase: str) -> bool:
    """Check if phrase looks like a specific product name"""
    phrase_lower = phrase.lower()
    
    # CPU patterns
    cpu_patterns = [
        r'ryzen\s*\d+\s*\d+\w*',  # Ryzen 5 5600G, Ryzen 7 5800X
        r'intel?\s*core?\s*i\d+',  # Intel Core i5, i7
        r'intel?\s*\w*\d+\w*',     # Intel 12700K
        r'amd\s*\w*\d+\w*',        # AMD 5600G
    ]
    
    # GPU patterns  
    gpu_patterns = [
        r'(rtx|gtx)\s*\d+\w*',     # RTX 4060, GTX 1660
        r'(radeon|rx)\s*\d+\w*',   # RX 6600 XT
    ]
    
    # Product model patterns
    model_patterns = [
        r'[a-z]+\s*\d+\w*',        # Generic model patterns
        r'\w+\s+[a-z]\d+\w*',      # Brand + model number
    ]
    
    all_patterns = cpu_patterns + gpu_patterns + model_patterns
    
    for pattern in all_patterns:
        if re.search(pattern, phrase_lower, re.IGNORECASE):
            return True
    
    return False

def infer_categories_from_product_name(phrase: str, categories_data: List[str]) -> List[str]:
    """Infer categories from specific product names"""
    phrase_lower = phrase.lower()
    inferred_categories = []
    
    # CPU inference
    cpu_patterns = [
        r'ryzen', r'intel', r'amd', r'cpu', r'processor', r'i\d+', r'\d+\w*g$'
    ]
    
    if any(re.search(pattern, phrase_lower) for pattern in cpu_patterns):
        # CPU could be standalone or in notebooks
        possible_cats = ['CPU', 'Notebooks', 'Desktop PC']
        inferred_categories.extend([cat for cat in possible_cats if cat in categories_data])
    
    # GPU inference
    gpu_patterns = [
        r'rtx', r'gtx', r'radeon', r'rx', r'graphics'
    ]
    
    if any(re.search(pattern, phrase_lower) for pattern in gpu_patterns):
        possible_cats = ['Graphics Cards', 'Gaming Notebooks', 'Desktop PC']
        inferred_categories.extend([cat for cat in possible_cats if cat in categories_data])
    
    return list(set(inferred_categories))

def build_basic_query(processed_terms: Dict[str, Any]) -> Dict[str, Any]:
    """Build basic MongoDB query from processed terms"""
    query = {"stockQuantity": {"$gt": 0}}
    
    # Add category - handle both single and multiple categories
    if processed_terms.get("category"):
        # Single category
        query["cateName"] = processed_terms["category"]
    elif processed_terms.get("categories"):
        # Multiple categories - use $in operator
        query["cateName"] = {"$in": processed_terms["categories"]}
    
    # Add budget if found
    if processed_terms.get("budget", {}).get("max"):
        query["salePrice"] = {"$lte": processed_terms["budget"]["max"]}
    
    return query

# LLM Stage 2: Deep Content Analyzer and Product Matcher
async def stage2_content_analyzer(
    user_input: str,
    stage1_result: Dict[str, Any],
    products: List[Product]
) -> List[Product]:
    """
    Stage 2 LLM: Deep content analysis and product matching
    Analyzes remaining terms from Stage 1 and matches against title/description
    """
    if len(products) == 0:
        return []
    
    processed_terms = stage1_result.get("processedTerms", {})
    remaining_terms = processed_terms.get("remaining", [user_input])
    used_terms = processed_terms.get("used", [])
    
    # If no remaining terms to analyze, just sort by popularity
    if not remaining_terms or (len(remaining_terms) == 1 and remaining_terms[0] == user_input and not used_terms):
        print("[Stage 2] No specific analysis needed - using popularity sorting")
        return sorted(products, 
                     key=lambda p: (p.productView, p.rating, -p.salePrice), 
                     reverse=True)[:8]
    
    print(f"[Stage 2] Analyzing {len(products)} products for remaining terms: {remaining_terms}")
    
    # Prepare products info for LLM analysis
    products_info = ""
    for i, p in enumerate(products[:15]):  # Limit to 15 products for token efficiency
        discount = p.price - p.salePrice
        discount_text = ""
        if discount > 0:
            discount_percent = round((discount / p.price) * 100)
            discount_text = f" (ลด {discount_percent}%)"
        
        price_formatted = f"฿{p.salePrice:,}"
        views_formatted = f"{p.productView:,}"
        
        products_info += f"""
Product {i + 1}:
Title: {p.title}
Description: {p.description[:200]}...
Category: {p.cateName}
Price: {price_formatted}{discount_text}
Rating: {p.rating}/5 ({p.totalReviews})
Views: {views_formatted}
Stock: {p.stockQuantity}
"""
    
    prompt = f"""
คุณคือ Stage 2 Content Analyzer - เชี่ยวชาญในการวิเคราะห์เนื้อหาสินค้าให้ตรงกับความต้องการ

**ORIGINAL USER INPUT:** "{user_input}"

**STAGE 1 PROCESSING RESULTS:**
- **Segmented Phrases:** {processed_terms.get('segmentedPhrases', [])}
- **Used Phrases (Stage 1 กรองแล้ว):** {used_terms}
- **Remaining Phrases (ให้ Stage 2 วิเคราะห์):** {remaining_terms}
- **Segmentation Analysis:** {processed_terms.get('analysis', 'N/A')}
- **MongoDB Query Applied:** {json.dumps(stage1_result.get('query', {}), ensure_ascii=False)}
- **Stage 1 Reasoning:** {stage1_result.get('reasoning', 'N/A')}

**PRODUCTS TO ANALYZE:**
{products_info}

**STAGE 2 ANALYSIS MISSION:**
1. **วิเคราะห์ Remaining Terms** - ในสิ่งที่ Stage 1 ยังไม่ได้จัดการ
2. **ระบุประเภทข้อมูล** - แบรนด์ (title), สเปค/การใช้งาน (description), คุณสมบัติ (title+description)
3. **จับคู่เนื้อหา** - ค้นหาในฟิลด์ที่เหมาะสม (title สำหรับแบรนด์, description สำหรับการใช้งาน)
4. **ให้คะแนนความเหมาะสม** - 0-100 ตามความตรงกับ remaining terms
5. **SPECIFIC PRODUCT MATCHING** - ถ้าวลีดูเหมือนชื่อผลิตภัณฑ์เฉพาะ ให้ค้นหาในชื่อก่อน แล้วคำอธิบายตามลำดับ

**ANALYSIS GUIDELINES:**

**ชื่อผลิตภัณฑ์เฉพาะ** → ค้นหาใน **TITLE** (ความสำคัญสูงสุด):
- "Ryzen 5 5600G", "Intel Core i5", "RTX 4060", "GTX 1660"
- "MacBook Pro", "ThinkPad", "Pavilion", "Inspiron"
- "MX Master", "K95 RGB", "Razer DeathAdder"
- **วิธีการ**: ค้นหาคำสำคัญในชื่อ เช่น "5600G" อาจพบใน "AMD RYZEN 5 5600G 3.9 GHz"

**แบรนด์/รุ่น** → ค้นหาใน **TITLE**:
- "ASUS", "HP", "Dell", "MSI", "Acer", "Lenovo", "Apple"
- "AMD", "Intel", "NVIDIA" 
- "Razer", "Logitech", "Corsair"

**การใช้งาน/เกม** → ค้นหาใน **DESCRIPTION**:
- "เล่นเกม", "gaming", "valorant", "pubg", "gta", "cyberpunk"
- "ทำงาน", "office", "excel", "photoshop", "video editing"
- "เรียน", "streaming", "design", "programming"

**สเปคเฉพาะ** → ค้นหาใน **TITLE + DESCRIPTION**:
- "16GB RAM", "512GB SSD", "144Hz", "4K", "RGB"
- "mechanical", "wireless", "bluetooth", "USB-C"
- "RTX", "GTX", "Intel", "AMD", "Core i7"

**SCORING CRITERIA:**
- **Perfect Match** (90-100): ตรงทุกคำใน remaining terms
- **Good Match** (70-89): ตรงส่วนใหญ่ของ remaining terms  
- **Partial Match** (50-69): ตรงบางส่วนของ remaining terms
- **Weak Match** (30-49): ตรงเล็กน้อยหรือคล้ายกัน
- **No Match** (0-29): ไม่ตรงเลย

**EXAMPLES:**

Remaining: ["ASUS"] → ดู title ว่ามี "ASUS" หรือไม่
Remaining: ["valorant"] → ดู description ว่าระบุสเปคเล่น valorant ได้หรือไม่  
Remaining: ["RGB", "mechanical"] → ดู title+description ว่ามีคำเหล่านี้หรือไม่
Remaining: ["Ryzen 5 5600G"] → ดู title ว่าผลิตภัณฑ์ไหนมีคำว่า "5600G" หรือ "RYZEN 5 5600G" ใน title
Remaining: ["RTX 4060"] → ดู title ว่าผลิตภัณฑ์ไหนมีคำว่า "RTX 4060" ใน title

**SPECIFIC PRODUCT NAME MATCHING STRATEGY:**
1. **แยกคำสำคัญ**: "Ryzen 5 5600G" → ["Ryzen", "5600G", "AMD"]
2. **ค้นหาใน Title**: หาผลิตภัณฑ์ที่มีคำสำคัญเหล่านี้ใน title
3. **ถ้าไม่เจอใน Title**: ลองค้นหาใน description 
4. **ให้คะแนนสูง**: ถ้าเจอใน title = 95-100 คะแนน, ใน description = 70-80 คะแนน

ตอบใน JSON:
{{
  "selectedProducts": [
    {{
      "index": 0,
      "score": 95,
      "matchDetails": {{
        "titleMatches": ["คำที่พบใน title"],
        "descriptionMatches": ["คำที่พบใน description"],  
        "reasoning": "เหตุผลที่ให้คะแนนนี้"
      }}
    }}
  ],
  "analysisSummary": "สรุปการวิเคราะห์ remaining terms",
  "unmatchedTerms": ["คำที่ไม่พบในสินค้าใดเลย"]
}}

**สำคัญ:** วิเคราะห์เฉพาะ remaining terms ที่ Stage 1 ยังไม่ได้จัดการ!
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
        selected_products_data = result.get("selectedProducts", [])
        
        # Build filtered and ranked products list
        filtered_products = []
        for item in selected_products_data:
            idx = item.get("index", -1)
            if 0 <= idx < len(products):
                filtered_products.append(products[idx])
        
        print(f"[Stage 2] Selected {len(filtered_products)} products from {len(products)}")
        
        # If no products matched remaining terms, return top products by popularity
        if not filtered_products:
            print("[Stage 2] No content matches found - falling back to popularity sorting")
            return sorted(products, 
                         key=lambda p: (p.productView, p.rating, -p.salePrice), 
                         reverse=True)[:8]
        
        return filtered_products[:8]  # Limit to top 8
        
    except Exception as error:
        print(f"Stage 2 analysis error: {error}")
        # Fallback: return products sorted by popularity
        return sorted(products, 
                     key=lambda p: (p.productView, p.rating, -p.salePrice), 
                     reverse=True)[:8]

# Combined two-stage response generator
async def generate_two_stage_response(
    user_input: str,
    stage1_result: Dict[str, Any],
    products: List[Product],
    stage2_analysis: Dict[str, Any] = None
) -> str:
    """Generate natural language response explaining the two-stage process"""
    
    if len(products) == 0:
        return await generate_two_stage_no_results(user_input, stage1_result)
    
    processed_terms = stage1_result.get("processedTerms", {})
    used_terms = processed_terms.get("used", [])
    remaining_terms = processed_terms.get("remaining", [])
    
    top_products = products[:3]
    total_results = len(products)
    
    products_info = ""
    for i, p in enumerate(top_products):
        discount = p.price - p.salePrice
        discount_text = ""
        if discount > 0:
            discount_percent = round((discount / p.price) * 100)
            price_original_formatted = f"฿{p.price:,}"
            discount_text = f" (ลด {discount_percent}% จาก {price_original_formatted})"
        
        price_sale_formatted = f"฿{p.salePrice:,}"
        views_formatted = f"{p.productView:,}"
        shipping_text = '✅' if p.freeShipping else '❌'
        
        products_info += f"""
{i + 1}. {p.title}
   - ราคา: {price_sale_formatted}{discount_text}
   - คะแนน: {p.rating}/5 ({p.totalReviews} รีวิว)
   - ยอดนิยม: {views_formatted} ครั้งเข้าชม
   - สต็อก: {p.stockQuantity} ชิ้น
   - หมวด: {p.cateName or 'N/A'}
   - ส่งฟรี: {shipping_text}"""
    
    prompt = f"""
คุณคือ Professional IT Sales Assistant ที่เชี่ยวชาญการแนะนำสินค้าด้วยระบบ Two-Stage Analysis

**USER INPUT:** "{user_input}"

**TWO-STAGE PROCESSING RESULTS:**

**Stage 1 - Basic Filtering:**
- **Used Terms:** {used_terms} 
- **MongoDB Query:** {json.dumps(stage1_result.get('query', {}), ensure_ascii=False)}
- **Reasoning:** {stage1_result.get('reasoning', 'N/A')}

**Stage 2 - Content Analysis:**
- **Remaining Terms:** {remaining_terms}
- **Products Found:** {total_results} รายการ
- **Analysis Method:** {"Deep Content Analysis" if remaining_terms else "Popularity Sorting"}

**TOP RECOMMENDATIONS:**
{products_info}

**RESPONSE INSTRUCTIONS:**
1. สร้างการแนะนำที่เป็นธรรมชาติ เหมือนพนักงานขายมืออาชีพ
2. อธิบายว่าทำไมแนะนำสินค้านี้ (highlight key selling points)
3. เปรียบเทียบตัวเลือกหากมีหลายตัว
4. ระบุข้อดี: ราคา, คะแนน, ความนิยม, ส่วนลด, สต็อก
5. ใช้ emoji เพื่อให้น่าสนใจ แต่ไม่มากเกินไป
6. **อธิบายกระบวนการค้นหา 2 ขั้นตอนในส่วนท้าย** (สำหรับความโปร่งใส)

**FORMAT:**
[การแนะนำสินค้าตามปกติ]

---
🔍 **Search Process:**
- **Stage 1:** กรอง {', '.join(used_terms) if used_terms else 'ไม่มี'} → MongoDB Query
- **Stage 2:** วิเคราะห์ {', '.join(remaining_terms) if remaining_terms else 'ไม่มี'} → Content Matching

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
        print(f"Two-stage response generation error: {error}")
        return generate_two_stage_fallback_response(user_input, products, stage1_result)

async def generate_two_stage_no_results(user_input: str, stage1_result: Dict[str, Any]) -> str:
    """Generate no results response with two-stage explanation"""
    processed_terms = stage1_result.get("processedTerms", {})
    used_terms = processed_terms.get("used", [])
    remaining_terms = processed_terms.get("remaining", [])
    
    response = "ขออภัย ไม่พบสินค้าที่ตรงกับความต้องการของคุณ 🔍\n\n"
    
    response += "💡 **ข้อเสนอแนะ:**\n"
    response += "• ลองเพิ่มงบประมาณ\n"
    response += "• ค้นหาด้วยชื่อสินค้าโดยตรง\n"
    response += "• ระบุความต้องการให้ชัดเจนมากขึ้น\n"
    response += "• ลองหมวดหมู่ที่เกี่ยวข้อง\n\n"
    
    response += "---\n"
    response += "🔍 **Search Process:**\n"
    response += f"- **Stage 1:** กรอง {', '.join(used_terms) if used_terms else 'ไม่มี'} → MongoDB Query\n"
    response += f"- **Stage 2:** วิเคราะห์ {', '.join(remaining_terms) if remaining_terms else 'ไม่มี'} → Content Matching\n"
    response += f"\n```json\n{json.dumps(stage1_result.get('query', {}), ensure_ascii=False, indent=2)}\n```"
    
    return response

def generate_two_stage_fallback_response(user_input: str, products: List[Product], stage1_result: Dict[str, Any]) -> str:
    """Fallback response generator for two-stage system"""
    if len(products) == 0:
        return f"ไม่พบสินค้าจาก query: {user_input} 🔍"
    
    top_product = products[0]
    total_results = len(products)
    processed_terms = stage1_result.get("processedTerms", {})
    used_terms = processed_terms.get("used", [])
    remaining_terms = processed_terms.get("remaining", [])
    
    response = f"พบสินค้าที่ตรงกับความต้องการ {total_results} รายการ 🛍️\n\n"
    response += f"⭐ **แนะนำ:** {top_product.title}\n"
    sale_price_formatted = f"฿{top_product.salePrice:,}"
    response += f"💰 **ราคา:** {sale_price_formatted}"
    
    discount = top_product.price - top_product.salePrice
    if discount > 0:
        discount_percent = round((discount / top_product.price) * 100)
        original_price_formatted = f"฿{top_product.price:,}"
        response += f" (ลด {discount_percent}% จาก {original_price_formatted})"
    
    response += f"\n📦 **คงเหลือ:** {top_product.stockQuantity} ชิ้น"
    response += f"\n⭐ **คะแนน:** {top_product.rating}/5 ({top_product.totalReviews} รีวิว)"
    views_formatted = f"{top_product.productView:,}"
    response += f"\n🔥 **ยอดนิยม:** {views_formatted} ครั้งเข้าชม"
    
    if top_product.freeShipping:
        response += "\n🚚 **ส่งฟรี**"
    
    if total_results > 1:
        response += f"\n\n📋 มีทั้งหมด {total_results} รายการให้เลือก!"
    
    response += "\n\n---\n"
    response += "🔍 **Search Process:**\n"
    response += f"- **Stage 1:** กรอง {', '.join(used_terms) if used_terms else 'ไม่มี'} → MongoDB Query\n"
    response += f"- **Stage 2:** วิเคราะห์ {', '.join(remaining_terms) if remaining_terms else 'ไม่มี'} → Content Matching"
    
    return response

# LLM Stage 3: Question Answerer for remaining question phrases
async def stage3_question_answerer(
    user_input: str,
    stage1_result: Dict[str, Any],
    selected_products: List[Product],
    remaining_questions: List[str]
) -> str:
    """
    Stage 3 LLM: Answer questions based on selected products
    Analyzes remaining question phrases and provides answers using product information
    """
    if not remaining_questions or len(selected_products) == 0:
        return ""
    
    print(f"[Stage 3] Answering questions: {remaining_questions}")
    
    # Prepare products info for analysis
    top_products = selected_products[:3]  # Analyze top 3 products
    products_info = ""
    for i, p in enumerate(top_products):
        products_info += f"""
Product {i + 1}: {p.title}
Price: ฿{p.salePrice:,}
Category: {p.cateName}
Description: {p.description[:300]}...
Rating: {p.rating}/5 ({p.totalReviews} reviews)
Stock: {p.stockQuantity}
"""
    
    prompt = f"""
คุณคือ IT Product Expert ที่เชี่ยวชาญในการตอบคำถามเกี่ยวกับสินค้า IT

**USER INPUT:** "{user_input}"
**QUESTION PHRASES TO ANSWER:** {remaining_questions}

**SELECTED PRODUCTS FOR ANALYSIS:**
{products_info}

**STAGE 3 MISSION:**
1. วิเคราะห์แต่ละคำถามใน remaining_questions
2. ตอบคำถามโดยอ้างอิงจากข้อมูลสินค้าที่ได้รับ
3. ใช้ความรู้ทั่วไปเกี่ยวกับ IT ประกอบการตอบ
4. ให้คำตอบที่มีประโยชน์และครอบคลุม

**QUESTION ANALYSIS GUIDELINES:**

**"เล่นเกมได้ไหม" / "gaming performance":**
- ดู CPU: Ryzen 5/7, Intel i5/i7 = เล่นเกมได้ดี
- ดู GPU: RTX/GTX series = เล่นเกมได้
- ดู RAM: 16GB+ = เหมาะสำหรับเกม
- ดูหมวดหมู่: Gaming Notebooks/Desktop = ออกแบบมาเล่นเกม

**"ใช้งานได้ไหม" / "performance questions":**
- วิเคราะห์สเปคตามการใช้งาน
- พิจารณาราคาและความคุ้มค่า
- แนะนำการใช้งานที่เหมาะสม

**"ดีไหม" / "quality questions":**
- ดูคะแนนรีวิว และจำนวนรีวิว
- ดูความนิยม (productView)
- เปรียบเทียบกับสินค้าอื่น

**ANSWER FORMAT:**
ตอบแต่ละคำถามในรูปแบบย่อหน้าที่ชัดเจน เป็นธรรมชาติ และให้ข้อมูลที่เป็นประโยชน์

ตอบคำถามที่ถูกถาม โดยใช้ข้อมูลจากสินค้าที่คัดเลือกมา:
"""

    try:
        global client
        if client is None:
            client = get_openai_client()
            
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as error:
        print(f"Stage 3 question answering error: {error}")
        return generate_stage3_fallback_answer(remaining_questions, selected_products)

def generate_stage3_fallback_answer(questions: List[str], products: List[Product]) -> str:
    """Fallback answer generator for Stage 3"""
    if not questions or not products:
        return ""
    
    answers = []
    top_product = products[0]
    
    for question in questions:
        if "เล่นเกม" in question and "ได้ไหม" in question:
            # Gaming capability assessment
            if any(keyword in top_product.title.lower() for keyword in ['gaming', 'rtx', 'gtx', 'ryzen', 'intel']):
                answers.append(f"✅ **{question}**: ใช่ เครื่องนี้เหมาะสำหรับเล่นเกม จากสเปคที่ดูแล้วน่าจะรับเกมส่วนใหญ่ได้")
            else:
                answers.append(f"⚠️ **{question}**: อาจเล่นเกมเบาๆ ได้ แต่เกมหนักอาจต้องลดคุณภาพกราฟิก")
        elif "ดีไหม" in question:
            # Quality assessment
            if top_product.rating >= 4:
                answers.append(f"⭐ **คุณภาพ**: ดี! ได้คะแนน {top_product.rating}/5 จาก {top_product.totalReviews} รีวิว")
            else:
                answers.append(f"📊 **คุณภาพ**: พอใช้ ได้คะแนน {top_product.rating}/5 จาก {top_product.totalReviews} รีวิว")
    
    return "\n\n".join(answers)

def extract_question_phrases(phrases: List[str]) -> List[str]:
    """Extract phrases that are questions (for Stage 3)"""
    question_phrases = []
    
    for phrase in phrases:
        if is_question_phrase(phrase):
            question_phrases.append(phrase)
    
    return question_phrases

def is_question_phrase(phrase: str) -> bool:
    """Check if phrase is a question that needs Stage 3 analysis"""
    phrase_lower = phrase.lower()
    
    question_patterns = [
        r'\w+ได้ไหม',      # เล่นเกมได้ไหม, ใช้งานได้ไหม
        r'\w+ดีไหม',       # ดีไหม
        r'เป็นอย่างไร',     # เป็นอย่างไร
        r'อย่างไร',        # อย่างไร
        r'ดีมั้ย',         # ดีมั้ย
        r'เอาไหม'          # เอาไหม
    ]
    
    for pattern in question_patterns:
        if re.search(pattern, phrase_lower):
            return True
    
    return False

# Export main functions
__all__ = [
    'stage1_basic_query_builder',
    'stage2_content_analyzer', 
    'stage3_question_answerer',
    'generate_two_stage_response',
    'normalize_text_advanced',
    'get_comprehensive_category_mapping',
    'is_non_filter_phrase',
    'extract_question_phrases',
    'is_question_phrase'
]