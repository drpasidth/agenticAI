# agent/tools.py
import requests
from bs4 import BeautifulSoup
import json
from typing import Dict, Any, List
from datetime import datetime

class ToolManager:
    def __init__(self):
        self.tools = {
            "web_search": self.web_search,
            "web_scrape": self.web_scrape,
            "calculator": self.calculator,
            "get_time": self.get_time,
            "save_note": self.save_note,
            "read_file": self.read_file
        }
    
    def get_available_tools(self) -> List[str]:
        """ดูเครื่องมือที่มี"""
        return list(self.tools.keys())
    
    def use_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """ใช้เครื่องมือ"""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"เครื่องมือ {tool_name} ไม่มีอยู่"
            }
        
        try:
            result = self.tools[tool_name](**kwargs)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def web_search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """ค้นหาข้อมูลจากเว็บ"""
        # ตัวอย่างการใช้ DuckDuckGo API (ฟรี)
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            
            results = []
            for topic in data.get('RelatedTopics', [])[:num_results]:
                if 'Text' in topic:
                    results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1],
                        'snippet': topic['Text'],
                        'url': topic.get('FirstURL', '')
                    })
            
            return results
        except Exception as e:
            return [{"error": f"การค้นหาล้มเหลว: {str(e)}"}]
    
    def web_scrape(self, url: str) -> Dict[str, str]:
        """ดึงเนื้อหาจากเว็บไซต์"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # ลบ script และ style tags
            for script in soup(["script", "style"]):
                script.decompose()
            
            # ดึงข้อความ
            text = soup.get_text()
            # ทำความสะอาดข้อความ
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return {
                'title': soup.title.string if soup.title else 'ไม่มีชื่อ',
                'content': text[:5000],  # จำกัดความยาว
                'url': url
            }
        except Exception as e:
            return {'error': f"ไม่สามารถดึงข้อมูลได้: {str(e)}"}
    
    def calculator(self, expression: str) -> float:
        """เครื่องคิดเลข"""
        try:
            # ใช้ eval อย่างปลอดภัย (ในการใช้งานจริงควรใช้ ast.literal_eval)
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                raise ValueError("มีตัวอักษรที่ไม่อนุญาต")
            
            result = eval(expression)
            return float(result)
        except Exception as e:
            raise Exception(f"ไม่สามารถคำนวณได้: {str(e)}")
    
    def get_time(self) -> str:
        """ดูเวลาปัจจุบัน"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def save_note(self, filename: str, content: str) -> str:
        """บันทึกโน๊ต"""
        try:
            with open(f"data/{filename}", 'w', encoding='utf-8') as f:
                f.write(content)
            return f"บันทึกไฟล์ {filename} เรียบร้อย"
        except Exception as e:
            raise Exception(f"ไม่สามารถบันทึกได้: {str(e)}")
    
    def read_file(self, filename: str) -> str:
        """อ่านไฟล์"""
        try:
            with open(f"data/{filename}", 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"ไม่สามารถอ่านไฟล์ได้: {str(e)}")