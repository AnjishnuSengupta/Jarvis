import schedule
import time
import threading
import sqlite3
import os
import datetime
from src.tools.calendar import get_calendar_service

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "jarvis.db"))

CURRENT_NOTIFICATIONS = []

def get_current_notifications():
    """Returns the most recent notifications list."""
    return CURRENT_NOTIFICATIONS

def proactive_check():
    """A proactive check that runs periodically."""
    global CURRENT_NOTIFICATIONS
    print("\n  [Scheduler] Running proactive checks...")
    
    new_notifications = []
    
    # 1. Check if there are unreviewed flagged interactions
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interactions WHERE needs_review = 1 AND was_corrected = 0")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            msg = f"{count} interaction(s) need your review! Run `python review.py`."
            new_notifications.append(msg)
            print(f"  [Scheduler] Alert: {msg}")
    except Exception as e:
        print(f"  [Scheduler] Failed to check database: {e}")
        
    # 2. Check for upcoming calendar events in the next 15 minutes
    try:
        service = get_calendar_service()
        now = datetime.datetime.now(datetime.timezone.utc)
        in_15_mins = now + datetime.timedelta(minutes=15)
        
        timeMin = now.isoformat().replace('+00:00', 'Z')
        timeMax = in_15_mins.isoformat().replace('+00:00', 'Z')
        
        events_result = service.events().list(calendarId='primary', timeMin=timeMin,
                                            timeMax=timeMax, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])
        
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'Meeting')
            msg = f"Upcoming: '{summary}' starting soon."
            new_notifications.append(msg)
            print(f"  [Scheduler] Alert: {msg}")
    except Exception as e:
        print(f"  [Scheduler] Failed to check calendar: {e}")
        
    CURRENT_NOTIFICATIONS = new_notifications

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
