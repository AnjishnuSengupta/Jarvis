import sqlite3
import os
import json
import numpy as np
import datetime

from src.nlu.tokenizer import Tokenizer
from src.nlu.vectorizer import TFIDFVectorizer

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "jarvis.db"))
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models"))

def execute_memory_store(slots):
    fact = slots.get("fact", "").strip()
    if not fact:
        return {"status": "error", "message": "No fact provided to store."}
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        timestamp = datetime.datetime.now().isoformat()
        cursor.execute('INSERT INTO memories (timestamp, fact) VALUES (?, ?)', (timestamp, fact))
        
        conn.commit()
        conn.close()
        
        return {"status": "success", "message": f"Successfully stored memory: '{fact}'."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to store memory: {str(e)}"}

def execute_memory_query(slots):
    topic = slots.get("topic", "").strip()
    if not topic:
        return {"status": "error", "message": "No topic provided to query."}
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT fact FROM memories')
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {"status": "success", "message": "I don't have any memories stored yet."}
            
        facts = [row[0] for row in rows]
        
        # Load Vectorizer
        with open(os.path.join(MODELS_DIR, "vocab.json"), "r") as f:
            vocab_data = json.load(f)
            
        tokenizer = Tokenizer(max_vocab_size=vocab_data["max_vocab_size"])
        tokenizer.vocab = vocab_data["vocab"]
        tokenizer.inv_vocab = {v: k for k, v in tokenizer.vocab.items()}
        tokenizer.is_fit = True
        
        vectorizer = TFIDFVectorizer(tokenizer)
        vectorizer.idf = np.load(os.path.join(MODELS_DIR, "idf.npy"))
        vectorizer.is_fit = True
        
        # Vectorize query and all facts
        query_vec = vectorizer.transform([topic])[0]
        fact_vecs = vectorizer.transform(facts)
        
        # Compute Cosine Similarity
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return {"status": "success", "message": "I couldn't find anything matching that exactly."}
            
        best_match = None
        best_score = -1
        
        for idx, fact_vec in enumerate(fact_vecs):
            fact_norm = np.linalg.norm(fact_vec)
            if fact_norm == 0:
                continue
                
            sim = np.dot(query_vec, fact_vec) / (query_norm * fact_norm)
            if sim > best_score:
                best_score = sim
                best_match = facts[idx]
                
        # If score is very low, say we didn't find a good match
        if best_score < 0.1 or not best_match:
            return {"status": "success", "message": f"I couldn't find a strong memory related to '{topic}'."}
            
        return {"status": "success", "message": f"I recall this: {best_match}"}
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to query memory: {str(e)}"}
