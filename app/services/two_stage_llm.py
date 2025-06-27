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

# Enhanced contextual phrase segmentation with better context analysis
def enhanced_contextual_phrase_segmentation(text: str) -> Dict[str, Any]:
    """
    Enhanced phrase segmentation with context analysis and phrase classification
    Returns segmented phrases with their types and processing stage assignments
    """
    import re
    
    # Normalize first
    normalized = normalize_text_advanced(text)
    
    # Initialize result structure
    result = {
        "original_text": text,
        "normalized_text": normalized,
        "segmented_phrases": [],
        "phrase_classification": {
            "filter_phrases": [],           # วลีที่ระบุ filter ได้ชัดเจน (Stage 1 only)
            "content_analysis_phrases": [], # วลีระบุสินค้าด้วยเนื้อหา (Stage 2)
            "question_phrases": [],         # วลีคำถาม/คำแนะนำ (Stage 3)
            "context_inferred_phrases": []  # วลีที่ต้องอนุมานจากบริบท (Stage 1 inference)
        },
        "stage_assignments": {
            "stage1_filter": [],
            "stage1_inference": [],
            "stage2_content": [],
            "stage3_questions": []
        }
    }
    
    # Enhanced phrase patterns with context awareness and priority
    phrase_patterns = [
        # HIGH PRIORITY: Clear filter phrases (Stage 1 - Direct filtering)
        {
            "pattern": r'(?:อยากได้|ต้องการ|หา|ซื้อ)\s*(โน้ตบุ๊ก|คอมพิวเตอร์|คอม|การ์ดจอ|เมาส์|คีย์บอร์ด|หูฟัง|จอ|ซีพียู|แรม)',
            "type": "PRODUCT_DESIRE_FILTER",
            "stage": "stage1_filter",
            "priority": 10
        },
        {
            "pattern": r'(โน้?[ตด]บุ๊?[กค]|คอมพิวเตอร์|คอมตั้งโต๊ะ|การ์ดจอ|เมาส์|คีย์บอร์ด|หูฟัง|จอมอนิเตอร์|ซีพียู|แรม|เครื่องพิมพ์)(?!\s*[เล่นทำใช้])',
            "type": "CATEGORY_FILTER",
            "stage": "stage1_filter", 
            "priority": 9
        },
        {
            "pattern": r'(?:งบ|ไม่เกิน|ประมาณ|ราคา|budget)[\s\w]*?(\d{1,3}(?:,\d{3})*|\d+)(?:\s*บาท|$)',
            "type": "BUDGET_FILTER",
            "stage": "stage1_filter",
            "priority": 9
        },
        {
            "pattern": r'ราคา[\s\w]*?(\d{1,3}(?:,\d{3})*|\d+)',
            "type": "BUDGET_FILTER",
            "stage": "stage1_filter",
            "priority": 9
        },
        
        # MEDIUM PRIORITY: Specific product names (Stage 1 - Category inference + Stage 2)
        {
            "pattern": r'(Ryzen\s*\d+\s*\d+\w*|Intel\s*Core\s*i\d+|RTX\s*\d+\w*|GTX\s*\d+\w*|AMD\s*\w*\d+\w*)',
            "type": "SPECIFIC_PRODUCT_NAME",
            "stage": "stage1_inference", # อนุมานหมวดหมู่ + ส่งไป Stage 2
            "priority": 8
        },
        {
            "pattern": r'(ASUS|HP|Dell|MSI|Acer|Lenovo|Apple|Razer|Logitech|Corsair|Gigabyte|EVGA)\s*[\w\s]*',
            "type": "BRAND_PRODUCT",
            "stage": "stage2_content",
            "priority": 7
        },
        
        # CONTENT ANALYSIS: Usage and application phrases (Stage 2)
        {
            "pattern": r'ทำงานกราฟิก',
            "type": "USAGE_GRAPHICS",
            "stage": "stage2_content",
            "priority": 9  # เพิ่ม priority เพื่อจับก่อน pattern อื่น
        },
        {
            "pattern": r'เล่นเกม\s*(?!ได้ไหม)[\w\s]*',
            "type": "USAGE_GAMING",
            "stage": "stage2_content",
            "priority": 8
        },
        {
            "pattern": r'(?:ทำงาน|ใช้งาน|สำหรับ)(?!กราฟิก)[\w\s]*(?=\s|$)',
            "type": "USAGE_GENERAL",
            "stage": "stage2_content", 
            "priority": 6
        },
        {
            "pattern": r'(?:ออฟฟิศ|เอกสาร|โปรแกรม|ซอฟต์แวร์)[\w\s]*',
            "type": "USAGE_OFFICE",
            "stage": "stage2_content",
            "priority": 6
        },
        
        # QUESTIONS: Request and question phrases (Stage 3)
        {
            "pattern": r'เล่นเกมได้ไหม',
            "type": "GAMING_QUESTION",
            "stage": "stage3_questions",
            "priority": 9
        },
        {
            "pattern": r'(?:แนะนำ|recommend)(?:\s*หน่อย|\s*ได้ไหม|\s*ดี)*',
            "type": "RECOMMENDATION_REQUEST",
            "stage": "stage3_questions",
            "priority": 8
        },
        {
            "pattern": r'ดีไหม|เป็นอย่างไร|ใช้ได้ไหม',
            "type": "GENERAL_QUESTION",
            "stage": "stage3_questions",
            "priority": 8  # เพิ่ม priority ให้สูงกว่า budget pattern
        },
        {
            "pattern": r'(?:รุ่นไหนดี|มีอะไรบ้าง|มีไหม)',
            "type": "PRODUCT_INQUIRY",
            "stage": "stage3_questions",
            "priority": 7
        },
        
        # SPECIFICATIONS (Stage 2)
        {
            "pattern": r'(?:\d+GB\s*(?:RAM|แรม)|mechanical|ไร้สาย|RGB|wireless)',
            "type": "SPECIFICATION",
            "stage": "stage2_content",
            "priority": 6
        }
    ]
    
    # Track processed text to avoid overlapping matches
    processed_text = normalized.lower()
    found_phrases = []
    
    # Sort patterns by priority (highest first)
    sorted_patterns = sorted(phrase_patterns, key=lambda x: x['priority'], reverse=True)
    
    # Extract phrases using prioritized patterns - เก็บ original text สำหรับ matching แต่ใช้ normalized text สำหรับ pattern
    original_text = text.lower()
    
    # Extract phrases using prioritized patterns
    for pattern_info in sorted_patterns:
        # ใช้ original text สำหรับ matching เพื่อให้จับ "ทำงานกราฟิก" ได้
        matches = re.finditer(pattern_info['pattern'], original_text, re.IGNORECASE)
        for match in matches:
            phrase = match.group().strip()
            if phrase and len(phrase) > 1:
                # Check for overlaps with higher priority phrases
                overlap = False
                for existing_phrase, _, _ in found_phrases:
                    # More strict overlap detection
                    if (len(phrase) > 5 and len(existing_phrase) > 5):
                        if (phrase.lower() in existing_phrase.lower() or 
                            existing_phrase.lower() in phrase.lower()):
                            overlap = True
                            break
                    elif phrase.lower() == existing_phrase.lower():
                        overlap = True
                        break
                
                if not overlap:
                    found_phrases.append((phrase, pattern_info['type'], pattern_info['stage']))
                    # Mark this position as used in original text
                    original_text = re.sub(re.escape(phrase.lower()), ' ' * len(phrase), original_text, count=1)
    
    # Initial processing of found phrases (will be overwritten by enhanced fallback)
    initial_phrases = found_phrases.copy()
    
    # Limited fallback: เฉพาะคำสำคัญที่ไม่ได้ถูกจับ
    remaining_text = re.sub(r'\s+', ' ', original_text).strip()
    important_words = re.findall(r'\b\w{4,}\b', remaining_text)  # เพิ่มความยาวขั้นต่ำ
    
    # Look for important unmatched terms - ลดจำนวน fallback
    existing_phrases_lower = [p[0].lower() for p in found_phrases]
    
    for word in important_words:
        if len(word) > 3 and word.lower() not in existing_phrases_lower:
            # เฉพาะคำที่สำคัญจริงๆ เท่านั้น
            if (word in ['ryzen', 'intel', 'rtx', 'gtx', 'asus', 'hp', 'dell', 'msi'] or
                re.match(r'\d{4,}', word)):  # ตัวเลข 4 หลักขึ้นไป (ราคา/รุ่น)
                found_phrases.append((word, "IMPORTANT_FALLBACK", "stage2_content"))
    
    # Re-process found phrases including fallbacks
    for phrase, phrase_type, stage in found_phrases:
        result["segmented_phrases"].append({
            "phrase": phrase,
            "type": phrase_type,
            "stage": stage,
            "original_text": phrase
        })
        
        # Classify by type
        if stage == "stage1_filter":
            result["phrase_classification"]["filter_phrases"].append(phrase)
            result["stage_assignments"]["stage1_filter"].append(phrase)
        elif stage == "stage1_inference":
            result["phrase_classification"]["context_inferred_phrases"].append(phrase) 
            result["stage_assignments"]["stage1_inference"].append(phrase)
        elif stage == "stage2_content":
            result["phrase_classification"]["content_analysis_phrases"].append(phrase)
            result["stage_assignments"]["stage2_content"].append(phrase)
        elif stage == "stage3_questions":
            result["phrase_classification"]["question_phrases"].append(phrase)
            result["stage_assignments"]["stage3_questions"].append(phrase)
    
    # Final fallback: if still no phrases found, create basic segmentation
    if not found_phrases:
        words = re.findall(r'\b\w{2,}\b', normalized)
        if words:
            # Try to identify at least one phrase for each potential stage
            basic_phrase = ' '.join(words)
            result["segmented_phrases"].append({
                "phrase": basic_phrase,
                "type": "FALLBACK_ANALYSIS",
                "stage": "stage2_content",
                "original_text": basic_phrase
            })
            result["phrase_classification"]["content_analysis_phrases"].append(basic_phrase)
            result["stage_assignments"]["stage2_content"].append(basic_phrase)
    
    return result

# Updated contextual_phrase_segmentation for backward compatibility
def contextual_phrase_segmentation(text: str) -> List[str]:
    """
    Backward compatible version - returns just the phrase list
    """
    analysis = enhanced_contextual_phrase_segmentation(text)
    return [item["phrase"] for item in analysis["segmented_phrases"]]

# Load database schema and categories
def load_database_schema():
    """Load actual database schema and categories"""
    schema_data = {}
    categories_data = []
    keyword_mapping = {}
    
    # Load schema.json
    try:
        schema_paths = ['backend/schema.json', '../backend/schema.json', './schema.json', 'schema.json']
        
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
        nav_paths = ['backend/navigation_attributes.json', '../backend/navigation_attributes.json', './navigation_attributes.json', 'navigation_attributes.json']
        
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
    
    # Load keyword_to_cateName.json (NEW!)
    try:
        keyword_paths = ['backend/keyword_to_cateName.json', '../backend/keyword_to_cateName.json', './keyword_to_cateName.json', 'keyword_to_cateName.json']
        
        for path in keyword_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    keyword_data = json.load(f)
                    # ใช้ categoryMapping structure ตาม user requirement
                    keyword_mapping = keyword_data.get("categoryMapping", keyword_data)
                    print(f"✅ Loaded keyword mapping from {path}")
                    break
            except FileNotFoundError:
                continue
    except Exception as e:
        print(f"Warning: Could not load keyword_to_cateName.json: {e}")
    
    return schema_data, categories_data, keyword_mapping

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

# LLM Stage 1: Context Analysis and Basic Query Builder
async def stage1_context_analysis_and_query_builder(user_input: str) -> Dict[str, Any]:
    """
    Stage 1 LLM: Context Analysis and Basic MongoDB Query Building
    
    NEW RESPONSIBILITIES:
    1. แยกวลีตามบริบท (Contextual Phrase Segmentation)
    2. วิเคราะห์แต่ละวลีและจัดหมวดหมู่:
       - วลีที่ระบุ filter ได้ชัดเจน → ใช้ทำ query
       - วลีที่ต้องอนุมานจากบริบท → อนุมานแล้วใช้ทำ query
       - วลีที่เป็นเนื้อหาสินค้า → ส่งไป Stage 2
       - วลีที่เป็นคำถาม/คำแนะนำ → ส่งไป Stage 3
    3. สร้าง MongoDB query จากวลีที่ระบุ filter ได้
    4. ส่งวลีที่เหลือไปให้ Stage อื่นๆ
    """
    print(f"[Stage 1] Processing input: {user_input}")
    
    # Enhanced phrase segmentation and analysis
    phrase_analysis = enhanced_contextual_phrase_segmentation(user_input)
    
    # Load database information
    schema_data, categories_data, keyword_mapping = load_database_schema()
    category_mapping = get_comprehensive_category_mapping()
    
    # Get actual database fields
    actual_fields = []
    if schema_data and 'properties' in schema_data:
        actual_fields = list(schema_data['properties'].keys())
    
    # Extract phrases for each stage
    stage1_filter_phrases = phrase_analysis["stage_assignments"]["stage1_filter"]
    stage1_inference_phrases = phrase_analysis["stage_assignments"]["stage1_inference"]
    stage2_content_phrases = phrase_analysis["stage_assignments"]["stage2_content"]
    stage3_question_phrases = phrase_analysis["stage_assignments"]["stage3_questions"]
    
    print(f"[Stage 1] Phrase Analysis:")
    print(f"  - Filter phrases: {stage1_filter_phrases}")
    print(f"  - Inference phrases: {stage1_inference_phrases}")
    print(f"  - Content phrases: {stage2_content_phrases}")
    print(f"  - Question phrases: {stage3_question_phrases}")
    
    # Convert data to strings to avoid f-string issues
    fields_str = str(actual_fields)
    categories_str = json.dumps(categories_data, ensure_ascii=False)
    mapping_str = json.dumps(category_mapping, ensure_ascii=False, indent=2)
    keyword_str = json.dumps(keyword_mapping, ensure_ascii=False, indent=2)
    
    # Create analysis summary for the LLM
    phrase_summary = {
        "stage1_filter": stage1_filter_phrases,
        "stage1_inference": stage1_inference_phrases,
        "stage2_content": stage2_content_phrases,
        "stage3_questions": stage3_question_phrases
    }
    phrase_summary_str = json.dumps(phrase_summary, ensure_ascii=False, indent=2)
    
    prompt = """
คุณคือ Stage 1 Context Analyzer และ Query Builder - วิเคราะห์บริบทและสร้าง MongoDB Query

**USER INPUT:** "{user_input}"

**PHRASE ANALYSIS RESULT:** {phrase_summary_str}

**DATABASE FIELDS:** {fields_str}
**AVAILABLE CATEGORIES:** {categories_str}
**CATEGORY MAPPING:** {mapping_str}
**KEYWORD TO CATEGORY MAPPING:** {keyword_str}""".format(
        user_input=user_input,
        phrase_summary_str=phrase_summary_str,
        fields_str=fields_str,
        categories_str=categories_str,
        mapping_str=mapping_str,
        keyword_str=keyword_str
    ) + """

**NEW STAGE 1 RESPONSIBILITIES:**
1. **รับผลการแยกวลี** - จากระบบ enhanced phrase segmentation
2. **วิเคราะห์วลี Stage 1 Filter** - วลีที่ระบุ filter ได้ชัดเจน
3. **วิเคราะห์วลี Stage 1 Inference** - วลีที่ต้องอนุมานหมวดหมู่
4. **สร้าง MongoDB Query** - จากวลีที่วิเคราะห์ได้
5. **ส่งวลีที่เหลือ** - ไปให้ Stage 2 และ 3

**ANALYSIS PROCESS:**

**Phase 1: วิเคราะห์วลี stage1_filter (ระบุ filter ได้ชัดเจน)**
- วลีเหล่านี้ควรนำมาสร้าง MongoDB query ทันที
- ตัวอย่าง: "อยากได้คอม", "โน้ตบุ๊ก", "งบ 20000"
- วิเคราะห์: หมวดหมู่ (cateName) และราคา (salePrice)

**Phase 2: วิเคราะห์วลี stage1_inference (ต้องอนุมานจากบริบท)**
- วลีที่เป็นชื่อผลิตภัณฑ์เฉพาะ แต่ต้องอนุมานหมวดหมู่
- ตัวอย่าง: "Ryzen 5 5600G" → อนุมาน CPU/Desktop PC/Notebooks
- วิเคราะห์แล้วเพิ่มเข้า query และส่งไป Stage 2 ด้วย

**Phase 3: ส่งวลีที่เหลือไปให้ Stage อื่น**
- stage2_content: วลีเนื้อหาสินค้า (แบรนด์, การใช้งาน, สเปค)
- stage3_questions: วลีคำถาม/คำแนะนำ

**RULES:**
- ใช้เฉพาะ: stockQuantity, cateName, salePrice
- ห้ามใช้: title, description, $regex, $or สำหรับ content
- ใช้ KEYWORD TO CATEGORY MAPPING เพื่อจับคู่คำไทย/อังกฤษกับ cateName
- **MONGODB SYNTAX**: 
  - Single: "cateName": "Notebooks"
  - Multiple: "cateName": {"$in": ["Desktop PC", "Notebooks"]}

**EXAMPLES:**

Input: "อยากได้คอมทำงานกราฟิก แนะนำหน่อย"
Analysis:
- stage1_filter: ["อยากได้คอม"] → cateName: {"$in": ["Desktop PC", "All in One PC (AIO)", "Computer Set JIB"]}
- stage2_content: ["ทำงานกราฟิก"] → ส่งไป Stage 2 
- stage3_questions: ["แนะนำหน่อย"] → ส่งไป Stage 3

Input: "โน้ตบุ๊ค ASUS งบ 20000"  
Analysis:
- stage1_filter: ["โน้ตบุ๊ก", "งบ 20000"] → cateName: "Notebooks", salePrice: {"$lte": 20000}
- stage2_content: ["ASUS"] → ส่งไป Stage 2

Input: "Ryzen 5 5600G เล่นเกมได้ไหม"
Analysis:
- stage1_inference: ["Ryzen 5 5600G"] → อนุมาน cateName: {"$in": ["CPU", "Desktop PC", "Notebooks"]}
- stage2_content: ["Ryzen 5 5600G"] → ส่งไป Stage 2 ด้วย (ชื่อเฉพาะ)
- stage3_questions: ["เล่นเกมได้ไหม"] → ส่งไป Stage 3

ตอบใน JSON:
{
  "mongoQuery": {
    "stockQuantity": {"$gt": 0}
    // เพิ่ม cateName และ salePrice ตามที่วิเคราะห์ได้
  },
  "processedTerms": {
    "stage1_filter_used": ["วลี stage1_filter ที่ใช้ทำ query"],
    "stage1_inference_used": ["วลี stage1_inference ที่อนุมานและใช้ทำ query"],
    "stage2_content_phrases": ["วลีส่งไป Stage 2"],
    "stage3_question_phrases": ["วลีส่งไป Stage 3"],
    "category": "หมวดหมู่ที่ระบุได้",
    "budget": {"max": number},
    "used": ["รวมวลีที่ใช้ใน Stage 1"],
    "remaining": ["รวมวลีส่งไป Stage 2+3"]
  },
  "reasoning": "อธิบายการวิเคราะห์แต่ละวลีและการตัดสินใจ",
  "queryType": "three_stage_analysis"
}
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
        
        # Enhanced return structure for 3-stage system
        processed_terms = result["processedTerms"]
        
        return {
            "query": validated_query,
            "processedTerms": processed_terms,
            "phraseAnalysis": phrase_analysis,
            "stageAssignments": {
                "stage1_filter": processed_terms.get("stage1_filter_used", []),
                "stage1_inference": processed_terms.get("stage1_inference_used", []),
                "stage2_content": processed_terms.get("stage2_content_phrases", []),
                "stage3_questions": processed_terms.get("stage3_question_phrases", [])
            },
            "reasoning": result.get("reasoning", "Stage 1 three-stage analysis"),
            "queryType": result.get("queryType", "three_stage_analysis"),
            "confidence": 0.8
        }
        
    except Exception as error:
        print(f"Stage 1 query generation error: {error}")
        # Enhanced fallback that includes phrase analysis
        fallback_result = generate_stage1_fallback_enhanced(user_input, phrase_analysis, categories_data)
        return fallback_result

def validate_stage1_query(query: Dict[str, Any], actual_fields: List[str]) -> Dict[str, Any]:
    """Validate Stage 1 query - only allow basic fields"""
    validated_query = {"stockQuantity": {"$gt": 0}}
    
    # Only allow these fields in Stage 1
    allowed_fields = ['stockQuantity', 'cateName', 'salePrice', 'cateId', 'categoryId']
    
    for key, value in query.items():
        if key in allowed_fields:
            validated_query[key] = value
    
    return validated_query

def generate_stage1_fallback_enhanced(input_text: str, phrase_analysis: Dict[str, Any], categories_data: List[str]) -> Dict[str, Any]:
    """Enhanced fallback for Stage 1 when LLM fails"""
    processed_terms = extract_basic_entities(input_text, categories_data)
    query = build_basic_query(processed_terms)
    
    # Try to extract stage assignments from phrase analysis if available
    stage_assignments = {
        "stage1_filter": [],
        "stage1_inference": [],
        "stage2_content": [],
        "stage3_questions": []
    }
    
    if phrase_analysis:
        stage_assignments = phrase_analysis.get("stage_assignments", stage_assignments)
    
    return {
        "query": query,
        "processedTerms": processed_terms,
        "phraseAnalysis": phrase_analysis,
        "stageAssignments": stage_assignments,
        "reasoning": "Stage 1 fallback - basic pattern matching with phrase analysis",
        "queryType": "three_stage_fallback",
        "confidence": 0.6
    }

def generate_stage1_fallback(input_text: str, categories_data: List[str]) -> Dict[str, Any]:
    """Legacy fallback for Stage 1 when LLM fails - backward compatibility"""
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
    
    # Load keyword mapping from file
    try:
        _, _, keyword_mapping = load_database_schema()
    except:
        keyword_mapping = {}
    
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
        
        # First try keyword mapping (more accurate)
        category_found = False
        # keyword_mapping structure: {"keyword": ["cateName1", "cateName2"]}
        for keyword, category_list in keyword_mapping.items():
            if keyword.lower() in phrase_lower:
                # category_list เป็น array ของ cateName
                for cateName in category_list:
                    if cateName in categories_data:  # Only consider available categories
                        found_categories.append(cateName)
                        if phrase not in processed_terms["used"]:
                            processed_terms["used"].append(phrase)
                        if phrase in processed_terms["remaining"]:
                            processed_terms["remaining"].remove(phrase)
                        category_found = True
                if category_found:
                    break
        
        # If not found in keyword mapping, try direct category matching
        if not category_found:
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
                        category_found = True
                        break
        
        # If still no category found, try to infer from product names
        if not category_found:
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
    Analyzes content-related phrases from Stage 1 and matches against title/description
    """
    if len(products) == 0:
        return []
    
    # Get content phrases from Stage 1's enhanced analysis
    stage_assignments = stage1_result.get("stageAssignments", {})
    content_phrases = stage_assignments.get("stage2_content", [])
    
    # Backward compatibility - if no stage assignments, use old method
    if not content_phrases:
        processed_terms = stage1_result.get("processedTerms", {})
        content_phrases = processed_terms.get("remaining", [user_input])
        used_terms = processed_terms.get("used", [])
    else:
        # Get used terms from Stage 1 filtering and inference
        used_terms = (stage_assignments.get("stage1_filter", []) + 
                     stage_assignments.get("stage1_inference", []))
    
    print(f"[Stage 2] Content phrases to analyze: {content_phrases}")
    print(f"[Stage 2] Stage 1 used terms: {used_terms}")
    
    # If no content phrases to analyze, just sort by popularity
    if not content_phrases or (len(content_phrases) == 1 and content_phrases[0] == user_input and not used_terms):
        print("[Stage 2] No specific content analysis needed - using popularity sorting")
        return sorted(products, 
                     key=lambda p: (p.productView, p.rating, -p.salePrice), 
                     reverse=True)[:8]
    
    print(f"[Stage 2] Analyzing {len(products)} products for content phrases: {content_phrases}")
    
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
- **Stage Assignments:** {json.dumps(stage_assignments, ensure_ascii=False, indent=2)}
- **Used Phrases (Stage 1 กรองแล้ว):** {used_terms}
- **Content Phrases (ให้ Stage 2 วิเคราะห์):** {content_phrases}
- **MongoDB Query Applied:** {json.dumps(stage1_result.get('query', {}), ensure_ascii=False)}
- **Stage 1 Reasoning:** {stage1_result.get('reasoning', 'N/A')}

**PRODUCTS TO ANALYZE:**
{products_info}

**STAGE 2 ANALYSIS MISSION:**
1. **วิเคราะห์ Content Phrases** - วลีที่ Stage 1 ส่งมาให้วิเคราะห์เนื้อหา
2. **ระบุประเภทข้อมูล** - แบรนด์ (title), สเปค/การใช้งาน (description), คุณสมบัติ (title+description)
3. **จับคู่เนื้อหา** - ค้นหาในฟิลด์ที่เหมาะสม (title สำหรับแบรนด์, description สำหรับการใช้งาน)
4. **ให้คะแนนความเหมาะสม** - 0-100 ตามความตรงกับ content phrases
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
- **Perfect Match** (90-100): ตรงทุกคำใน content phrases
- **Good Match** (70-89): ตรงส่วนใหญ่ของ content phrases  
- **Partial Match** (50-69): ตรงบางส่วนของ content phrases
- **Weak Match** (30-49): ตรงเล็กน้อยหรือคล้ายกัน
- **No Match** (0-29): ไม่ตรงเลย

**EXAMPLES:**

Content: ["ASUS"] → ดู title ว่ามี "ASUS" หรือไม่
Content: ["ทำงานกราฟิก"] → ดู description ว่าระบุสเปคทำงานกราฟิกได้หรือไม่  
Content: ["RGB", "mechanical"] → ดู title+description ว่ามีคำเหล่านี้หรือไม่
Content: ["Ryzen 5 5600G"] → ดู title ว่าผลิตภัณฑ์ไหนมีคำว่า "5600G" หรือ "RYZEN 5 5600G" ใน title
Content: ["RTX 4060"] → ดู title ว่าผลิตภัณฑ์ไหนมีคำว่า "RTX 4060" ใน title

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
  "analysisSummary": "สรุปการวิเคราะห์ content phrases",
  "unmatchedTerms": ["คำที่ไม่พบในสินค้าใดเลย"]
}}

**สำคัญ:** วิเคราะห์เฉพาะ content phrases ที่ Stage 1 ส่งมาให้วิเคราะห์เนื้อหา!
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
        
        # If no products matched content phrases, return top products by popularity
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