import os
import sys

# Ensure imports work when run from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.logger import get_flagged_interactions, update_interaction

def main():
    print("=== Jarvis Active Learning Review ===")
    flagged = get_flagged_interactions()
    
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
        print("1. schedule_meeting     2. write_code           3. bluetooth_control")
        print("4. system_control       5. file_operation       6. memory_query")
        print("7. general_chat         8. clarification_response")
        print("9. [Skip / Was Correct]")
        
        while True:
            try:
                choice = int(input("\nEnter correct intent number (1-9): "))
                if 1 <= choice <= 9:
                    break
                print("Invalid choice.")
            except ValueError:
                print("Please enter a number.")
                
        intents_map = {
            1: "schedule_meeting",
            2: "write_code",
            3: "bluetooth_control",
            4: "system_control",
            5: "file_operation",
            6: "memory_query",
            7: "general_chat",
            8: "clarification_response"
        }
        
        if choice == 9:
            # It was actually correct, just low confidence
            correct_intent = predicted_intent
            print("Marked as correct.")
        else:
            correct_intent = intents_map[choice]
            print(f"Corrected to: {correct_intent}")
            
        update_interaction(interaction_id, correct_intent)
        
    print("\nReview complete! You should run `python src/nlu/train.py` to retrain the model.")

if __name__ == "__main__":
    main()
