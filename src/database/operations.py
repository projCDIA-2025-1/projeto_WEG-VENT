"""Database CRUD operations."""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..config import DATABASE_PATH

def insert_patent(patent_data: Dict[str, Any], keyword: str, ipc_filter: str) -> bool:
    """Insert a patent into the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    try:
        c.execute('''INSERT OR IGNORE INTO patents
                     (patent_number, title, abstract, publication_date, filing_date, 
                      inventors, assignees, ipc_codes, search_keyword, ipc_filter, 
                      fetch_date, assignee_location, full_text, jurisdiction, 
                      international_family, citation_count, ai_summary)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?, ?, ?, ?, ?,?)''',
                  (patent_data.get("patent_number"), patent_data.get("title"), 
                   patent_data.get("abstract"), patent_data.get("publication_date"),
                   patent_data.get("filing_date"), patent_data.get("inventors"), 
                   patent_data.get("assignees"), patent_data.get("ipc_codes"),
                   keyword, ipc_filter, patent_data.get("assignee_location"), 
                   patent_data.get("full_text"), patent_data.get("jurisdiction"), 
                   patent_data.get("international_family"), patent_data.get("citation_count"), patent_data.get("ai_summary")))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error inserting patent: {e}")
        return False
    finally:
        conn.close()

def insert_ner_results(patent_number: str, entities: List[Dict[str, Any]]) -> bool:
    """Insert NER results for a patent."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    try:
        c.execute("DELETE FROM ner_results WHERE patent_number = ?", (patent_number,))
        
        for entity in entities:
            c.execute('''INSERT INTO ner_results
                         (patent_number, entity_type, entity_text, start_pos, end_pos, 
                          confidence, created_date)
                         VALUES (?, ?, ?, ?, ?, ?, datetime('now'))''',
                      (patent_number, entity.get('label'), entity.get('text'),
                       entity.get('start'), entity.get('end'), entity.get('confidence', 1.0)))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error inserting NER results: {e}")
        return False
    finally:
        conn.close()

def get_patents(limit: int = 10, keyword: Optional[str] = None, 
                ipc: Optional[str] = None) -> List[Dict[str, Any]]:
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

def get_ner_results(patent_number: str) -> List[Dict[str, Any]]:
    """Get NER results for a specific patent."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("""SELECT entity_type, entity_text, start_pos, end_pos, confidence 
                 FROM ner_results 
                 WHERE patent_number = ? 
                 ORDER BY start_pos""", (patent_number,))
    
    results = [dict(row) for row in c.fetchall()]
    conn.close()
    return results

def get_patents_with_ner(keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get patents with their NER results."""
    patents = get_patents(keyword=keyword, limit=100)
    
    for patent in patents:
        patent['ner_results'] = get_ner_results(patent['patent_number'])
    
    return patents

def get_database_stats() -> Dict[str, Any]:
    """Get database statistics."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    stats = {}
    
    c.execute("SELECT COUNT(*) FROM patents")
    stats["total_patents"] = c.fetchone()[0]
    
    c.execute("SELECT COUNT(DISTINCT search_keyword) FROM patents")
    stats["unique_keywords"] = c.fetchone()[0]
    
    c.execute("""SELECT search_keyword, COUNT(*) as count 
                 FROM patents 
                 GROUP BY search_keyword 
                 ORDER BY count DESC 
                 LIMIT 5""")
    stats["top_keywords"] = c.fetchall()
    
    c.execute("SELECT COUNT(*) FROM ner_results")
    stats["total_entities"] = c.fetchone()[0]
    
    c.execute("""SELECT entity_type, COUNT(*) as count 
                 FROM ner_results 
                 GROUP BY entity_type 
                 ORDER BY count DESC""")
    stats["entity_counts"] = c.fetchall()
    
    c.execute("SELECT MAX(fetch_date) FROM patents")
    stats["latest_fetch"] = c.fetchone()[0]
    
    c.execute("SELECT MIN(fetch_date) FROM patents")
    stats["earliest_fetch"] = c.fetchone()[0]
    
    # Add citation and region statistics
    c.execute("SELECT SUM(citation_count) FROM patents WHERE citation_count IS NOT NULL")
    result = c.fetchone()
    stats["total_citations"] = result[0] if result[0] is not None else 0
    
    c.execute("SELECT AVG(citation_count) FROM patents WHERE citation_count IS NOT NULL")
    result = c.fetchone()
    stats["avg_citations"] = round(result[0], 2) if result[0] is not None else 0
    
    c.execute("SELECT COUNT(DISTINCT jurisdiction) FROM patents WHERE jurisdiction IS NOT NULL")
    stats["unique_jurisdictions"] = c.fetchone()[0]
    
    c.execute("""SELECT jurisdiction, COUNT(*) as count 
                 FROM patents 
                 WHERE jurisdiction IS NOT NULL 
                 GROUP BY jurisdiction 
                 ORDER BY count DESC""")
    stats["jurisdiction_counts"] = c.fetchall()
    
    conn.close()
    return stats

def get_citation_and_region_stats(patents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get citation and region statistics for a specific set of patents."""
    stats = {}
    
    # Citation statistics
    citations = [p.get('citation_count', 0) for p in patents if p.get('citation_count') is not None]
    stats['total_citations'] = sum(citations)
    stats['avg_citations'] = round(sum(citations) / len(citations), 2) if citations else 0
    stats['max_citations'] = max(citations) if citations else 0
    
    # Region statistics
    jurisdictions = [p.get('jurisdiction') for p in patents if p.get('jurisdiction')]
    unique_jurisdictions = list(set(jurisdictions))
    stats['unique_regions'] = len(unique_jurisdictions)
    stats['regions_list'] = unique_jurisdictions
    
    # Count patents per region
    region_counts = {}
    for jurisdiction in jurisdictions:
        region_counts[jurisdiction] = region_counts.get(jurisdiction, 0) + 1
    stats['region_distribution'] = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)
    
    return stats
