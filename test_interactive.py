# test_interactive.py (เวอร์ชันแก้ไขแล้ว)
import os
from dotenv import load_dotenv

# ⭐ โหลด environment variables ก่อนการ import อื่น ๆ
load_dotenv()

# ตรวจสอบ API key ก่อน
if not os.getenv("OPENAI_API_KEY"):
    print("❌ ไม่พบ OPENAI_API_KEY ในไฟล์ .env")
    print("💡 กรุณาสร้างไฟล์ .env และเพิ่ม:")
    print("   OPENAI_API_KEY=your_api_key_here")
    exit(1)

# ตอนนี้สามารถ import agent ได้แล้ว
from agent.core import AdvancedAgenticAI
import json

def interactive_test():
    """ทดสอบแบบโต้ตอบ"""
    print("🤖 เริ่มต้นทดสอบ Agentic AI")
    print("พิมพ์ 'quit' เพื่อออก")
    print("-" * 50)
    
    try:
        print("⏳ กำลังเริ่มต้น Agent...")
        agent = AdvancedAgenticAI()
        print("✅ Agent พร้อมใช้งาน!")
        
    except Exception as e:
        print(f"❌ ไม่สามารถเริ่มต้น Agent ได้: {e}")
        return
    
    while True:
        user_input = input("\n👤 คุณ: ")
        
        if user_input.lower() in ['quit', 'exit', 'ออก']:
            print("👋 ขอบคุณที่ใช้งาน!")
            break
        
        if user_input.strip():
            print("\n🤖 AI: กำลังประมวลผล...")
            
            try:
                response_data = agent.process(user_input)
                print(f"🤖 AI: {response_data['response']}")
                
                # แสดงข้อมูลเพิ่มเติม
                if response_data.get("planning_used"):
                    print(f"\n📋 ใช้การวางแผน: ใช่")
                    print(f"📊 คะแนนความซับซ้อน: {response_data['complexity_score']:.2f}")
                
                if response_data.get("actions_taken"):
                    print(f"⚡ การดำเนินการ: {', '.join(response_data['actions_taken'])}")
                    
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    interactive_test()