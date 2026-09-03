import json
import random
import os
import re
from pathlib import Path

random.seed(42)

def introduce_noise(text):
    """Introduces realistic typos and punctuation dropping."""
    if random.random() < 0.2:
        # drop punctuation
        text = text.replace('?', '').replace('.', '').replace(',', '')
    if random.random() < 0.1:
        # simulate typo
        typos = {
            "schedule": "schdule",
            "bluetooth": "blutooth",
            "turn": "trun",
            "meeting": "meting",
            "tomorrow": "tomorow"
        }
        for word, typo in typos.items():
            if word in text.lower():
                text = re.sub(rf'\b{word}\b', typo, text, flags=re.IGNORECASE)
                break
    return text

INTENTS = {
    "schedule_meeting": {
        "templates": [
            "schedule a meeting with {name} {time}",
            "book some time with {name} {time}",
            "set up a call with {name} for {time}",
            "can you schedule a meeting {time} with {name}",
            "create an event with {name} {time}",
            "meeting with {name} {time}",
            "schedule a meeting with {name} {time} and turn on bluetooth"
        ],
        "slots": {
            "name": ["Raj", "Alice", "Bob", "Charlie", "Dave", "Eve", "my manager", "the team", "John", "Sarah"],
            "time": ["tomorrow at 4pm", "next monday", "in 2 hours", "at 3:30 pm today", "on friday morning", "tomorrow morning", "at 10am"]
        }
    },
    "write_code": {
        "templates": [
            "make me a {project_type}",
            "scaffold a {project_type}",
            "write code for a {project_type}",
            "create a {project_type} project",
            "I need a {project_type}",
            "build a {project_type}"
        ],
        "slots": {
            "project_type": ["landing page with a contact form", "React app", "Vite project", "simple python script", "node express server", "basic portfolio website", "todo app"]
        }
    },
    "bluetooth_control": {
        "templates": [
            "turn on Bluetooth",
            "turn off Bluetooth",
            "connect to my {device}",
            "disconnect from {device}",
            "pair with {device}",
            "is bluetooth on?"
        ],
        "slots": {
            "device": ["headphones", "AirPods", "Sony WH-1000XM4", "speaker", "car audio", "keyboard", "mouse"]
        }
    },
    "system_control": {
        "templates": [
            "lock the screen",
            "mute the volume",
            "turn the volume up",
            "set brightness to {level}",
            "put the computer to sleep",
            "check battery level",
            "suspend the system",
            "make the screen brighter",
            "lower the volume to {level}",
            "lock my pc"
        ],
        "slots": {
            "level": ["maximum", "50%", "low", "high", "100 percent", "75%"]
        }
    },
    "file_operation": {
        "templates": [
            "create a new file called {filename}",
            "delete {filename}",
            "move {filename} to {folder}",
            "read the contents of {filename}",
            "find the file named {filename}",
            "make a file named {filename}",
            "remove {filename}",
            "where is {filename} located?",
            "what is inside {filename}?"
        ],
        "slots": {
            "filename": ["notes.txt", "report.pdf", "main.py", "index.html", "the document", "my resume", "test.py"],
            "folder": ["desktop", "documents", "downloads", "the archive", "home folder"]
        }
    },
    "memory_query": {
        "templates": [
            "what did I say about {topic}?",
            "do you remember {topic}?",
            "recall {topic}",
            "what was the name of the {topic}?",
            "search your memory for {topic}"
        ],
        "slots": {
            "topic": ["the new project", "Raj's email", "that book recommendation", "my wifi password", "the meeting last week"]
        }
    },
    "store_memory": {
        "templates": [
            "remember that {fact}",
            "store this in your memory: {fact}",
            "keep in mind that {fact}",
            "my {fact} is {value}",
            "note that {fact}"
        ],
        "slots": {
            "fact": ["wifi password is 123", "favorite color is blue", "manager's name is Dave", "flight leaves at 4pm"],
            "value": ["blue", "123", "Dave"]
        }
    },
    "general_chat": {
        "templates": [
            "hello",
            "hi there",
            "how are you?",
            "good morning",
            "what's up?",
            "who are you?",
            "thanks",
            "thank you"
        ],
        "slots": {}
    },
    "calculate_math": {
        "templates": [
            "what is {expression}?",
            "calculate {expression}",
            "{expression}",
            "how much is {expression}?",
            "can you calculate {expression}",
            "tell me what is {expression}",
            "integrate {expression} dx",
            "find ∫ {expression} dx",
            "derivative of {expression} with respect to x",
            "solve {expression}",
            "evaluate {expression}"
        ],
        "slots": {
            "expression": ["2+2", "5 * 10", "100 / 4", "3 + 7", "10-2", "8 times 8", "12 divided by 3", "20 + 30 - 5", "x^3 - 4*x", "x^2 + 2*x + 1", "sin(x)", "cos(x)"]
        }
    },
    "get_time_date": {
        "templates": [
            "what time is it?",
            "what is the time?",
            "tell me the time",
            "what is today's date?",
            "what is the date today?",
            "what day is it?"
        ],
        "slots": {}
    },
    "get_weather": {
        "templates": [
            "what is the weather like in {location}?",
            "tell me the weather for {location}",
            "is it going to rain in {location}?",
            "weather in {location}",
            "what's the temperature in {location}?",
            "what is the weather in {location}?",
            "is it raining in {location}?"
        ],
        "slots": {
            "location": ["London", "New York", "Tokyo", "Paris", "my city", "San Francisco"]
        }
    },
    "web_search": {
        "templates": [
            "search the web for {query}",
            "google {query}",
            "look up {query}",
            "find information about {query}",
            "can you search for {query}?",
            "search for {query}"
        ],
        "slots": {
            "query": ["python tutorials", "how to tie a tie", "latest news", "best restaurants nearby", "cute cat videos"]
        }
    },
    "tell_joke": {
        "templates": [
            "tell me a joke",
            "say something funny",
            "make me laugh",
            "do you know any jokes?",
            "tell a joke"
        ],
        "slots": {}
    },
    "system_status": {
        "templates": [
            "how is your cpu usage?",
            "what is my battery level?",
            "how much memory is being used?",
            "check system status",
            "are we running hot?"
        ],
        "slots": {}
    },
    "clarification_response": {
        "templates": [
            "it is {value}",
            "the value is {value}",
            "I meant {value}",
            "{value}",
            "let's go with {value}",
            "yes",
            "y",
            "sure",
            "ok",
            "do it"
        ],
        "slots": {
            "value": ["tomorrow", "Raj", "4pm", "a React app", "my AirPods", "notes.txt", "yes", "no"]
        }
    },
    "operation_cancelled": {
        "templates": [
            "cancel that",
            "stop",
            "abort",
            "nevermind",
            "no",
            "don't do it",
            "cancel",
            "quit",
            "exit",
            "no thanks",
            "forget it",
            "no wait",
            "actually don't",
            "never mind",
            "no cancel that",
            "wait stop"
        ],
        "slots": {}
    }
}

def generate_examples(intent_name, intent_data, num_examples=200):
    templates = intent_data["templates"]
    slots = intent_data["slots"]
    examples = []
    
    for _ in range(num_examples):
        template = random.choice(templates)
        example_str = template
        
        # Determine which slots are needed for this template
        # Very simple replacement loop
        for slot_name, slot_values in slots.items():
            slot_token = f"{{{slot_name}}}"
            if slot_token in example_str:
                chosen_value = random.choice(slot_values)
                example_str = example_str.replace(slot_token, chosen_value)
                
        # Optional: sometimes add random noise like punctuation or typos? Keep it clean for now.
        example_str = introduce_noise(example_str)
        
        examples.append({
            "text": example_str,
            "intent": intent_name
        })
        
    return examples

def main():
    print("Generating synthetic dataset...")
    all_examples = []
    
    for intent_name, intent_data in INTENTS.items():
        # Generate examples
        examples = generate_examples(intent_name, intent_data, num_examples=500)
        # Deduplicate to some extent
        unique_texts = set()
        deduped = []
        for ex in examples:
            if ex["text"] not in unique_texts:
                unique_texts.add(ex["text"])
                deduped.append(ex)
        
        # If we have less than 150 examples, pad by repeating
        target_size = 150
        if len(deduped) < target_size:
            padded = deduped.copy()
            while len(padded) < target_size:
                padded.append(random.choice(deduped))
            deduped = padded
        
        print(f"Generated {len(deduped)} examples for intent: {intent_name}")
        all_examples.extend(deduped)
        
    # Shuffle dataset
    random.shuffle(all_examples)
    
    # Save to JSON
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "synthetic_dataset.json"
    
    with open(output_file, "w") as f:
        json.dump(all_examples, f, indent=2)
        
    print(f"Total examples generated: {len(all_examples)}")
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    main()
