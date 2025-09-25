# agent/core.py (เวอร์ชันสมบูรณ์)
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from .simple_memory import SimpleVectorMemory as VectorMemory
from .tools import ToolManager
from .planner import TaskPlanner
from typing import List, Dict, Any
import json
from datetime import datetime

class AdvancedAgenticAI:
    def __init__(self, 
                 model_name: str = "gpt-3.5-turbo",
                 temperature: float = 0.7):
        # เริ่มต้น LLM
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature
        )
        
        # เริ่มต้นส่วนประกอบ
        self.memory = VectorMemory()
        self.tools = ToolManager()
        self.planner = TaskPlanner(self.llm)
        
        # หน่วยความจำชั่วคราว
        self.conversation_history = []
        
        self.system_prompt = """
        คุณเป็น Advanced AI Agent ที่มีความสามารถดังนี้:

        1. **การวิเคราะห์งาน**: แยกแยะงานซับซ้อนเป็นขั้นตอนย่อย
        2. **การใช้เครื่องมือ**: มีเครื่องมือหลากหลายให้ใช้งาน
        3. **หน่วยความจำ**: จดจำและค้นหาข้อมูลเก่า
        4. **การวางแผน**: สร้างและปฏิบัติตามแผน

        เครื่องมือที่มี: {tools}

        วิธีการทำงาน:
        1. รับรู้คำขอของผู้ใช้
        2. ค้นหาข้อมูลที่เกี่ยวข้องจากหน่วยความจำ
        3. กำหนดว่าต้องใช้เครื่องมือหรือไม่
        4. วางแผนการทำงาน
        5. ดำเนินการและรายงานผล

        กฎสำคัญ:
        - อธิบายเหตุผลในการตัดสินใจ
        - ใช้เครื่องมือเมื่อจำเป็น
        - บันทึกข้อมูลสำคัญ
        - ตอบเป็นภาษาไทยที่เข้าใจง่าย
        """
    
    def process(self, user_input: str, use_planning: bool = True) -> Dict[str, Any]:
        """ประมวลผลคำขอจากผู้ใช้"""
        
        # 1. บันทึกข้อความผู้ใช้
        self.conversation_history.append({
            "type": "user",
            "content": user_input,
            "timestamp": self._get_timestamp()
        })
        
        # 2. ค้นหาข้อมูลที่เกี่ยวข้อง
        related_memories = self.memory.search_memory(user_input, n_results=3)
        
        # 3. ตัดสินใจว่าต้องใช้ planning หรือไม่
        complexity_score = self._assess_complexity(user_input)
        
        response_data = {
            "user_input": user_input,
            "complexity_score": complexity_score,
            "related_memories": related_memories,
            "response": "",
            "actions_taken": [],
            "success": True
        }
        
        try:
            if use_planning and complexity_score > 0.7:
                # งานซับซ้อน ใช้ planning
                response_data.update(self._handle_complex_task(user_input, related_memories))
            else:
                # งานง่าย ตอบโดยตรง
                response_data.update(self._handle_simple_task(user_input, related_memories))
            
            # 4. บันทึกความจำ
            self.memory.add_memory(
                content=f"ผู้ใช้: {user_input}\nตอบ: {response_data['response']}",
                metadata={
                    "type": "conversation",
                    "timestamp": self._get_timestamp(),
                    "complexity": complexity_score
                }
            )
            
            # 5. บันทึกประวัติการสนทนา
            self.conversation_history.append({
                "type": "assistant",
                "content": response_data['response'],
                "timestamp": self._get_timestamp()
            })
            
        except Exception as e:
            response_data["success"] = False
            response_data["response"] = f"เกิดข้อผิดพลาด: {str(e)}"
        
        return response_data
    
    def _assess_complexity(self, task: str) -> float:
        """ประเมินความซับซ้อนของงาน"""
        complex_keywords = [
            'วิเคราะห์', 'เปรียบเทียบ', 'สร้างรายงาน', 'ค้นหา', 
            'คำนวณ', 'สรุป', 'แปล', 'ตรวจสอบ', 'จัดการ'
        ]
        
        score = 0.3  # base score
        
        # เพิ่มคะแนนตาม keyword
        for keyword in complex_keywords:
            if keyword in task:
                score += 0.2
        
        # เพิ่มคะแนนตามความยาว
        if len(task.split()) > 10:
            score += 0.2
        
        return min(score, 1.0)
    
    def _handle_simple_task(self, user_input: str, related_memories: List) -> Dict[str, Any]:
        """จัดการงานง่าย"""
        
        # สร้าง context จากความจำ
        context = self._build_context(related_memories)
        
        # สร้างข้อความ
        messages = [
            SystemMessage(content=self.system_prompt.format(
                tools=", ".join(self.tools.get_available_tools())
            )),
            HumanMessage(content=f"Context: {context}\n\nคำขอ: {user_input}")
        ]
        
        # ได้รับคำตอบ
        response = self.llm.invoke(messages)
        
        return {
            "response": response.content,
            "actions_taken": ["direct_response"],
            "planning_used": False
        }
    
    def _handle_complex_task(self, user_input: str, related_memories: List) -> Dict[str, Any]:
        """จัดการงานซับซ้อน"""
        
        # สร้างแผน
        plan = self.planner.create_plan(
            task=user_input,
            available_tools=self.tools.get_available_tools()
        )
        
        # ดำเนินการตามแผน
        execution_result = self.planner.execute_plan(plan, self.tools, self)
        
        # สร้างคำตอบ
        if execution_result['completed']:
            response = self._summarize_results(execution_result)
        else:
            response = f"ไม่สามารถดำเนินการให้เสร็จสิ้นได้ กรุณาดูรายละเอียดในผลการดำเนินงาน"
        
        return {
            "response": response,
            "actions_taken": ["planning", "execution"],
            "planning_used": True,
            "plan": plan,
            "execution_result": execution_result
        }
    
    def _build_context(self, memories: List) -> str:
        """สร้าง context จากความจำ"""
        if not memories:
            return "ไม่มีข้อมูลที่เกี่ยวข้องจากอดีต"
        
        context_parts = []
        for memory in memories:
            context_parts.append(f"- {memory['content']}")
        
        return "ข้อมูลที่เกี่ยวข้อง:\n" + "\n".join(context_parts)
    
    def _summarize_results(self, execution_result: Dict) -> str:
        """สรุปผลการดำเนินงาน"""
        successful_steps = [r for r in execution_result['results'] if r['success']]
        
        if not successful_steps:
            return "ไม่สามารถดำเนินการได้สำเร็จ"
        
        summary_parts = []
        summary_parts.append(f"เป้าหมาย: {execution_result['plan']['goal']}")
        summary_parts.append(f"ดำเนินการสำเร็จ {len(successful_steps)} ขั้นตอน")
        
        for step in successful_steps:
            summary_parts.append(f"✓ {step['description']}")
            if step['output']:
                summary_parts.append(f"  ผลลัพธ์: {str(step['output'])[:200]}")
        
        return "\n".join(summary_parts)
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_conversation_history(self) -> List[Dict]:
        """ดูประวัติการสนทนา"""
        return self.conversation_history
    
    def clear_conversation(self):
        """ล้างประวัติการสนทนา"""
        self.conversation_history = []
