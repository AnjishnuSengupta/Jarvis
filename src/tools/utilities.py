import datetime
import webbrowser
import psutil
import urllib.parse
import urllib.request
import json

def execute_time_date(slots):
    """Returns the current system time and date."""
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%A, %B %d, %Y")
    return {"status": "success", "message": f"It is currently {current_time} on {current_date}."}

def execute_weather(slots):
    """Fetches real weather data from wttr.in."""
    location = slots.get("location", "")
    if not location:
        return {"status": "error", "message": "I need a location to check the weather."}
        
    encoded_location = urllib.parse.quote(location)
    url = f"https://wttr.in/{encoded_location}?format=3"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            weather_data = response.read().decode('utf-8').strip()
            if weather_data:
                return {"status": "success", "message": f"The weather in {weather_data}."}
            else:
                return {"status": "error", "message": "Could not retrieve weather data."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch weather: {e}"}

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
    """Fetches a real random joke from the Official Joke API."""
    url = "https://official-joke-api.appspot.com/random_joke"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            setup = data.get("setup", "")
            punchline = data.get("punchline", "")
            return {"status": "success", "message": f"{setup} ... {punchline}"}
    except Exception as e:
        return {"status": "error", "message": "I couldn't think of a joke right now."}

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
