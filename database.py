import sqlite3

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
