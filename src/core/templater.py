import random

class ResponseTemplater:
    def __init__(self):
        self.templates = {
            "schedule_meeting": [
                "I have scheduled a meeting with {name} at {time}.",
                "Meeting with {name} is booked for {time}.",
                "Done! Your calendar now has an event with {name} for {time}."
            ],
            "write_code": [
                "I've scaffolded a new {project_type} project for you.",
                "Your {project_type} is ready.",
                "Done scaffolding the {project_type}."
            ],
            "bluetooth_control": [
                "Bluetooth is now connected to {device}.",
                "Successfully paired with {device}.",
                "Your {device} is now connected."
            ],
            "system_control": [
                "System level set to {level}.",
                "Adjusted system settings to {level}."
            ],
            "file_operation": [
                "File operation successful on {filename}.",
                "Done working with {filename}."
            ],
            "memory_query": [
                "Regarding {topic}: {message}",
                "{message}"
            ],
            "store_memory": [
                "I've remembered that for you.",
                "Got it. I'll keep that in mind.",
                "Stored in memory."
            ],
            "general_chat": [
                "{message}",
                "I am Jarvis. {message}"
            ],
            "calculate_math": [
                "The answer is {result}.",
                "{result}",
                "That would be {result}."
            ],
            "get_time_date": [
                "{message}"
            ],
            "get_weather": [
                "{message}"
            ],
            "web_search": [
                "{message}"
            ],
            "tell_joke": [
                "{message}"
            ],
            "system_status": [
                "{message}"
            ]
        }
        
        self.clarification_templates = {
            "name": [
                "Who would you like to schedule this with?",
                "What is the name of the person?"
            ],
            "time": [
                "At what time should I schedule this?",
                "When would you like the meeting to be?"
            ],
            "project_type": [
                "What kind of project should I scaffold?",
                "Are we building a React app, a Python script, or something else?"
            ],
            "device": [
                "Which device should I connect to?",
                "What is the name of the Bluetooth device?"
            ],
            "filename": [
                "What is the name of the file?",
                "Which file?"
            ],
            "level": [
                "What level should I set it to?"
            ],
            "topic": [
                "What topic are you looking for?"
            ],
            "fact": [
                "What should I remember?"
            ],
            "expression": [
                "What would you like me to calculate?",
                "What is the mathematical expression?"
            ],
            "location": [
                "Which location should I check the weather for?"
            ],
            "query": [
                "What would you like me to search for?"
            ]
        }

    def generate_response(self, intent, slots, tool_result):
        if intent not in self.templates:
            return tool_result.get("message", "Done.")
            
        template = random.choice(self.templates[intent])
        
        # Combine slots and tool_result for string formatting
        format_args = slots.copy()
        format_args.update(tool_result)
        
        # Safe format
        try:
            return template.format(**format_args)
        except KeyError:
            return tool_result.get("message", "Done.")

    def generate_clarification(self, missing_slot):
        if missing_slot in self.clarification_templates:
            return random.choice(self.clarification_templates[missing_slot])
        return f"Could you please specify the {missing_slot}?"
