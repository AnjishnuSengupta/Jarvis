class DialogueManager:
    def __init__(self):
        self.pending_intent = None
        self.filled_slots = {}
        
        # Define required slots for each intent
        self.intent_schema = {
            "schedule_meeting": ["name", "time"],
            "write_code": ["project_type"],
            "bluetooth_control": ["device"],
            "system_control": ["level"],
            "file_operation": ["filename"],
            "memory_query": ["topic"],
            "store_memory": ["fact"],
            "general_chat": [],
            "clarification_response": []
        }
        
    def process_turn(self, predicted_intent, extracted_slots):
        # If we have a pending intent, and we receive a clarification response,
        # or if the user just repeats the same intent with new slots, we merge them.
        if self.pending_intent and (predicted_intent == "clarification_response" or predicted_intent == self.pending_intent):
            intent = self.pending_intent
            
            # Merge extracted slots into filled_slots
            for k, v in extracted_slots.items():
                if k == "value":
                    # Find the first missing slot and assign this generic value
                    missing_slots = [slot for slot in self.intent_schema[intent] if slot not in self.filled_slots]
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
            
        missing_slots = [slot for slot in self.intent_schema[intent] if slot not in self.filled_slots]
        
        if missing_slots:
            return intent, self.filled_slots, False, missing_slots[0]
            
        # All required slots filled
        final_intent = self.pending_intent
        final_slots = self.filled_slots.copy()
        
        # Reset state
        self.pending_intent = None
        self.filled_slots = {}
        
        return final_intent, final_slots, True, None
