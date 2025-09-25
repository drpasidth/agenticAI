# agent/planner.py
from typing import List, Dict, Any
import json
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

class TaskPlanner:
    def __init__(self, llm):
        self.llm = llm
        self.planning_prompt = """
        คุณเป็นผู้วางแผนที่ฉลาด ได้รับงานจากผู้ใช้แล้วแบ่งออกเป็นขั้นตอนย่อย ๆ
        
        เครื่องมือที่มี: {tools}
        
        ให้คุณวิเคราะห์งานและสร้างแผนเป็น JSON format:
        {{
            "goal": "เป้าหมายหลัก",
            "steps": [
                {{
                    "step": 1,
                    "description": "คำอธิบายขั้นตอน",
                    "tool": "เครื่องมือที่ใช้ (หากมี)",
                    "parameters": {{"key": "value"}},
                    "expected_output": "ผลลัพธ์ที่คาดหวัง"
                }}
            ],
            "success_criteria": "เงื่อนไขความสำเร็จ"
        }}
        
        งานที่ได้รับ: {task}
        """
    
    def create_plan(self, task: str, available_tools: List[str]) -> Dict[str, Any]:
        """สร้างแผนการทำงาน"""
        prompt = self.planning_prompt.format(
            tools=", ".join(available_tools),
            task=task
        )
        
        messages = [SystemMessage(content=prompt)]
        response = self.llm(messages)
        
        try:
            # แยก JSON จาก response
            content = response.content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            else:
                json_str = content
            
            plan = json.loads(json_str)
            return plan
        except Exception as e:
            # ถ้า parse ไม่ได้ให้สร้างแผนง่าย ๆ
            return {
                "goal": task,
                "steps": [
                    {
                        "step": 1,
                        "description": f"ทำงาน: {task}",
                        "tool": None,
                        "parameters": {},
                        "expected_output": "ผลลัพธ์ตามที่ร้องขอ"
                    }
                ],
                "success_criteria": "งานเสร็จสมบูรณ์"
            }
    
    def execute_plan(self, plan: Dict[str, Any], tool_manager, agent) -> Dict[str, Any]:
        """ดำเนินการตามแผน"""
        results = []
        
        for step in plan['steps']:
            print(f"กำลังดำเนินการขั้นตอนที่ {step['step']}: {step['description']}")
            
            step_result = {
                "step": step['step'],
                "description": step['description'],
                "success": False,
                "output": None,
                "error": None
            }
            
            try:
                if step.get('tool'):
                    # ใช้เครื่องมือ
                    tool_result = tool_manager.use_tool(
                        step['tool'], 
                        **step.get('parameters', {})
                    )
                    
                    if tool_result['success']:
                        step_result['success'] = True
                        step_result['output'] = tool_result['result']
                    else:
                        step_result['error'] = tool_result['error']
                else:
                    # ทำงานโดยตรง
                    response = agent.llm([HumanMessage(content=step['description'])])
                    step_result['success'] = True
                    step_result['output'] = response.content
                
            except Exception as e:
                step_result['error'] = str(e)
            
            results.append(step_result)
            
            # ถ้าขั้นตอนล้มเหลวให้หยุด
            if not step_result['success']:
                break
        
        return {
            "plan": plan,
            "results": results,
            "completed": all(r['success'] for r in results)
        }