import asyncio
import time
from typing import Dict, Any
from app.services.conversation_manager import conversation_memory

class BackgroundTaskManager:
    """จัดการ background tasks สำหรับระบบ chatbot"""
    
    def __init__(self):
        self.running = False
        self.tasks = []
    
    async def start_background_tasks(self):
        """เริ่มต้น background tasks ทั้งหมด"""
        if self.running:
            return
        
        self.running = True
        
        # Start conversation memory cleanup task
        cleanup_task = asyncio.create_task(self.periodic_cleanup())
        self.tasks.append(cleanup_task)
        
        print("[Background] Started conversation memory cleanup task")
    
    async def stop_background_tasks(self):
        """หยุด background tasks ทั้งหมด"""
        self.running = False
        
        for task in self.tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.tasks.clear()
        print("[Background] Stopped all background tasks")
    
    async def periodic_cleanup(self):
        """ทำความสะอาด conversation memory เป็นระยะ"""
        while self.running:
            try:
                # Clean up expired conversations every 5 minutes
                await asyncio.sleep(300)  # 5 minutes
                
                expired_count = conversation_memory.cleanup_expired_sessions()
                if expired_count > 0:
                    print(f"[Cleanup] Removed {expired_count} expired conversation sessions")
                
            except asyncio.CancelledError:
                break
            except Exception as error:
                print(f"[Cleanup] Error in periodic cleanup: {error}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

# Global instance
background_manager = BackgroundTaskManager()

async def startup_background_tasks():
    """เริ่มต้น background tasks เมื่อ app เริ่ม"""
    await background_manager.start_background_tasks()

async def shutdown_background_tasks():
    """หยุด background tasks เมื่อ app ปิด"""
    await background_manager.stop_background_tasks()