import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class ConversationMemory:
    """จัดการ conversation memory และ context ต่อเนื่อง"""
    
    def __init__(self, timeout_minutes: int = 30):
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.timeout_minutes = timeout_minutes
    
    def get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        """สร้างหรือดึง conversation session"""
        if session_id not in self.conversations:
            self.conversations[session_id] = {
                "session_id": session_id,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "messages": [],
                "context": {
                    "last_query_type": None,
                    "last_categories": [],
                    "last_budget": None,
                    "user_preferences": {},
                    "pending_specs": None,  # สำหรับจัดสเปค
                    "comparison_items": []  # สำหรับเปรียบเทียบ
                },
                "consolidated_inputs": []  # เก็บ input ที่ติดกัน
            }
        
        # Update last activity
        self.conversations[session_id]["last_activity"] = datetime.now()
        return self.conversations[session_id]
    
    def add_message(self, session_id: str, user_input: str, bot_response: str, 
                   query_type: str = None, categories: List[str] = None, 
                   budget: Dict[str, Any] = None):
        """เพิ่มข้อความใน conversation"""
        session = self.get_or_create_session(session_id)
        
        message = {
            "timestamp": datetime.now(),
            "user_input": user_input,
            "bot_response": bot_response,
            "query_type": query_type,
            "categories": categories or [],
            "budget": budget
        }
        
        session["messages"].append(message)
        
        # Update context
        if query_type:
            session["context"]["last_query_type"] = query_type
        if categories:
            session["context"]["last_categories"] = categories
        if budget:
            session["context"]["last_budget"] = budget
        
        # Keep only last 10 messages to manage memory
        if len(session["messages"]) > 10:
            session["messages"] = session["messages"][-10:]
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """ดึง context ปัจจุบันของ conversation"""
        session = self.get_or_create_session(session_id)
        return session["context"]
    
    def get_recent_messages(self, session_id: str, count: int = 3) -> List[Dict[str, Any]]:
        """ดึงข้อความล่าสุด"""
        session = self.get_or_create_session(session_id)
        return session["messages"][-count:] if session["messages"] else []
    
    def cleanup_expired_sessions(self):
        """ลบ session ที่หมดอายุ"""
        cutoff_time = datetime.now() - timedelta(minutes=self.timeout_minutes)
        expired_sessions = [
            session_id for session_id, session in self.conversations.items()
            if session["last_activity"] < cutoff_time
        ]
        
        for session_id in expired_sessions:
            del self.conversations[session_id]
        
        return len(expired_sessions)

class InputConsolidator:
    """รวมและปรับปรุง input ที่ติดกันหรือซ้ำ"""
    
    def __init__(self, memory: ConversationMemory):
        self.memory = memory
        self.consolidation_timeout = 60  # seconds
    
    def should_consolidate(self, session_id: str, new_input: str) -> bool:
        """ตรวจสอบว่าควรรวม input หรือไม่"""
        recent_messages = self.memory.get_recent_messages(session_id, 2)
        
        if not recent_messages:
            return False
        
        last_message = recent_messages[-1]
        time_diff = (datetime.now() - last_message["timestamp"]).total_seconds()
        
        # ถ้าใหม่กว่า 60 วินาที และ input สั้น อาจเป็น continuation
        if time_diff < self.consolidation_timeout and len(new_input.strip()) < 50:
            return True
        
        # ตรวจสอบ continuation patterns
        continuation_patterns = [
            "สำหรับ", "เพื่อ", "ใช้", "ทำ", "เล่น", "งบ", "ราคา",
            "แล้ว", "และ", "หรือ", "ด้วย", "กับ"
        ]
        
        for pattern in continuation_patterns:
            if new_input.strip().startswith(pattern):
                return True
        
        return False
    
    def consolidate_input(self, session_id: str, new_input: str) -> str:
        """รวม input ใหม่กับ input ก่อนหน้า"""
        recent_messages = self.memory.get_recent_messages(session_id, 3)
        
        if not recent_messages:
            return new_input
        
        # หาข้อความที่เกี่ยวข้องจาก 3 ข้อความล่าสุด
        related_inputs = []
        
        for message in recent_messages:
            user_input = message["user_input"]
            
            # ตรวจสอบว่าเป็น input ที่เกี่ยวข้องหรือไม่
            if self._is_related_input(user_input, new_input):
                related_inputs.append(user_input)
        
        # รวม input
        if related_inputs:
            consolidated = " ".join(related_inputs + [new_input])
            return self._clean_consolidated_input(consolidated)
        
        return new_input
    
    def _is_related_input(self, old_input: str, new_input: str) -> bool:
        """ตรวจสอบว่า input เกี่ยวข้องกันหรือไม่"""
        old_lower = old_input.lower()
        new_lower = new_input.lower()
        
        # Category matching
        categories = ["คอม", "โน้ตบุ๊ก", "การ์ดจอ", "cpu", "ram", "ssd"]
        old_categories = [cat for cat in categories if cat in old_lower]
        new_categories = [cat for cat in categories if cat in new_lower]
        
        if old_categories and new_categories:
            return any(cat in old_categories for cat in new_categories)
        
        # Budget/spec continuation
        if ("งบ" in old_lower or "ราคา" in old_lower) and any(word in new_lower for word in ["สำหรับ", "เพื่อ", "ใช้", "เล่น"]):
            return True
        
        return False
    
    def _clean_consolidated_input(self, consolidated: str) -> str:
        """ทำความสะอาด input ที่รวมแล้ว"""
        # ลบคำซ้ำ
        words = consolidated.split()
        seen = set()
        cleaned_words = []
        
        for word in words:
            if word.lower() not in seen:
                cleaned_words.append(word)
                seen.add(word.lower())
        
        return " ".join(cleaned_words)

class SpecBuilder:
    """สร้างสเปคคอมพิวเตอร์และโน้ตบุ๊ก"""
    
    def __init__(self):
        self.spec_templates = {
            "gaming_desktop": {
                "name": "Gaming Desktop",
                "components": ["cpu", "gpu", "ram", "storage", "motherboard", "psu", "case"],
                "priorities": ["gpu", "cpu", "ram", "storage"]
            },
            "work_desktop": {
                "name": "Work Desktop", 
                "components": ["cpu", "ram", "storage", "motherboard", "psu", "case"],
                "priorities": ["cpu", "ram", "storage"]
            },
            "gaming_laptop": {
                "name": "Gaming Laptop",
                "components": ["cpu", "gpu", "ram", "storage", "display"],
                "priorities": ["gpu", "cpu", "ram"]
            },
            "work_laptop": {
                "name": "Work Laptop",
                "components": ["cpu", "ram", "storage", "display", "battery"],
                "priorities": ["cpu", "ram", "storage"]
            }
        }
    
    def detect_spec_request(self, user_input: str) -> Optional[Dict[str, Any]]:
        """ตรวจสอบว่าเป็นคำขอจัดสเปคหรือไม่"""
        input_lower = user_input.lower()
        
        spec_patterns = [
            r'จัดสเปค',
            r'จัดชุด',
            r'ชุดอุปกรณ์',
            r'สเปค.*?งบ',
            r'งบ.*?จัด'
        ]
        
        import re
        
        for pattern in spec_patterns:
            if re.search(pattern, input_lower):
                return self._extract_spec_requirements(user_input)
        
        return None
    
    def _extract_spec_requirements(self, user_input: str) -> Dict[str, Any]:
        """แยกความต้องการในการจัดสเปค"""
        import re
        
        input_lower = user_input.lower()
        requirements = {
            "type": "unknown",
            "usage": [],
            "budget": None,
            "preferences": []
        }
        
        # ตรวจสอบประเภท
        if any(word in input_lower for word in ["คอม", "desktop", "pc"]):
            if any(word in input_lower for word in ["เล่นเกม", "gaming"]):
                requirements["type"] = "gaming_desktop"
            else:
                requirements["type"] = "work_desktop"
        elif any(word in input_lower for word in ["โน้ตบุ๊ก", "laptop", "notebook"]):
            if any(word in input_lower for word in ["เล่นเกม", "gaming"]):
                requirements["type"] = "gaming_laptop"
            else:
                requirements["type"] = "work_laptop"
        
        # แยกการใช้งาน
        usage_patterns = {
            "gaming": ["เล่นเกม", "gaming", "เกม"],
            "work": ["ทำงาน", "work", "office"],
            "design": ["กราฟิก", "photoshop", "premiere", "design"],
            "programming": ["programming", "coding", "dev"],
            "streaming": ["streaming", "live", "stream"]
        }
        
        for usage_type, patterns in usage_patterns.items():
            if any(pattern in input_lower for pattern in patterns):
                requirements["usage"].append(usage_type)
        
        # แยกงบประมาณ
        budget_match = re.search(r'งบ\s*(\d+(?:,\d{3})*)', input_lower)
        if budget_match:
            requirements["budget"] = int(budget_match.group(1).replace(',', ''))
        
        return requirements

# Global instances
conversation_memory = ConversationMemory()
input_consolidator = InputConsolidator(conversation_memory)
spec_builder = SpecBuilder()