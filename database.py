import sqlite3
from datetime import datetime

DATABASE_PATH = "patents.db"

def migrate_database():
    """Ensure the patents table has all required columns."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute("PRAGMA table_info(patents)")
    columns = [col[1] for col in c.fetchall()]
    print(f"Existing columns in patents table: {columns}")
    
    # Add missing columns
    for col in ["assignee_location", "full_text", "jurisdiction", "international_family", "citation_count"]:
        if col not in columns:
            print(f"Adding {col} column...")
            dtype = "INTEGER" if col == "citation_count" else "TEXT"
            c.execute(f"ALTER TABLE patents ADD COLUMN {col} {dtype}")
    
    conn.commit()
    conn.close()

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
                  inventors TEXT,
                  assignees TEXT,
                  search_keyword TEXT,
                  ipc_filter TEXT,
                  fetch_date TEXT,
                  assignee_location TEXT,
                  full_text TEXT,
                  jurisdiction TEXT,
                  international_family TEXT,
                  citation_count INTEGER)''')
    conn.commit()
    conn.close()
    migrate_database()

def insert_patent(patent_data, keyword, ipc_filter):
    """Insert a patent into the database, including new fields."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    print(f"Inserting patent: {patent_data}")
    print(f"Keyword: {keyword}, IPC Filter: {ipc_filter}")
    
    c.execute('''INSERT OR IGNORE INTO patents
                 (patent_number, title, abstract, publication_date, inventors, assignees, search_keyword, ipc_filter, fetch_date, assignee_location, full_text, jurisdiction, international_family, citation_count)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?, ?, ?, ?, ?)''',
              (patent_data.get("patent_number"), patent_data.get("title"), patent_data.get("abstract"),
               patent_data.get("publication_date"), patent_data.get("inventors"), patent_data.get("assignees"),
               keyword, ipc_filter, patent_data.get("assignee_location"), patent_data.get("full_text"),
               patent_data.get("jurisdiction"), patent_data.get("international_family"), patent_data.get("citation_count")))
    conn.commit()
    conn.close()

def get_patents(limit=10, keyword=None, ipc=None):
    """Retrieve patents from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    query = "SELECT * FROM patents"
    params = []
    
    conditions = []
    if keyword:
        conditions.append("search_keyword LIKE ?")
        params.append(f"%{keyword}%")
    if ipc:
        conditions.append("ipc_filter LIKE ?")
        params.append(f"%{ipc}%")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY fetch_date DESC LIMIT ?"
    params.append(limit)
    
    c.execute(query, params)
    results = [dict(row) for row in c.fetchall()]
    conn.close()
    return results

def get_database_stats():
    """Get database statistics."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    stats = {}
    
    c.execute("SELECT COUNT(*) FROM patents")
    stats["total_patents"] = c.fetchone()[0]
    
    c.execute("SELECT COUNT(DISTINCT search_keyword) FROM patents")
    stats["unique_keywords"] = c.fetchone()[0]
    
    c.execute("""
        SELECT search_keyword, COUNT(*) as count 
        FROM patents 
        GROUP BY search_keyword 
        ORDER BY count DESC 
        LIMIT 5
    """)
    stats["top_keywords"] = c.fetchall()
    
    c.execute("""
        SELECT ipc_filter, COUNT(*) as count 
        FROM patents 
        GROUP BY ipc_filter 
        ORDER BY count DESC 
        LIMIT 5
    """)
    stats["top_ipc_filters"] = c.fetchall()
    
    c.execute("SELECT MAX(fetch_date) FROM patents")
    stats["latest_fetch"] = c.fetchone()[0]
    
    c.execute("SELECT MIN(fetch_date) FROM patents")
    stats["earliest_fetch"] = c.fetchone()[0]
    
    conn.close()
    return stats

def get_database_info():
    """Get database information."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    info = {}
    
    c.execute("PRAGMA table_info(patents)")
    info["schema"] = c.fetchall()
    
    print("\nCurrent database schema:")
    for col in info["schema"]:
        col_id, name, type_name, not_null, default_val, pk = col
        print(f"  - {name} ({type_name}){' PRIMARY KEY' if pk else ''}{' NOT NULL' if not_null else ''}")
    
    import os
    if os.path.exists(DATABASE_PATH):
        info["file_size"] = os.path.getsize(DATABASE_PATH) / (1024 * 1024)
    else:
        info["file_size"] = 0
    
    conn.close()
    return info
