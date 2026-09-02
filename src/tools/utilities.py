import datetime
import webbrowser
import psutil
import random
import urllib.parse

def execute_time_date(slots):
    """Returns the current system time and date."""
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%A, %B %d, %Y")
    return {"status": "success", "message": f"It is currently {current_time} on {current_date}."}

def execute_weather(slots):
    """Mocks weather functionality (could be expanded to a real API)."""
    location = slots.get("location", "your area")
    # Mocked weather conditions
    conditions = ["sunny", "cloudy", "raining", "snowing", "clear"]
    temp = random.randint(40, 90)
    cond = random.choice(conditions)
    return {"status": "success", "message": f"The weather in {location} is {temp} degrees and {cond}."}

def execute_web_search(slots):
    """Opens a web browser to search for a query."""
    query = slots.get("query", "")
    if not query:
        return {"status": "error", "message": "I didn't catch what you wanted to search for."}
    
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded_query}"
    
    try:
        webbrowser.open(url)
        return {"status": "success", "message": f"I have opened a search for {query} in your browser."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to open browser: {e}"}

def execute_joke(slots):
    """Returns a random joke."""
    jokes = [
        "Why do programmers prefer dark mode? Because light attracts bugs.",
        "There are 10 types of people in the world: those who understand binary, and those who don't.",
        "Why did the developer go broke? Because he used up all his cache.",
        "I would tell you a UDP joke, but you might not get it."
    ]
    return {"status": "success", "message": random.choice(jokes)}

def execute_system_status(slots):
    """Returns real system status using psutil."""
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        
        status_msg = f"CPU is at {cpu}%. Memory usage is at {mem}%."
        if battery:
            status_msg += f" Battery is at {battery.percent}%."
            
        return {"status": "success", "message": status_msg}
    except Exception as e:
        return {"status": "error", "message": f"Could not retrieve system status: {e}"}
