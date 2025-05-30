"""Database models and schema definitions."""

import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional
from ..config import DATABASE_PATH

def create_database():
    """Create the patents database with all fields and migrate if needed."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS patents
                 (id INTEGER PRIMARY KEY,
                  patent_number TEXT UNIQUE,
                  title TEXT,
                  abstract TEXT,
                  publication_date TEXT,
                  filing_date TEXT,
                  inventors TEXT,
                  assignees TEXT,
                  ipc_codes TEXT,
                  search_keyword TEXT,
                  ipc_filter TEXT,
                  fetch_date TEXT,
                  assignee_location TEXT,
                  full_text TEXT,
                  jurisdiction TEXT,
                  international_family TEXT,
                  citation_count INTEGER,
                  ai_summary TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS ner_results
                 (id INTEGER PRIMARY KEY,
                  patent_number TEXT,
                  entity_type TEXT,
                  entity_text TEXT,
                  start_pos INTEGER,
                  end_pos INTEGER,
                  confidence REAL,
                  created_date TEXT,
                  FOREIGN KEY (patent_number) REFERENCES patents (patent_number))''')
    
    conn.commit()
    conn.close()
    migrate_database()

def migrate_database():
    """Ensure the patents table has all required columns."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute("PRAGMA table_info(patents)")
    columns = [col[1] for col in c.fetchall()]
    
    missing_columns = {
        "filing_date": "TEXT",
        "ipc_codes": "TEXT", 
        "assignee_location": "TEXT",
        "full_text": "TEXT",
        "jurisdiction": "TEXT",
        "international_family": "TEXT",
        "citation_count": "INTEGER"
    }
    
    for col, dtype in missing_columns.items():
        if col not in columns:
            print(f"Adding {col} column to patents table...")
            c.execute(f"ALTER TABLE patents ADD COLUMN {col} {dtype}")
    
    conn.commit()
    conn.close()

def get_database_info():
    """Get database information."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    info = {}
    
    c.execute("PRAGMA table_info(patents)")
    info["patents_schema"] = c.fetchall()
    
    c.execute("PRAGMA table_info(ner_results)")
    info["ner_schema"] = c.fetchall()
    
    import os
    if os.path.exists(DATABASE_PATH):
        info["file_size"] = os.path.getsize(DATABASE_PATH) / (1024 * 1024)
    else:
        info["file_size"] = 0
    
    conn.close()
    return info
