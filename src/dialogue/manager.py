class DialogueManager:
    def __init__(self):
        self.pending_intent = None
        self.filled_slots = {}
        
        # Define required slots for each intent
        self.intent_schema = {
            "schedule_meeting": ["name", "time"],
            "write_code": ["project_type"],
            "bluetooth_control": ["device"],
            "system_control": ["action"],
            "file_operation": ["action", "filename"],
            "memory_query": ["topic"],
            "store_memory": ["fact"],
            "general_chat": [],
            "calculate_math": ["expression"],
            "get_time_date": [],
            "get_weather": ["location"],
            "web_search": ["query"],
            "tell_joke": [],
            "system_status": [],
            "code_lookup": ["query"],
            "clarification_response": [],
            "operation_cancelled": []
        }
        
    def get_missing_slots(self, intent, filled_slots):
        if intent not in self.intent_schema:
            return []
            
        required = self.intent_schema[intent].copy()
        
        # Dynamic requirement: if system_control is volume/brightness, we also need level
        if intent == "system_control" and filled_slots.get("action") in ["volume", "brightness"]:
            required.append("level")
            
        # Dynamic requirement: if file_operation is move, we also need folder
        if intent == "file_operation" and filled_slots.get("action") == "move":
            required.append("folder")
            
        # Confirmation logic for destructive actions
        if intent == "file_operation" and filled_slots.get("action") in ["delete", "move"]:
            required.append("confirmed")
            
        return [slot for slot in required if slot not in filled_slots]
        
    def process_turn(self, predicted_intent, extracted_slots):
        # If we have a pending intent, and we receive a clarification response,
        # or if the user just repeats the same intent with new slots, we merge them.
        if self.pending_intent and (predicted_intent == "clarification_response" or predicted_intent == self.pending_intent):
            intent = self.pending_intent
            
            # Merge extracted slots into filled_slots
            for k, v in extracted_slots.items():
                if k == "value":
                    # Find the first missing slot and assign this generic value
                    missing_slots = self.get_missing_slots(intent, self.filled_slots)
                    if missing_slots:
                        self.filled_slots[missing_slots[0]] = v
                else:
                    self.filled_slots[k] = v
        else:
            # New turn
            self.pending_intent = predicted_intent
            self.filled_slots = extracted_slots
            intent = predicted_intent
            
        if intent not in self.intent_schema:
            return intent, self.filled_slots, True, "Unknown intent schema."
            
        missing_slots = self.get_missing_slots(intent, self.filled_slots)
            
        if missing_slots:
            # Special check for confirmation
            if missing_slots[0] == "confirmed":
                self.pending_intent = intent
                return intent, self.filled_slots, False, "confirmed"
                
            return intent, self.filled_slots, False, missing_slots[0]
            
        # If confirmed slot is present but not positive
        if intent == "file_operation" and self.filled_slots.get("action") in ["delete", "move"]:
            if self.filled_slots.get("confirmed", "").lower() not in ["yes", "y", "sure", "ok", "do it"]:
                self.reset()
                return "operation_cancelled", {}, True, "Operation cancelled."
            
        # All required slots filled
        final_intent = self.pending_intent
        final_slots = self.filled_slots.copy()
        
        # Reset state
        self.pending_intent = None
        self.filled_slots = {}
        
        return final_intent, final_slots, True, None

    def reset(self):
        self.pending_intent = None
        self.filled_slots = {}
