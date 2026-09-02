import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
CREDS_FILE = os.path.join(DATA_DIR, "credentials.json")
TOKEN_FILE = os.path.join(DATA_DIR, "token.json")

def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS_FILE):
                raise FileNotFoundError(f"Missing {CREDS_FILE}. Please download OAuth client ID from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            
    service = build('calendar', 'v3', credentials=creds)
    return service

def execute_schedule_meeting(slots):
    name = slots.get("name", "someone")
    dt = slots.get("time", "sometime")
    
    if not name or not dt:
        return {"status": "error", "message": "Missing name or time for the meeting."}
        
    try:
        service = get_calendar_service()
        
        # In a real assistant, you would parse `dt` (e.g. "tomorrow 4pm") into an ISO format datetime.
        # Since we are keeping it simple, we will just use the current time + 1 hour as a placeholder,
        # but put the original request in the description.
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        start_time = now.isoformat() + 'Z'
        end_time = (now + datetime.timedelta(hours=1)).isoformat() + 'Z'
        
        event = {
            'summary': f'Meeting with {name}',
            'description': f'Scheduled by Jarvis for: {dt}',
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': f"jarvis_{int(datetime.datetime.now().timestamp())}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }
        
        print("  [Calendar] Authenticating and creating event...")
        event = service.events().insert(
            calendarId='primary', 
            body=event, 
            conferenceDataVersion=1
        ).execute()
        
        meet_link = event.get('hangoutLink', 'No Meet link generated')
        
        return {
            "status": "success", 
            "message": f"Event created with {name} at {dt}. Meet link: {meet_link}",
            "name": name,
            "time": dt,
            "link": meet_link
        }
        
    except FileNotFoundError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Failed to access Google Calendar: {str(e)}"}
