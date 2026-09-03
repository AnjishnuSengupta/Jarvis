import platform

def execute_system_control(slots):
    current_os = platform.system()
    
    if current_os == "Linux":
        from src.tools.system_linux import linux_system_control
        return linux_system_control(slots)
    elif current_os == "Windows":
        from src.tools.system_windows import windows_system_control
        return windows_system_control(slots)
    else:
        return {"status": "error", "message": f"System control not supported on {current_os}."}
