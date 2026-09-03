import os
import sys

# Ensure imports work when run from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.logger import get_flagged_interactions, update_interaction
from src.dialogue.manager import DialogueManager

def main():
    print("=== Jarvis Active Learning Review ===")
    flagged = get_flagged_interactions()
    
    dm = DialogueManager()
    trained_intents = list(dm.intent_schema.keys())
    
    if not flagged:
        print("No flagged interactions require review. Jarvis is confident!")
        return
        
    print(f"Found {len(flagged)} interaction(s) to review.\n")
    
    for row in flagged:
        interaction_id, raw_text, predicted_intent, confidence = row
        print("-" * 50)
        print(f"Text: '{raw_text}'")
        print(f"Predicted Intent: {predicted_intent} (Confidence: {confidence:.2f})")
        print("\nAvailable Intents:")
        for i, intent in enumerate(trained_intents, 1):
            print(f"{i}. {intent}")
            
        skip_idx = len(trained_intents) + 1
        print(f"{skip_idx}. [Skip / Was Correct]")
        
        while True:
            try:
                choice = int(input(f"\nEnter correct intent number (1-{skip_idx}): "))
                if 1 <= choice <= skip_idx:
                    break
                print("Invalid choice.")
            except ValueError:
                print("Please enter a number.")
                
        if choice == skip_idx:
            # It was actually correct, just low confidence
            correct_intent = predicted_intent
            print("Marked as correct.")
        else:
            correct_intent = trained_intents[choice - 1]
            print(f"Corrected to: {correct_intent}")
            
        update_interaction(interaction_id, correct_intent)
        
    print("\nReview complete! You should run `python src/nlu/train.py` to retrain the model.")

if __name__ == "__main__":
    main()
