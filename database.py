import sqlite3
from datetime import datetime

DATABASE_PATH = "patents.db"

def create_database():
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
                  fetch_date TEXT)''')
    conn.commit()
    conn.close()

def insert_patent(patent_data, keyword, ipc_filter):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO patents
                 (patent_number, title, abstract, publication_date, inventors, assignees, search_keyword, ipc_filter, fetch_date)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))''',
              (patent_data.get("patent_number"), patent_data.get("title"), patent_data.get("abstract"),
               patent_data.get("publication_date"), patent_data.get("inventors"), patent_data.get("assignees"),
               keyword, ipc_filter))
    conn.commit()
    conn.close()

def get_patents(limit=10, keyword=None, ipc=None):
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
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    stats = {}
    
    # Total number of patents
    c.execute("SELECT COUNT(*) FROM patents")
    stats["total_patents"] = c.fetchone()[0]
    
    # Number of unique keywords
    c.execute("SELECT COUNT(DISTINCT search_keyword) FROM patents")
    stats["unique_keywords"] = c.fetchone()[0]
    
    # Most common keywords
    c.execute("""
        SELECT search_keyword, COUNT(*) as count 
        FROM patents 
        GROUP BY search_keyword 
        ORDER BY count DESC 
        LIMIT 5
    """)
    stats["top_keywords"] = c.fetchall()
    
    # Most common IPC filters
    c.execute("""
        SELECT ipc_filter, COUNT(*) as count 
        FROM patents 
        GROUP BY ipc_filter 
        ORDER BY count DESC 
        LIMIT 5
    """)
    stats["top_ipc_filters"] = c.fetchall()
    
    # Latest fetch date
    c.execute("SELECT MAX(fetch_date) FROM patents")
    stats["latest_fetch"] = c.fetchone()[0]
    
    # Earliest fetch date
    c.execute("SELECT MIN(fetch_date) FROM patents")
    stats["earliest_fetch"] = c.fetchone()[0]
    
    conn.close()
    return stats

def get_database_info():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    info = {}
    
    # Get table schema
    c.execute("PRAGMA table_info(patents)")
    info["schema"] = c.fetchall()
    
    # Get database file size
    import os
    if os.path.exists(DATABASE_PATH):
        info["file_size"] = os.path.getsize(DATABASE_PATH) / (1024 * 1024)  # Size in MB
    else:
        info["file_size"] = 0
    
    conn.close()
    return info
