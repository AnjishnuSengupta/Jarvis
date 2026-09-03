import subprocess
import re

def linux_system_control(slots):
    action = slots.get("action", "")
    level_str = slots.get("level", "")
    
    if not action and not level_str:
        return {"status": "error", "message": "No system action specified."}
        
    try:
        if action == "lock":
            print("  [System-Linux] Locking screen...")
            subprocess.run(["loginctl", "lock-session"], check=True)
            return {"status": "success", "message": "Screen locked."}
            
        elif action == "sleep":
            print("  [System-Linux] Suspending...")
            subprocess.run(["systemctl", "suspend"], check=True)
            return {"status": "success", "message": "System going to sleep."}
            
        elif action == "brightness":
            print(f"  [System-Linux] Setting brightness to {level_str}...")
            # Requires brightnessctl
            subprocess.run(["brightnessctl", "set", f"{level_str}%"], check=True)
            return {"status": "success", "message": f"Brightness set to {level_str}%."}
            
        elif action in ["volume", "mute"]:
            if action == "mute" or "mute" in level_str:
                subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "mute"], check=True)
                return {"status": "success", "message": "System volume muted."}
                
            volume_val = None
            if "max" in level_str or "100" in level_str:
                volume_val = "100%"
            elif "half" in level_str or "50" in level_str:
                volume_val = "50%"
            else:
                match = re.search(r'(\d+)', level_str)
                if match:
                    volume_val = f"{match.group(1)}%"
                    
            if volume_val:
                print(f"  [System-Linux] Setting volume to {volume_val}...")
                subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "unmute"], check=True)
                subprocess.run(["amixer", "-D", "pulse", "sset", "Master", volume_val], check=True)
                return {"status": "success", "message": f"System volume set to {volume_val}."}
                
        return {"status": "error", "message": f"Could not understand system control instruction: {action} {level_str}"}
        
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"System command failed. Note: This requires amixer, loginctl, and brightnessctl on Linux."}
    except FileNotFoundError:
        return {"status": "error", "message": "Required system utilities not found on this Linux system."}
