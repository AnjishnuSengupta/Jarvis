import speech_recognition as sr
import pyttsx3
import sys

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
                
                # Using Google's free endpoint for simplicity, fallback could be PocketSphinx for offline
                text = self.recognizer.recognize_google(audio)
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
