import sqlite3
import os
import json
import numpy as np

from src.nlu.tokenizer import Tokenizer
from src.nlu.vectorizer import TFIDFVectorizer
from src.data.logger import init_db

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "jarvis.db"))
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models"))

def seed_snippets_if_empty():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT count(*) FROM code_snippets')
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("[Code Retrieval] Seeding initial hand-curated snippets...")
        seed_data = [
            ("debounce a function in javascript", "function debounce(func, wait) {\n  let timeout;\n  return function executedFunction(...args) {\n    const later = () => {\n      clearTimeout(timeout);\n      func(...args);\n    };\n    clearTimeout(timeout);\n    timeout = setTimeout(later, wait);\n  };\n}", "manual_seed", "javascript"),
            ("binary search algorithm in python", "def binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1", "manual_seed", "python")
        ]
        cursor.executemany('INSERT INTO code_snippets (description, code, source_path, language) VALUES (?, ?, ?, ?)', seed_data)
        conn.commit()
    conn.close()

def execute_code_lookup(slots):
    seed_snippets_if_empty()
    query = slots.get("query", "").strip()
    
    if not query:
        return {"status": "error", "message": "What kind of code are you looking for?"}
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT description, code, source_path, language FROM code_snippets')
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {"status": "error", "message": "The code repository is completely empty."}
            
        descriptions = [row[0] for row in rows]
        
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
        
        # Vectorize query and descriptions
        query_vec = vectorizer.transform([query])[0]
        desc_vecs = vectorizer.transform(descriptions)
        
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return {"status": "success", "message": f"I couldn't find any code matching '{query}'."}
            
        best_match = None
        best_score = -1
        
        for idx, desc_vec in enumerate(desc_vecs):
            desc_norm = np.linalg.norm(desc_vec)
            if desc_norm == 0:
                continue
                
            sim = np.dot(query_vec, desc_vec) / (query_norm * desc_norm)
            if sim > best_score:
                best_score = sim
                best_match = rows[idx]
                
        # Cosine similarity threshold
        if best_score < 0.1 or not best_match:
            return {"status": "success", "message": f"I couldn't find a strong match for '{query}' in the code database. (Highest match was {(best_score*100):.1f}%)"}
            
        desc, code, src, lang = best_match
        response_msg = f"Found a match from {src} ({lang}):\n\n```{lang}\n{code}\n```"
        
        return {"status": "success", "message": response_msg, "code": code, "language": lang, "source": src}
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to retrieve code: {str(e)}"}
