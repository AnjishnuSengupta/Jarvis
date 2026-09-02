import sys
import json
import numpy as np

from src.nlu.tokenizer import Tokenizer
from src.nlu.vectorizer import TFIDFVectorizer
from src.nlu.classifier import IntentClassifier
from src.nlu.entity_extractor import EntityExtractor
from src.dialogue.manager import DialogueManager
from src.core.dispatcher import ToolDispatcher
from src.core.templater import ResponseTemplater
from src.core.voice import VoiceEngine

def main():
    use_voice = "--voice" in sys.argv
    print(r"""
      _   _    ___  __   __ ___  ___ 
     | | / \  | _ \ \ \ / /|_ _|/ __|
   _ | |/ _ \ |   /  \ V /  | | \__ \
  | || / ___ \|_|_\   \_/  |___||___/
   \__/
    """)
    print("Initializing Jarvis...")
    
    if use_voice:
        print("Initializing Voice Engine...")
        voice_engine = VoiceEngine()
    else:
        voice_engine = None
    
    # 1. Load Tokenizer & Vectorizer
    try:
        with open("models/vocab.json", "r") as f:
            vocab_data = json.load(f)
            
        tokenizer = Tokenizer(max_vocab_size=vocab_data["max_vocab_size"])
        tokenizer.vocab = vocab_data["vocab"]
        tokenizer.inv_vocab = {v: k for k, v in tokenizer.vocab.items()}
        tokenizer.is_fit = True
        
        vectorizer = TFIDFVectorizer(tokenizer)
        vectorizer.idf = np.load("models/idf.npy")
        vectorizer.is_fit = True
        
    except FileNotFoundError:
        print("Error: Models not found. Please run 'python src/nlu/train.py' first.")
        sys.exit(1)
        
    # 2. Load Classifier
    try:
        with open("models/intent_model.npz_map.json", "r") as f:
            idx_to_intent = json.load(f)
            
        num_classes = len(idx_to_intent)
        classifier = IntentClassifier(input_size=len(tokenizer.vocab), num_classes=num_classes)
        _ = classifier.load("models/intent_model.npz")
    except FileNotFoundError:
        print("Error: Intent model not found.")
        sys.exit(1)
        
    # 3. Initialize middle-tier components
    extractor = EntityExtractor()
    dialogue_manager = DialogueManager()
    dispatcher = ToolDispatcher()
    templater = ResponseTemplater()
    
    print("Jarvis is online. Type 'exit' or 'quit' to stop.")
    print("-" * 50)
    
    while True:
        try:
            if use_voice:
                user_input = voice_engine.listen()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit", "goodbye"]:
                    break
            else:
                user_input = input("You: ")
                if user_input.lower() in ["exit", "quit"]:
                    break
                    
            if not user_input.strip():
                continue
                
            # Vectorize
            X = vectorizer.transform([user_input])
            
            # Predict Intent
            probs = classifier.forward(X)[0]
            pred_idx = np.argmax(probs)
            confidence = probs[pred_idx]
            predicted_intent = idx_to_intent[str(pred_idx)]
            
            # Extract Entities
            extracted_slots = extractor.extract_entities(user_input, predicted_intent)
            
            # Log Interaction
            from src.data.logger import log_interaction
            needs_review = log_interaction(user_input, predicted_intent, float(confidence), extracted_slots)
            
            if confidence < 0.35:
                msg_text = "I'm sorry, I don't understand that command."
                if use_voice:
                    voice_engine.speak(msg_text)
                else:
                    print(f"Jarvis: {msg_text}")
                continue

            if needs_review:
                msg_text = f"I'm not entirely sure, but I'll assume you meant '{predicted_intent}'."
                if use_voice:
                    voice_engine.speak(msg_text)
                else:
                    print(f"Jarvis [Low Confidence: {confidence:.2f}]: {msg_text}")
                
            # Dialogue Manager Processing
            final_intent, final_slots, ready_to_dispatch, msg = dialogue_manager.process_turn(predicted_intent, extracted_slots)
            
            if not ready_to_dispatch:
                # Ask clarification question
                clarification = templater.generate_clarification(msg)
                if use_voice:
                    voice_engine.speak(clarification)
                else:
                    print(f"Jarvis: {clarification}")
            else:
                # Dispatch Tool
                tool_result = dispatcher.dispatch(final_intent, final_slots)
                
                # Generate Response
                response = templater.generate_response(final_intent, final_slots, tool_result)
                if use_voice:
                    voice_engine.speak(response)
                else:
                    print(f"Jarvis: {response}")
                
        except (KeyboardInterrupt, EOFError):
            break
            
    print("\nGoodbye!")

if __name__ == "__main__":
    main()
