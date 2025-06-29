import json
import re
from typing import Dict, List, Any, Optional, Tuple
from app.models import Product

class SpecManager:
    """จัดการการจัดสเปคคอมพิวเตอร์และโน้ตบุ๊ค"""
    
    def __init__(self):
        self.spec_templates = {
            "gaming_desktop": {
                "name": "Gaming Desktop",
                "budget_ranges": {
                    "budget": (15000, 30000),
                    "mid": (30000, 60000), 
                    "high": (60000, 100000),
                    "extreme": (100000, 200000)
                },
                "components": {
                    "cpu": {"priority": 2, "budget_ratio": 0.20},
                    "gpu": {"priority": 1, "budget_ratio": 0.35},
                    "ram": {"priority": 3, "budget_ratio": 0.15},
                    "storage": {"priority": 4, "budget_ratio": 0.10},
                    "motherboard": {"priority": 5, "budget_ratio": 0.08},
                    "psu": {"priority": 6, "budget_ratio": 0.07},
                    "case": {"priority": 7, "budget_ratio": 0.05}
                }
            },
            "work_desktop": {
                "name": "Work Desktop",
                "budget_ranges": {
                    "budget": (10000, 25000),
                    "mid": (25000, 50000),
                    "high": (50000, 80000)
                },
                "components": {
                    "cpu": {"priority": 1, "budget_ratio": 0.30},
                    "ram": {"priority": 2, "budget_ratio": 0.20},
                    "storage": {"priority": 3, "budget_ratio": 0.15},
                    "motherboard": {"priority": 4, "budget_ratio": 0.12},
                    "psu": {"priority": 5, "budget_ratio": 0.10},
                    "case": {"priority": 6, "budget_ratio": 0.08},
                    "gpu": {"priority": 7, "budget_ratio": 0.05}
                }
            },
            "gaming_laptop": {
                "name": "Gaming Laptop",
                "budget_ranges": {
                    "budget": (25000, 40000),
                    "mid": (40000, 70000),
                    "high": (70000, 120000),
                    "extreme": (120000, 200000)
                },
                "key_specs": ["cpu", "gpu", "ram", "storage", "display", "cooling"]
            },
            "work_laptop": {
                "name": "Work Laptop", 
                "budget_ranges": {
                    "budget": (15000, 30000),
                    "mid": (30000, 50000),
                    "high": (50000, 80000)
                },
                "key_specs": ["cpu", "ram", "storage", "display", "battery", "portability"]
            },
            "streaming_setup": {
                "name": "Live Streaming Setup",
                "components": {
                    "camera": {"priority": 1, "budget_ratio": 0.25},
                    "microphone": {"priority": 2, "budget_ratio": 0.20},
                    "lighting": {"priority": 3, "budget_ratio": 0.15},
                    "capture_card": {"priority": 4, "budget_ratio": 0.15},
                    "audio_interface": {"priority": 5, "budget_ratio": 0.10},
                    "accessories": {"priority": 6, "budget_ratio": 0.15}
                }
            },
            "pos_system": {
                "name": "POS System",
                "components": {
                    "tablet_pc": {"priority": 1, "budget_ratio": 0.40},
                    "receipt_printer": {"priority": 2, "budget_ratio": 0.20},
                    "cash_drawer": {"priority": 3, "budget_ratio": 0.15},
                    "barcode_scanner": {"priority": 4, "budget_ratio": 0.15},
                    "card_reader": {"priority": 5, "budget_ratio": 0.10}
                }
            }
        }
        
        self.usage_patterns = {
            "gaming": {
                "keywords": ["เล่นเกม", "gaming", "เกม", "lol", "valorant", "pubg", "cyberpunk", "gta"],
                "preferred_type": "gaming"
            },
            "work_office": {
                "keywords": ["ทำงาน", "office", "excel", "word", "ออฟฟิศ"],
                "preferred_type": "work"
            },
            "content_creation": {
                "keywords": ["photoshop", "premiere", "video", "edit", "render", "youtuber", "content"],
                "preferred_type": "work"
            },
            "programming": {
                "keywords": ["programming", "coding", "dev", "python", "java", "code"],
                "preferred_type": "work"
            },
            "streaming": {
                "keywords": ["streaming", "live", "stream", "broadcast"],
                "preferred_type": "streaming_setup"
            }
        }
    
    def detect_spec_request(self, user_input: str) -> Optional[Dict[str, Any]]:
        """ตรวจจับคำขอจัดสเปค"""
        input_lower = user_input.lower()
        
        # Spec building patterns
        spec_patterns = [
            r'จัดสเปค',
            r'จัดชุด', 
            r'ชุดอุปกรณ์',
            r'สเปค.*?งบ',
            r'งบ.*?จัด',
            r'ระบบ.*?งบ'
        ]
        
        is_spec_request = any(re.search(pattern, input_lower) for pattern in spec_patterns)
        
        if is_spec_request:
            return self._extract_spec_requirements(user_input)
        
        return None
    
    def _extract_spec_requirements(self, user_input: str) -> Dict[str, Any]:
        """แยกความต้องการการจัดสเปค"""
        input_lower = user_input.lower()
        
        requirements = {
            "type": "unknown",
            "usage": [],
            "budget": None,
            "budget_range": None,
            "preferences": [],
            "specific_needs": []
        }
        
        # ตรวจสอบประเภทอุปกรณ์
        if any(word in input_lower for word in ["pos", "ขายของ", "ร้านอาหาร", "ร้านค้า"]):
            requirements["type"] = "pos_system"
        elif any(word in input_lower for word in ["streaming", "live", "stream"]):
            requirements["type"] = "streaming_setup"
        elif any(word in input_lower for word in ["คอม", "desktop", "pc"]):
            requirements["type"] = "desktop"
        elif any(word in input_lower for word in ["โน้ตบุ๊ก", "โน๊ตบุ๊ค", "laptop", "notebook"]):
            requirements["type"] = "laptop"
        
        # ตรวจสอบการใช้งาน
        for usage_type, config in self.usage_patterns.items():
            if any(keyword in input_lower for keyword in config["keywords"]):
                requirements["usage"].append(usage_type)
        
        # กำหนดประเภทสเปคขั้นสุดท้าย
        if requirements["type"] in ["desktop", "laptop"]:
            if "gaming" in requirements["usage"]:
                requirements["type"] = f"gaming_{requirements['type']}"
            else:
                requirements["type"] = f"work_{requirements['type']}"
        
        # แยกงบประมาณ
        budget_patterns = [
            r'งบ\s*(\d+(?:,\d{3})*)',
            r'budget\s*(\d+(?:,\d{3})*)',
            r'(\d+(?:,\d{3})*)\s*บาท',
            r'(\d+(?:,\d{3})*)\s*-\s*(\d+(?:,\d{3})*)'  # Range pattern
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, input_lower)
            if match:
                if len(match.groups()) > 1 and match.group(2):  # Range budget
                    min_budget = int(match.group(1).replace(',', ''))
                    max_budget = int(match.group(2).replace(',', ''))
                    requirements["budget_range"] = (min_budget, max_budget)
                    requirements["budget"] = max_budget  # Use max for planning
                else:
                    requirements["budget"] = int(match.group(1).replace(',', ''))
                break
        
        # ตรวจสอบความต้องการเฉพาะ
        specific_needs = {
            "portable": ["เบา", "พกพา", "เดินทาง", "น้ำหนักเบา"],
            "quiet": ["เงียบ", "ไม่มีเสียง", "quiet"],
            "rgb": ["rgb", "สีสัน", "แสงไฟ"],
            "upgrade": ["อัพเกรด", "upgrade", "ขยาย"]
        }
        
        for need_type, keywords in specific_needs.items():
            if any(keyword in input_lower for keyword in keywords):
                requirements["specific_needs"].append(need_type)
        
        return requirements

class ComparisonManager:
    """จัดการการเปรียบเทียบสินค้า"""
    
    def __init__(self):
        self.comparison_patterns = {
            "vs_pattern": r'(.+?)\s*(?:vs|กับ|เทียบ)\s*(.+?)(?:\s|$)',
            "which_better": r'(.+?)\s*ตัวไหน(?:ดี|เก่ง|เร็ว)(?:กว่า|ที่สุด)',
            "difference": r'(.+?)\s*ต่างกัน(?:แค่ไหน|มาก|มั้ย|ไหม)',
            "recommend_budget": r'(.+?)\s*(?:ใน|งบ)\s*(\d+(?:,\d{3})*)\s*(?:เลือก|แนะนำ)'
        }
        
        self.component_categories = {
            "cpu": ["cpu", "processor", "ryzen", "intel", "i3", "i5", "i7", "i9"],
            "gpu": ["gpu", "การ์ดจอ", "rtx", "gtx", "radeon", "rx"],
            "ram": ["ram", "แรม", "memory", "ddr4", "ddr5"],
            "storage": ["ssd", "hdd", "nvme", "sata", "storage"],
            "laptop": ["โน้ตบุ๊ก", "laptop", "notebook", "macbook", "thinkpad"],
            "monitor": ["จอ", "monitor", "display", "ips", "va", "tn"]
        }
    
    def detect_comparison_request(self, user_input: str) -> Optional[Dict[str, Any]]:
        """ตรวจจับคำขอเปรียบเทียบ"""
        input_lower = user_input.lower()
        
        for pattern_name, pattern in self.comparison_patterns.items():
            match = re.search(pattern, input_lower)
            if match:
                return self._extract_comparison_details(user_input, pattern_name, match)
        
        return None
    
    def _extract_comparison_details(self, user_input: str, pattern_type: str, match) -> Dict[str, Any]:
        """แยกรายละเอียดการเปรียบเทียบ"""
        comparison = {
            "type": pattern_type,
            "items": [],
            "category": "unknown",
            "context": user_input,
            "budget": None,
            "usage": []
        }
        
        if pattern_type == "vs_pattern":
            comparison["items"] = [match.group(1).strip(), match.group(2).strip()]
        elif pattern_type == "recommend_budget":
            comparison["items"] = [match.group(1).strip()]
            comparison["budget"] = int(match.group(2).replace(',', ''))
        else:
            comparison["items"] = [match.group(1).strip()]
        
        # ตรวจสอบหมวดหมู่
        input_lower = user_input.lower()
        for category, keywords in self.component_categories.items():
            if any(keyword in input_lower for keyword in keywords):
                comparison["category"] = category
                break
        
        # ตรวจสอบการใช้งาน
        usage_keywords = {
            "gaming": ["เล่นเกม", "gaming", "เกม"],
            "work": ["ทำงาน", "work", "office"],
            "content": ["video", "editing", "render", "photoshop"]
        }
        
        for usage, keywords in usage_keywords.items():
            if any(keyword in input_lower for keyword in keywords):
                comparison["usage"].append(usage)
        
        return comparison

class TroubleshootingManager:
    """จัดการคำถามเกี่ยวกับการแก้ปัญหา"""
    
    def __init__(self):
        self.problem_patterns = {
            "boot_issue": {
                "keywords": ["เปิดไม่ติด", "boot", "บูต", "เปิดเครื่องไม่ได้"],
                "symptoms": ["เสียงบีบ", "จอดับ", "ไฟไม่ติด", "หน้าจอดำ"]
            },
            "performance": {
                "keywords": ["ช้า", "lag", "กระตุก", "fps ต่ำ", "ค้าง"],
                "symptoms": ["เกมกระตุก", "โหลดนาน", "แอปค้าง"]
            },
            "display": {
                "keywords": ["จอฟ้า", "blue screen", "จอดับ", "สีผิด"],
                "symptoms": ["จอฟ้า", "no signal", "สีเพี้ยน"]
            },
            "temperature": {
                "keywords": ["ร้อน", "hot", "temperature", "เป่าลมแรง"],
                "symptoms": ["เครื่องร้อน", "fan เสียงดัง", "shutdown เอง"]
            }
        }
        
        self.compatibility_patterns = {
            "cpu_mb": r'cpu\s*(.+?)\s*(?:ใช้กับ|กับ)\s*(?:mainboard|mb|เมนบอร์ด)\s*(.+)',
            "gpu_psu": r'(?:การ์ดจอ|gpu)\s*(.+?)\s*(?:ใช้กับ|กับ)\s*(?:psu|power|แหล่งจ่าย)\s*(.+)',
            "ram_mb": r'ram\s*(.+?)\s*(?:ใช้กับ|กับ)\s*(?:mainboard|mb)\s*(.+)'
        }
    
    def detect_troubleshooting_request(self, user_input: str) -> Optional[Dict[str, Any]]:
        """ตรวจจับคำถามเกี่ยวกับการแก้ปัญหา"""
        input_lower = user_input.lower()
        
        # ตรวจสอบคำถามแก้ปัญหา
        for problem_type, config in self.problem_patterns.items():
            if any(keyword in input_lower for keyword in config["keywords"]):
                return {
                    "type": "troubleshooting",
                    "problem_type": problem_type,
                    "description": user_input,
                    "keywords": config["keywords"]
                }
        
        # ตรวจสอบคำถามความเข้ากันได้
        for compat_type, pattern in self.compatibility_patterns.items():
            match = re.search(pattern, input_lower)
            if match:
                return {
                    "type": "compatibility",
                    "compatibility_type": compat_type,
                    "component1": match.group(1).strip(),
                    "component2": match.group(2).strip(),
                    "description": user_input
                }
        
        # ตรวจสอบคำถามการอัพเกรด
        upgrade_patterns = [
            r'อัพเกรด.*?จาก\s*(.+?)\s*เป็น\s*(.+)',
            r'เปลี่ยน.*?จาก\s*(.+?)\s*เป็น\s*(.+)',
            r'เพิ่ม\s*(.+?)\s*จาก\s*(.+?)\s*เป็น\s*(.+)'
        ]
        
        for pattern in upgrade_patterns:
            match = re.search(pattern, input_lower)
            if match:
                return {
                    "type": "upgrade",
                    "from_component": match.group(1).strip(),
                    "to_component": match.group(2).strip(),
                    "description": user_input
                }
        
        return None

# Global instances
spec_manager = SpecManager()
comparison_manager = ComparisonManager()
troubleshooting_manager = TroubleshootingManager()