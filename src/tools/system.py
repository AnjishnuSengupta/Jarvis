import subprocess
import re

def execute_system_control(slots):
    level_str = slots.get("level", "").lower()
    
    if not level_str:
        return {"status": "error", "message": "No system level specified."}
        
    try:
        # Determine if it's volume or lock screen based on typical keywords
        if "lock" in level_str:
            # Try loginctl first (systemd)
            print("  [System] Locking screen...")
            subprocess.run(["loginctl", "lock-session"], check=True)
            return {"status": "success", "message": "Screen locked."}
            
        # Parse volume level
        volume_val = None
        if "mute" in level_str:
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "mute"], check=True)
            return {"status": "success", "message": "System volume muted.", "level": "muted"}
            
        elif "max" in level_str or "100" in level_str:
            volume_val = "100%"
        elif "half" in level_str or "50" in level_str:
            volume_val = "50%"
        else:
            # Try to extract a number
            match = re.search(r'(\d+)', level_str)
            if match:
                volume_val = f"{match.group(1)}%"
                
        if volume_val:
            print(f"  [System] Setting volume to {volume_val}...")
            # Unmute just in case, then set volume
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "unmute"], check=True)
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", volume_val], check=True)
            return {"status": "success", "message": f"System volume set to {volume_val}.", "level": volume_val}
            
        return {"status": "error", "message": f"Could not understand system control instruction: {level_str}"}
        
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"System command failed. Note: This requires amixer/loginctl on Linux."}
    except FileNotFoundError:
        return {"status": "error", "message": "Required system utilities (amixer, loginctl) not found."}
