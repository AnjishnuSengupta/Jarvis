import os
import shutil
import time
from datetime import datetime, timedelta

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "workspace"))

def clean_workspace(days_old=7):
    if not os.path.exists(WORKSPACE_DIR):
        print(f"Workspace directory {WORKSPACE_DIR} does not exist. Nothing to clean.")
        return

    now = time.time()
    cutoff = now - (days_old * 86400)
    
    cleaned = 0
    for item in os.listdir(WORKSPACE_DIR):
        item_path = os.path.join(WORKSPACE_DIR, item)
        if os.path.isdir(item_path):
            stat = os.stat(item_path)
            # Check modification time
            if stat.st_mtime < cutoff:
                print(f"Removing old project: {item}")
                shutil.rmtree(item_path)
                cleaned += 1
                
    print(f"Cleaned {cleaned} old projects from the workspace.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Clean up old Jarvis workspace projects.")
    parser.add_argument("--days", type=int, default=7, help="Delete projects older than this many days.")
    args = parser.parse_args()
    clean_workspace(args.days)
