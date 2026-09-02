import schedule
import time
import threading
import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "jarvis.db"))

def proactive_check():
    """A proactive check that runs periodically."""
    print("\n  [Scheduler] Running proactive checks...")
    
    # Example: Check if there are unreviewed flagged interactions
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interactions WHERE needs_review = 1 AND was_corrected = 0")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            print(f"  [Scheduler] Alert: {count} interaction(s) need your review! Run `python review.py`.")
            # In a full desktop app, this could send a notification to the UI via a WebSocket
    except Exception as e:
        print(f"  [Scheduler] Failed to check database: {e}")

def run_scheduler():
    """Runs the scheduling loop in a background thread."""
    schedule.every(5).minutes.do(proactive_check)
    # Also run once at startup
    proactive_check()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_background_scheduler():
    """Starts the scheduler in a daemon thread."""
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    return thread
