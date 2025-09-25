# agent/memory.py
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import uuid

class VectorMemory:
    def __init__(self, collection_name: str = "agent_memory"):
        # สร้าง ChromaDB client
        self.client = chromadb.Client(Settings(
            persist_directory="./data/chroma_db",
            chroma_db_impl="duckdb+parquet"
        ))
        
        # สร้างหรือโหลด collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )
    
    def add_memory(self, 
                   content: str, 
                   metadata: Dict[str, Any] = None) -> str:
        """เพิ่มความจำใหม่"""
        memory_id = str(uuid.uuid4())
        
        self.collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[memory_id]
        )
        
        return memory_id
    
    def search_memory(self, 
                      query: str, 
                      n_results: int = 5) -> List[Dict[str, Any]]:
        """ค้นหาความจำที่เกี่ยวข้อง"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        memories = []
        for i in range(len(results['documents'][0])):
            memories.append({
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })
        
        return memories
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """ดึงความจำล่าสุด"""
        # สำหรับตัวอย่างนี้ เราจะใช้การ query ทั่วไป
        # ในการใช้งานจริงควรเก็บ timestamp และเรียงลำดับ
        return self.search_memory("", n_results=limit)
