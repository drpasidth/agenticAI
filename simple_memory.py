# agent/simple_memory.py
from typing import List, Dict, Any
import uuid
from datetime import datetime
import json
import re

class SimpleVectorMemory:
    def __init__(self):
        self.memories = []
    
    def add_memory(self, 
                   content: str, 
                   metadata: Dict[str, Any] = None) -> str:
        """เพิ่มความจำใหม่"""
        memory_id = str(uuid.uuid4())
        
        memory = {
            'id': memory_id,
            'content': content,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat(),
            'keywords': self._extract_keywords(content)
        }
        
        self.memories.append(memory)
        return memory_id
    
    def search_memory(self, 
                      query: str, 
                      n_results: int = 5) -> List[Dict[str, Any]]:
        """ค้นหาความจำที่เกี่ยวข้อง (แบบง่าย)"""
        if not query.strip():
            return self.memories[-n_results:] if self.memories else []
        
        query_keywords = self._extract_keywords(query.lower())
        
        # คำนวณคะแนนความเกี่ยวข้อง
        scored_memories = []
        for memory in self.memories:
            score = self._calculate_similarity(query_keywords, memory['keywords'])
            if score > 0:
                scored_memories.append({
                    **memory,
                    'distance': 1 - score  # แปลงเป็น distance (ต่ำ = เกี่ยวข้องมาก)
                })
        
        # เรียงลำดับตามคะแนน
        scored_memories.sort(key=lambda x: x['distance'])
        
        return scored_memories[:n_results]
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """ดึงความจำล่าสุด"""
        return self.memories[-limit:] if self.memories else []
    
    def clear_memory(self):
        """ล้างความจำทั้งหมด"""
        self.memories = []
        print("ล้างความจำเรียบร้อยแล้ว")
    
    def get_collection_info(self):
        """ดูข้อมูลของ memory"""
        return {
            "name": "simple_memory",
            "count": len(self.memories)
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """แยกคำสำคัญจากข้อความ"""
        # ลบสัญลักษณ์พิเศษและแยกคำ
        words = re.findall(r'\b\w+\b', text.lower())
        
        # กรองคำที่สั้นเกินไป
        keywords = [word for word in words if len(word) >= 2]
        
        # ลบคำที่ซ้ำ
        return list(set(keywords))
    
    def _calculate_similarity(self, keywords1: List[str], keywords2: List[str]) -> float:
        """คำนวณความคล้ายคลึง (Jaccard similarity)"""
        if not keywords1 or not keywords2:
            return 0.0
        
        set1 = set(keywords1)
        set2 = set(keywords2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def save_to_file(self, filename: str = "memory_backup.json"):
        """บันทึกความจำลงไฟล์"""
        try:
            with open(f"data/{filename}", 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, ensure_ascii=False, indent=2)
            print(f"บันทึกความจำลงไฟล์ {filename} แล้ว")
        except Exception as e:
            print(f"บันทึกไฟล์ไม่สำเร็จ: {e}")
    
    def load_from_file(self, filename: str = "memory_backup.json"):
        """โหลดความจำจากไฟล์"""
        try:
            with open(f"data/{filename}", 'r', encoding='utf-8') as f:
                self.memories = json.load(f)
            print(f"โหลดความจำจากไฟล์ {filename} แล้ว ({len(self.memories)} รายการ)")
        except Exception as e:
            print(f"โหลดไฟล์ไม่สำเร็จ: {e}")