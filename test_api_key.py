# test_api_key.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def test_api_key():
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ ไม่พบ OPENAI_API_KEY ในไฟล์ .env")
            return
        
        if not api_key.startswith("sk-"):
            print("⚠️  API key รูปแบบไม่ถูกต้อง")
            return
            
        # ทดสอบเรียกใช้ API
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", max_tokens=10)
        response = llm.invoke("Hello")
        print("✅ API key ใช้งานได้!")
        print(f"📝 ทดสอบ response: {response.content}")
        
    except Exception as e:
        print(f"❌ API key ไม่ถูกต้องหรือมีปัญหา: {e}")

if __name__ == "__main__":
    test_api_key()