import time
from src.tools.codegen import execute_codegen
from src.tools.system import execute_system_control
from src.tools.bluetooth import execute_bluetooth_control
from src.tools.memory import execute_memory_store, execute_memory_query
from src.tools.calendar import execute_schedule_meeting

def file_operation_tool(slots):
    filename = slots.get("filename", "file")
    folder = slots.get("folder", "current directory")
    return {"status": "success", "message": f"Operated on {filename} in {folder}"}

def general_chat_tool(slots):
    return {"status": "success", "message": "Hello! How can I help you today?"}

class ToolDispatcher:
    def __init__(self):
        self.tool_map = {
            "schedule_meeting": execute_schedule_meeting,
            "write_code": execute_codegen,
            "bluetooth_control": execute_bluetooth_control,
            "system_control": execute_system_control,
            "file_operation": file_operation_tool,
            "memory_query": execute_memory_query,
            "store_memory": execute_memory_store,
            "general_chat": general_chat_tool,
        }
        
    def dispatch(self, intent, slots):
        if intent in self.tool_map:
            print(f"  [Dispatcher] Executing tool for '{intent}' with args: {slots}")
            return self.tool_map[intent](slots)
        else:
            return {"status": "error", "message": f"No tool registered for intent: {intent}"}
