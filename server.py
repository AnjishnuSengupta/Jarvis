import json
import numpy as np
import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from src.nlu.tokenizer import Tokenizer
from src.nlu.vectorizer import TFIDFVectorizer
from src.nlu.classifier import IntentClassifier
from src.nlu.entity_extractor import EntityExtractor
from src.dialogue.manager import DialogueManager
from src.core.dispatcher import ToolDispatcher
from src.core.templater import ResponseTemplater
from src.data.logger import log_interaction
from src.core.scheduler import start_background_scheduler

app = Flask(__name__)
CORS(app)  # Allow Tauri frontend to communicate with Flask

# Global state for Jarvis core components
tokenizer = None
vectorizer = None
classifier = None
idx_to_intent = None
extractor = EntityExtractor()
dialogue_manager = DialogueManager()
dispatcher = ToolDispatcher()
templater = ResponseTemplater()

def init_jarvis():
    global tokenizer, vectorizer, classifier, idx_to_intent
    print(r"""
      _   _    ___  __   __ ___  ___ 
     | | / \  | _ \ \ \ / /|_ _|/ __|
   _ | |/ _ \ |   /  \ V /  | | \__ \
  | || / ___ \|_|_\   \_/  |___||___/
   \__/
    """)
    print("Initializing Jarvis Server Backend...")
    
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
        
    # Start Proactive Scheduler
    start_background_scheduler()
    print("Jarvis Backend is ready on port 5000!")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")
    
    if not user_input.strip():
        return jsonify({"response": "Please say something."})
        
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
    needs_review = log_interaction(user_input, predicted_intent, float(confidence), extracted_slots)
    
    response_prefix = ""
    if needs_review:
        response_prefix = f"[Low Confidence: {confidence:.2f}]: I'm not entirely sure, but I'll assume you meant '{predicted_intent}'. "
        
    # Dialogue Manager Processing
    final_intent, final_slots, ready_to_dispatch, msg = dialogue_manager.process_turn(predicted_intent, extracted_slots)
    
    if not ready_to_dispatch:
        # Ask clarification question
        clarification = templater.generate_clarification(msg)
        return jsonify({"response": response_prefix + clarification})
    else:
        # Dispatch Tool
        tool_result = dispatcher.dispatch(final_intent, final_slots)
        
        # Generate Response
        response = templater.generate_response(final_intent, final_slots, tool_result)
        return jsonify({"response": response_prefix + response, "tool_data": tool_result})

if __name__ == "__main__":
    init_jarvis()
    app.run(host="127.0.0.1", port=5000, debug=False)
