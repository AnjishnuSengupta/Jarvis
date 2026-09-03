import speech_recognition as sr
import pyttsx3
import sys
import os
import json
try:
    from vosk import Model, KaldiRecognizer
except ImportError:
    pass

class VoiceEngine:
    def __init__(self):
        # Initialize Text-to-Speech
        try:
            self.tts_engine = pyttsx3.init()
            # Try to select a good voice (optional)
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"Warning: TTS initialization failed: {e}")
            self.tts_engine = None

        # Initialize Speech-to-Text
        self.recognizer = sr.Recognizer()
        
        # Initialize Vosk Model
        self.vosk_model = None
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models", "vosk-model-small-en-us-0.15"))
        if os.path.exists(model_path):
            try:
                self.vosk_model = Model(model_path)
                print("Vosk STT Model loaded successfully.")
            except Exception as e:
                print(f"Warning: Failed to load Vosk model: {e}")
        else:
            print(f"Warning: Vosk model not found at {model_path}. Please run scripts/download_vosk_model.py")
        
    def speak(self, text):
        if not text:
            return
            
        print(f"Jarvis: {text}")
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"[TTS Error]: {e}")

    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("Processing...")
                
                if not self.vosk_model:
                    print("[STT Error]: Vosk model is not loaded. Cannot transcribe offline.")
                    return ""
                    
                # Use Vosk offline model
                rec = KaldiRecognizer(self.vosk_model, 16000)
                rec.AcceptWaveform(audio.get_raw_data(convert_rate=16000, convert_width=2))
                result = json.loads(rec.FinalResult())
                text = result.get("text", "")
                
                print(f"You said: {text}")
                return text
                
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                print("[STT Error]: Could not understand audio.")
                return ""
            except sr.RequestError as e:
                print(f"[STT Error]: Could not request results; {e}")
                return ""
            except Exception as e:
                print(f"[STT Error]: {e}")
                return ""
