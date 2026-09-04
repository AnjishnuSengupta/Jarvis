import sqlite3
import os
import json
import numpy as np
import re

from src.nlu.tokenizer import Tokenizer
from src.nlu.vectorizer import TFIDFVectorizer

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "jarvis.db"))
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models"))

def analyze_js_ts(code):
    suggestions = []
    if re.search(r'\bvar\b', code):
        suggestions.append("- Replace `var` with `let` or `const` to prevent scope hoisting bugs.")
    if re.search(r'\.then\(', code):
        suggestions.append("- Consider refactoring Promise `.then()` chains to `async/await` for better readability.")
    if re.search(r'console\.log\(', code):
        suggestions.append("- Remove `console.log` statements in production code or replace with a robust logger.")
    if re.search(r'==[^=]', code):
        suggestions.append("- Use strict equality `===` instead of loose equality `==` to prevent unintended type coercion.")
    return suggestions

def analyze_python(code):
    suggestions = []
    if re.search(r'except\s*:', code):
        suggestions.append("- Avoid bare `except:` clauses. Catch specific exceptions to prevent swallowing system exits.")
    if re.search(r'print\(', code):
        suggestions.append("- Replace `print()` statements with standard `logging` module calls for production-grade telemetry.")
    if not re.search(r'->\s*[a-zA-Z]', code) and re.search(r'def\s+\w+\(', code):
        suggestions.append("- Add PEP 484 type hints (e.g. `def my_func() -> None:`) to function signatures for better static analysis.")
    return suggestions

def analyze_dart(code):
    suggestions = []
    if re.search(r'print\(', code):
        suggestions.append("- Use `debugPrint()` or the `logging` package instead of `print()` to avoid missing long console outputs in Flutter.")
    if re.search(r'new\s+[A-Z]', code):
        suggestions.append("- The `new` keyword is optional in modern Dart. Remove it for cleaner code.")
    return suggestions

def execute_code_suggestion(slots):
    query = slots.get("query", "").strip()
    
    if not query:
        return {"status": "error", "message": "What code do you want me to suggest changes for?"}
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT description, code, source_path, language FROM code_snippets')
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {"status": "error", "message": "The code repository is completely empty. Start the indexer first!"}
            
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
            return {"status": "success", "message": f"I couldn't find any code matching '{query}' to suggest changes for."}
            
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
            return {"status": "success", "message": f"I couldn't find a strong match for '{query}' in the code database to analyze. (Highest match was {(best_score*100):.1f}%)"}
            
        desc, code, src, lang = best_match
        
        suggestions = []
        if lang in ["javascript", "typescript", "react"]:
            suggestions = analyze_js_ts(code)
        elif lang == "python":
            suggestions = analyze_python(code)
        elif lang == "dart":
            suggestions = analyze_dart(code)
            
        response_msg = f"I analyzed `{src}` ({lang}).\n\n"
        if not suggestions:
            response_msg += "Your code looks solidly written! I don't have any immediate classical heuristics to apply here."
        else:
            response_msg += "**Suggested Changes:**\n" + "\n".join(suggestions)
            
        response_msg += f"\n\n**Original Context:**\n```{lang}\n{code[:300]}{'...' if len(code) > 300 else ''}\n```"
        
        return {"status": "success", "message": response_msg, "code": code, "suggestions": suggestions, "source": src}
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to retrieve and analyze code: {str(e)}"}
