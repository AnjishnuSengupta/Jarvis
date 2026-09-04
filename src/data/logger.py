import sqlite3
import json
import os
import datetime

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "jarvis.db"))

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Interactions table for the Learning Loop
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            raw_text TEXT,
            predicted_intent TEXT,
            confidence REAL,
            extracted_slots TEXT,
            needs_review BOOLEAN,
            was_corrected BOOLEAN,
            corrected_intent TEXT
        )
    ''')
    
    # Memories table for Phase 10
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            fact TEXT
        )
    ''')
    
    # Code snippets table for Phase 21
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS code_snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            code TEXT,
            source_path TEXT,
            language TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def log_interaction(raw_text, predicted_intent, confidence, extracted_slots):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    needs_review = confidence < 0.6
    timestamp = datetime.datetime.now().isoformat()
    slots_json = json.dumps(extracted_slots)
    
    cursor.execute('''
        INSERT INTO interactions 
        (timestamp, raw_text, predicted_intent, confidence, extracted_slots, needs_review, was_corrected) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, raw_text, predicted_intent, confidence, slots_json, needs_review, False))
    
    conn.commit()
    conn.close()
    
    return needs_review

def get_flagged_interactions():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, raw_text, predicted_intent, confidence 
        FROM interactions 
        WHERE needs_review = 1 AND was_corrected = 0
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_interaction(interaction_id, corrected_intent):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE interactions 
        SET was_corrected = 1, needs_review = 0, corrected_intent = ? 
        WHERE id = ?
    ''', (corrected_intent, interaction_id))
    
    conn.commit()
    conn.close()

def get_all_reviewed_data():
    """Returns data formatted exactly like the synthetic dataset for retraining."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all interactions that were either high confidence to begin with, or have been corrected.
    cursor.execute('''
        SELECT raw_text, predicted_intent, was_corrected, corrected_intent 
        FROM interactions 
        WHERE (needs_review = 0 AND was_corrected = 0) OR (was_corrected = 1)
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    dataset = []
    for row in rows:
        raw_text, predicted_intent, was_corrected, corrected_intent = row
        intent = corrected_intent if was_corrected else predicted_intent
        dataset.append({
            "text": raw_text,
            "intent": intent
        })
        
    return dataset
