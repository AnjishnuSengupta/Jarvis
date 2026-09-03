import subprocess
import time

import platform

def execute_bluetooth_control(slots):
    device = slots.get("device", "").lower()
    
    if not device:
        # Generic turn on/off if no device specified
        try:
            print("  [Bluetooth] Powering on bluetooth adapter...")
            subprocess.run(["bluetoothctl", "power", "on"], check=True)
            return {"status": "success", "message": "Bluetooth adapter powered on."}
        except Exception:
            return {"status": "error", "message": "Failed to power on Bluetooth."}
            
    # Platform checks
    current_os = platform.system()
    
    if current_os == "Windows":
        return {"status": "error", "message": "Connecting to Bluetooth audio devices on Windows via script is unstable. Please use the Windows Settings app to connect."}
        
    if current_os != "Linux":
        return {"status": "error", "message": f"Bluetooth control not supported on {current_os}."}
        
    try:
        # Discover real MAC by matching name against paired devices
        result = subprocess.run(["bluetoothctl", "devices", "Paired"], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        
        mac_address = None
        for line in lines:
            if not line.startswith("Device"): continue
            parts = line.split(" ", 2)
            if len(parts) < 3: continue
            
            mac = parts[1]
            name = parts[2].lower()
            
            # Simple substring matching for "airpods" in "Anjishnu's AirPods"
            if device in name:
                mac_address = mac
                break
                
        if not mac_address:
            return {"status": "error", "message": f"Device '{device}' not found in paired devices list."}
            
        print(f"  [Bluetooth] Powering on adapter and connecting to {device} ({mac_address})...")
        subprocess.run(["bluetoothctl", "power", "on"], check=True, stdout=subprocess.DEVNULL)
        time.sleep(1)
        
        # Connect
        conn_result = subprocess.run(["bluetoothctl", "connect", mac_address], capture_output=True, text=True)
        if conn_result.returncode != 0:
            return {"status": "error", "message": f"Failed to connect: {conn_result.stderr.strip()}"}
            
        return {"status": "success", "message": f"Connection command sent to {device}.", "device": device}
        
    except FileNotFoundError:
        return {"status": "error", "message": "bluetoothctl command not found. Are you on Linux?"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to connect to {device}. {str(e)}"}
