import os
import glob
import shutil

SANDBOX_ROOT = os.path.expanduser("~/jarvis-sandbox")

def ensure_sandbox():
    if not os.path.exists(SANDBOX_ROOT):
        os.makedirs(SANDBOX_ROOT)

def is_safe_path(target_path):
    """Ensures the target path is strictly inside the sandbox root to prevent path traversal."""
    target = os.path.abspath(target_path)
    return os.path.commonpath([SANDBOX_ROOT, target]) == SANDBOX_ROOT

def execute_create_file(slots):
    ensure_sandbox()
    filename = slots.get("filename", "")
    if not filename:
        return {"status": "error", "message": "Missing filename to create."}
        
    target_path = os.path.join(SANDBOX_ROOT, filename)
    if not is_safe_path(target_path):
        return {"status": "error", "message": "Cannot perform operations outside the sandbox."}
        
    try:
        with open(target_path, 'w') as f:
            f.write("") # Create empty file
        return {"status": "success", "message": f"Created file {filename}."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to create file: {e}"}

def execute_delete_file(slots):
    ensure_sandbox()
    filename = slots.get("filename", "")
    if not filename:
        return {"status": "error", "message": "Missing filename to delete."}
        
    target_path = os.path.join(SANDBOX_ROOT, filename)
    if not is_safe_path(target_path):
        return {"status": "error", "message": "Cannot perform operations outside the sandbox."}
        
    if not os.path.exists(target_path):
        return {"status": "error", "message": f"File {filename} does not exist."}
        
    try:
        os.remove(target_path)
        return {"status": "success", "message": f"Deleted file {filename}."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to delete file: {e}"}

def execute_move_file(slots):
    ensure_sandbox()
    filename = slots.get("filename", "")
    folder = slots.get("folder", "")
    if not filename or not folder:
        return {"status": "error", "message": "Missing filename or target folder."}
        
    source_path = os.path.join(SANDBOX_ROOT, filename)
    dest_dir = os.path.join(SANDBOX_ROOT, folder)
    dest_path = os.path.join(dest_dir, filename)
    
    if not is_safe_path(source_path) or not is_safe_path(dest_path):
        return {"status": "error", "message": "Cannot perform operations outside the sandbox."}
        
    if not os.path.exists(source_path):
        return {"status": "error", "message": f"Source file {filename} does not exist."}
        
    try:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        shutil.move(source_path, dest_path)
        return {"status": "success", "message": f"Moved {filename} to {folder}."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to move file: {e}"}

def execute_read_file(slots):
    ensure_sandbox()
    filename = slots.get("filename", "")
    if not filename:
        return {"status": "error", "message": "Missing filename to read."}
        
    target_path = os.path.join(SANDBOX_ROOT, filename)
    if not is_safe_path(target_path):
        return {"status": "error", "message": "Cannot perform operations outside the sandbox."}
        
    if not os.path.exists(target_path):
        return {"status": "error", "message": f"File {filename} does not exist."}
        
    try:
        with open(target_path, 'r') as f:
            content = f.read(500) # Read up to 500 chars
            if len(content) == 500:
                content += "... (truncated)"
        return {"status": "success", "message": f"Contents of {filename}: {content}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to read file: {e}"}

def execute_find_file(slots):
    ensure_sandbox()
    filename = slots.get("filename", "")
    if not filename:
        return {"status": "error", "message": "Missing filename to find."}
        
    try:
        # Search recursively in the sandbox
        search_pattern = os.path.join(SANDBOX_ROOT, "**", filename)
        matches = glob.glob(search_pattern, recursive=True)
        if matches:
            # Just return the first match relative to sandbox
            rel_path = os.path.relpath(matches[0], SANDBOX_ROOT)
            return {"status": "success", "message": f"Found {filename} at {rel_path}."}
        else:
            return {"status": "success", "message": f"Could not find {filename}."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to find file: {e}"}
