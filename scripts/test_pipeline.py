import os
import sys

# Ensure imports work when run from scripts directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nlu.tokenizer import Tokenizer
from src.nlu.vectorizer import TFIDFVectorizer
from src.nlu.classifier import IntentClassifier
from src.nlu.entity_extractor import EntityExtractor
from src.dialogue.manager import DialogueManager
import pickle
import numpy as np

def run_tests():
    print("=== Jarvis NLU Automated Testing Suite ===")
    
    # 1. Load Tokenizer & Vectorizer
    try:
        import json
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
        print("Error: Vectorizer models not found. Run 'python src/nlu/train.py' first.")
        return
        
    # 2. Load Classifier
    try:
        with open("models/intent_model.npz_map.json", "r") as f:
            idx_to_intent = json.load(f)
            
        num_classes = len(idx_to_intent)
        classifier = IntentClassifier(input_size=len(tokenizer.vocab), num_classes=num_classes)
        _ = classifier.load("models/intent_model.npz")
    except FileNotFoundError:
        print("Error: Intent model not found.")
        return
        
    extractor = EntityExtractor()
    dm = DialogueManager()
    
    # Define test scenarios
    scenarios = [
        {
            "name": "Scenario 1: Simple Meeting Schedule",
            "turns": [
                {"input": "schedule a meeting with Raj tomorrow at 4pm", "expected_intent": "schedule_meeting", "ready": True}
            ]
        },
        {
            "name": "Scenario 2: Multi-turn Delete File with Cancellation",
            "turns": [
                {"input": "delete notes.txt", "expected_intent": "file_operation", "ready": False, "missing_slot": "confirmed"},
                {"input": "no wait", "expected_intent": "operation_cancelled", "ready": True}
            ]
        },
        {
            "name": "Scenario 3: Multi-turn Move File with Confirmation",
            "turns": [
                {"input": "move main.py", "expected_intent": "file_operation", "ready": False, "missing_slot": "folder"},
                {"input": "to the desktop", "expected_intent": "file_operation", "ready": False, "missing_slot": "confirmed"},
                {"input": "yes", "expected_intent": "file_operation", "ready": True}
            ]
        },
        {
            "name": "Scenario 4: Windows Brightness (OS parity test)",
            "turns": [
                {"input": "set brightness to 50%", "expected_intent": "system_control", "ready": True}
            ]
        }
    ]
    
    passed_all = True
    
    for scenario in scenarios:
        print(f"\nRunning {scenario['name']}...")
        dm.reset()
        
        for turn_idx, turn in enumerate(scenario["turns"], 1):
            text = turn["input"]
            print(f"  User: '{text}'")
            
            # 1. Vectorize
            vec = vectorizer.transform([text])
            
            # 2. Predict Intent
            pred = classifier.forward(vec)
            intent_idx = np.argmax(pred, axis=1)[0]
            confidence = np.max(pred, axis=1)[0]
            predicted_intent = idx_to_intent[str(intent_idx)]
            
            if predicted_intent == "general_chat" and confidence < 0.3:
                # low confidence mapping logic would happen here, but we assume synthetic data is strong
                pass
                
            # 3. Extract entities
            slots = extractor.extract_entities(text, predicted_intent)
            
            # 4. Dialogue Manager
            final_intent, final_slots, ready, missing = dm.process_turn(predicted_intent, slots)
            
            print(f"    -> Intent: {final_intent} | Ready: {ready} | Missing: {missing}")
            
            if final_intent != turn["expected_intent"]:
                print(f"    [FAIL] Expected intent {turn['expected_intent']}, got {final_intent}")
                passed_all = False
            if ready != turn["ready"]:
                print(f"    [FAIL] Expected ready={turn['ready']}, got {ready}")
                passed_all = False
            if not ready and missing != turn.get("missing_slot"):
                print(f"    [FAIL] Expected missing slot '{turn.get('missing_slot')}', got '{missing}'")
                passed_all = False
                
    if passed_all:
        print("\n✅ All NLU and Dialogue Manager tests passed perfectly!")
    else:
        print("\n❌ Some tests failed.")

if __name__ == "__main__":
    run_tests()
