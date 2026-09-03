import subprocess
import re
import ctypes
import sys

def set_windows_volume(volume_percent):
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        
        # Unmute if muted
        volume.SetMute(0, None)
        
        # volume_percent is 0-100, SetMasterVolumeLevelScalar takes 0.0-1.0
        scalar = max(0.0, min(1.0, float(volume_percent) / 100.0))
        volume.SetMasterVolumeLevelScalar(scalar, None)
        return True
    except ImportError:
        print("  [System-Windows] pycaw not installed.")
        return False
    except Exception as e:
        print(f"  [System-Windows] Volume error: {e}")
        return False

def mute_windows_volume():
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        
        volume.SetMute(1, None)
        return True
    except Exception as e:
        print(f"  [System-Windows] Mute error: {e}")
        return False

def set_windows_brightness(brightness_percent):
    try:
        import wmi
        wmi_obj = wmi.WMI(namespace='wmi')
        methods = wmi_obj.WmiMonitorBrightnessMethods()[0]
        methods.WmiSetBrightness(brightness_percent, 0)
        return True
    except ImportError:
        print("  [System-Windows] wmi not installed.")
        return False
    except Exception as e:
        print(f"  [System-Windows] Brightness error: {e}")
        return False

def windows_system_control(slots):
    action = slots.get("action", "")
    level_str = slots.get("level", "")
    
    if not action and not level_str:
        return {"status": "error", "message": "No system action specified."}
        
    try:
        if action == "lock":
            print("  [System-Windows] Locking screen...")
            ctypes.windll.user32.LockWorkStation()
            return {"status": "success", "message": "Screen locked."}
            
        elif action == "sleep":
            print("  [System-Windows] Suspending...")
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
            return {"status": "success", "message": "System going to sleep."}
            
        elif action == "brightness":
            match = re.search(r'(\d+)', level_str)
            if match:
                val = int(match.group(1))
                print(f"  [System-Windows] Setting brightness to {val}%...")
                if set_windows_brightness(val):
                    return {"status": "success", "message": f"Brightness set to {val}%."}
                else:
                    return {"status": "error", "message": "Failed to set Windows brightness."}
            return {"status": "error", "message": "No brightness level specified."}
            
        elif action in ["volume", "mute"]:
            if action == "mute" or "mute" in level_str:
                if mute_windows_volume():
                    return {"status": "success", "message": "System volume muted."}
                return {"status": "error", "message": "Failed to mute Windows volume."}
                
            volume_val = None
            if "max" in level_str or "100" in level_str:
                volume_val = 100
            elif "half" in level_str or "50" in level_str:
                volume_val = 50
            else:
                match = re.search(r'(\d+)', level_str)
                if match:
                    volume_val = int(match.group(1))
                    
            if volume_val is not None:
                print(f"  [System-Windows] Setting volume to {volume_val}%...")
                if set_windows_volume(volume_val):
                    return {"status": "success", "message": f"System volume set to {volume_val}%."}
                else:
                    return {"status": "error", "message": "Failed to set Windows volume."}
                    
        return {"status": "error", "message": f"Could not understand system control instruction: {action} {level_str}"}
        
    except Exception as e:
        return {"status": "error", "message": f"Windows system command failed: {e}"}
