import json
import numpy as np
import os
import random
from tokenizer import Tokenizer
from vectorizer import TFIDFVectorizer
from classifier import IntentClassifier

def load_data(path="data/synthetic_dataset.json"):
    with open(path, "r") as f:
        data = json.load(f)
    texts = [item["text"] for item in data]
    labels = [item["intent"] for item in data]
    return texts, labels

def train():
    texts, labels = load_data()
    
    # Shuffle together
    combined = list(zip(texts, labels))
    random.shuffle(combined)
    texts, labels = zip(*combined)
    texts = list(texts)
    labels = list(labels)
    
    # Intent mapping
    unique_intents = list(set(labels))
    intent_to_idx = {intent: idx for idx, intent in enumerate(unique_intents)}
    idx_to_intent = {idx: intent for intent, idx in intent_to_idx.items()}
    
    # Tokenizer & Vectorizer
    tokenizer = Tokenizer(max_vocab_size=3000)
    vectorizer = TFIDFVectorizer(tokenizer)
    
    print("Fitting Vectorizer...")
    vectorizer.fit(texts)
    X = vectorizer.transform(texts)
    
    # Labels to one-hot
    num_classes = len(unique_intents)
    y = np.zeros((len(labels), num_classes))
    for i, label in enumerate(labels):
        y[i, intent_to_idx[label]] = 1.0
        
    # Split train/test (80/20)
    split_idx = int(0.8 * len(X))
    X_train, y_train = X[:split_idx], y[:split_idx]
    X_test, y_test = X[split_idx:], y[split_idx:]
    
    print(f"Training data shape: {X_train.shape}")
    print(f"Testing data shape: {X_test.shape}")
    
    # Initialize Classifier
    classifier = IntentClassifier(input_size=X_train.shape[1], num_classes=num_classes)
    
    # Training Loop
    epochs = 150
    batch_size = 32
    learning_rate = 0.05
    
    print("Starting training...")
    for epoch in range(epochs):
        # Shuffle batches
        indices = np.arange(X_train.shape[0])
        np.random.shuffle(indices)
        X_train_shuffled = X_train[indices]
        y_train_shuffled = y_train[indices]
        
        epoch_loss = 0
        num_batches = 0
        for i in range(0, X_train.shape[0], batch_size):
            X_batch = X_train_shuffled[i:i+batch_size]
            y_batch = y_train_shuffled[i:i+batch_size]
            
            probs = classifier.forward(X_batch)
            loss = classifier.compute_loss(probs, y_batch)
            classifier.backward(y_batch)
            classifier.step(learning_rate)
            
            epoch_loss += loss
            num_batches += 1
            
        if (epoch + 1) % 10 == 0:
            # Eval on test set
            test_probs = classifier.forward(X_test)
            preds = np.argmax(test_probs, axis=1)
            truths = np.argmax(y_test, axis=1)
            acc = np.mean(preds == truths)
            print(f"Epoch {epoch+1}/{epochs} - Loss: {epoch_loss/num_batches:.4f} - Test Acc: {acc:.4f}")
            
    # Final eval
    test_probs = classifier.forward(X_test)
    preds = np.argmax(test_probs, axis=1)
    truths = np.argmax(y_test, axis=1)
    final_acc = np.mean(preds == truths)
    print(f"Final Test Accuracy: {final_acc:.4f}")
    
    # Save artifacts
    os.makedirs("models", exist_ok=True)
    
    # Save Vectorizer (vocab and idf)
    vocab_data = {
        "vocab": tokenizer.vocab,
        "max_vocab_size": tokenizer.max_vocab_size
    }
    with open("models/vocab.json", "w") as f:
        json.dump(vocab_data, f)
        
    np.save("models/idf.npy", vectorizer.idf)
    
    # Save Classifier
    classifier.save("models/intent_model.npz", idx_to_intent)
    print("Model and vectorizer saved to models/")

if __name__ == "__main__":
    train()
