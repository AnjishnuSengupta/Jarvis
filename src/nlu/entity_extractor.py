import json
import re
import datetime
import os

class EntityExtractor:
    def __init__(self, contacts_path="data/contacts.json"):
        # Load contacts gazetteer
        self.contacts = {}
        if os.path.exists(contacts_path):
            with open(contacts_path, "r") as f:
                self.contacts = json.load(f)
                
        # Mock paired devices gazetteer
        self.devices = ["headphones", "airpods", "sony wh-1000xm4", "speaker", "car audio", "keyboard", "mouse"]
        
    def extract_datetime(self, text):
        """
        Custom date parser using regex. Resolves relative dates to absolute datetimes.
        """
        text = text.lower()
        now = datetime.datetime.now().astimezone()
        
        # Match "tomorrow"
        if re.search(r'\btomorrow\b', text):
            target_date = now + datetime.timedelta(days=1)
            # Try to find a time associated with it
            time_match = re.search(r'at (\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                ampm = time_match.group(3)
                if ampm == 'pm' and hour < 12:
                    hour += 12
                elif ampm == 'am' and hour == 12:
                    hour = 0
                target_date = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return target_date.isoformat()
            
        # Match "in X hours"
        hours_match = re.search(r'in (\d+) hours?', text)
        if hours_match:
            hours = int(hours_match.group(1))
            target_date = now + datetime.timedelta(hours=hours)
            return target_date.isoformat()
            
        # Match "next <day>"
        days = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}
        next_day_match = re.search(r'next (monday|tuesday|wednesday|thursday|friday|saturday|sunday)', text)
        if next_day_match:
            target_weekday = days[next_day_match.group(1)]
            current_weekday = now.weekday()
            days_ahead = target_weekday - current_weekday
            if days_ahead <= 0:
                days_ahead += 7
            target_date = now + datetime.timedelta(days=days_ahead)
            return target_date.isoformat()
            
        # Match direct time like "4pm", "3:30 pm today"
        time_match = re.search(r'\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b', text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            ampm = time_match.group(3)
            
            if ampm == 'pm' and hour < 12:
                hour += 12
            elif ampm == 'am' and hour == 12:
                hour = 0
                
            target_date = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target_date < now:
                # If time has passed today, assume tomorrow
                target_date += datetime.timedelta(days=1)
            return target_date.isoformat()
            
        return None

    def extract_contact(self, text):
        text_lower = text.lower()
        for name in self.contacts.keys():
            if re.search(rf'\b{re.escape(name)}\b', text_lower):
                return name
        return None

    def extract_device(self, text):
        text_lower = text.lower()
        for device in self.devices:
            if re.search(rf'\b{re.escape(device)}\b', text_lower):
                return device
        return None
        
    def extract_entities(self, text, intent):
        """
        Extracts relevant slots based on the predicted intent.
        """
        slots = {}
        
        if intent == "schedule_meeting":
            contact = self.extract_contact(text)
            if contact: slots["name"] = contact
            
            dt = self.extract_datetime(text)
            if dt: slots["time"] = dt
            
        elif intent == "bluetooth_control":
            device = self.extract_device(text)
            if device: slots["device"] = device
            
        elif intent == "write_code":
            # Heuristic for project type
            match = re.search(r'(?:a|an)\s+(.*?)(?:\s+project|\s+script|\s+app|\s+website|$)', text.lower())
            if match:
                slots["project_type"] = match.group(1).strip()
                
        elif intent == "file_operation":
            action_match = re.search(r'\b(create|make|delete|remove|move|read|find|search)\b', text.lower())
            if action_match:
                action = action_match.group(1)
                if action in ["create", "make"]: slots["action"] = "create"
                elif action in ["delete", "remove"]: slots["action"] = "delete"
                elif action in ["move"]: slots["action"] = "move"
                elif action in ["read"]: slots["action"] = "read"
                elif action in ["find", "search"]: slots["action"] = "find"
                
            # Filename extraction
            match = re.search(r'(?:called|named|of)\s+([a-zA-Z0-9_\-\.]+)', text.lower())
            if match:
                slots["filename"] = match.group(1).strip()
            elif action_match:
                # Fallback: extract the next word/words after the action that isn't "to" or "a"
                after_action = text.lower().split(action_match.group(1), 1)[1].strip()
                # Remove prefixes like "a new file called" etc if they were somehow missed
                clean_name = re.sub(r'^(?:a|the|new|file)\s+', '', after_action).strip()
                name_match = re.match(r'^([a-zA-Z0-9_\-\.]+)', clean_name)
                if name_match and name_match.group(1) not in ["to", "in", "the", "a", "file"]:
                    slots["filename"] = name_match.group(1)
                    
            folder_match = re.search(r'to\s+(?:the\s+)?([a-zA-Z0-9_]+)', text.lower())
            if folder_match:
                slots["folder"] = folder_match.group(1).strip()
                
        elif intent == "system_control":
            action_match = re.search(r'\b(lock|sleep|suspend|brightness|volume|mute)\b', text.lower())
            if action_match:
                action = action_match.group(1)
                if action == "suspend": action = "sleep"
                slots["action"] = action
                
            match = re.search(r'(?:to|at)\s+([a-zA-Z0-9%]+)', text.lower())
            if match:
                slots["level"] = match.group(1).strip()
                
        elif intent == "memory_query":
            match = re.search(r'(?:about|remember|recall|name of the|for|what is)\s+(.*)', text.lower())
            if match:
                slots["topic"] = match.group(1).strip().strip('?')
                
        elif intent == "store_memory":
            match = re.search(r'(?:that|is)\s+(.*)', text.lower())
            if match:
                slots["fact"] = match.group(1).strip()
                
        elif intent == "calculate_math":
            match = re.search(r'(?:is|calculate|solve|much is|integrate|derivative of|find|evaluate)\s+([0-9a-zA-Z+\-*/.\s\(\)\^∫]+)\??$', text.lower())
            if match:
                slots["expression"] = match.group(1).strip()
            else:
                # If no keyword, assume the whole text is the expression except maybe "?"
                slots["expression"] = text.lower().replace("?", "").strip()
                
        elif intent == "get_weather":
            match = re.search(r'(?:in|for)\s+([a-zA-Z\s]+)\??$', text.lower())
            if match:
                slots["location"] = match.group(1).strip()
                
        elif intent == "web_search":
            match = re.search(r'(?:for|about|google|up)\s+(.*)', text.lower())
            if match:
                slots["query"] = match.group(1).strip()
                
        elif intent == "code_lookup":
            match = re.search(r'(?:how do i|code for|snippet|how to|find my|lookup)\s+(.*)', text.lower())
            if match:
                slots["query"] = match.group(1).strip()
            else:
                slots["query"] = text.lower().strip()
                
        elif intent == "suggest_code_changes":
            match = re.search(r'(?:changes for|improve|refactor my|refactor|changes to|optimize|suggestions for|analyze)\s+(.*)', text.lower())
            if match:
                slots["query"] = match.group(1).strip()
            else:
                slots["query"] = text.lower().strip()
                
        elif intent == "clarification_response":
            # Could be a time, a name, a device, etc.
            # Try all extractions
            contact = self.extract_contact(text)
            if contact: slots["value"] = contact
            else:
                dt = self.extract_datetime(text)
                if dt: slots["value"] = dt
                else:
                    device = self.extract_device(text)
                    if device: slots["value"] = device
                    else:
                        match = re.search(r'(?:is|meant|with)\s+(.*)', text.lower())
                        if match:
                            slots["value"] = match.group(1).strip()
                        else:
                            slots["value"] = text.strip()
                            
        return slots

if __name__ == "__main__":
    extractor = EntityExtractor()
    print(extractor.extract_entities("schedule a meeting with raj tomorrow at 4pm", "schedule_meeting"))
    print(extractor.extract_entities("turn on bluetooth and connect to my airpods", "bluetooth_control"))
    print(extractor.extract_entities("make me a React app", "write_code"))
