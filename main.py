from fetcher import fetch_patents
from database import create_database, insert_patent, get_patents, get_database_stats, get_database_info
import json

def fetch_and_store_patents(keyword, limit=10, ipc_codes=None):
    create_database()
    patents, ipc_filter = fetch_patents(keyword, ipc_codes, limit)
    for patent in patents:
        insert_patent(patent, keyword, ipc_filter)
    print(f"Fetched and stored {len(patents)} patents for keyword '{keyword}' with IPC filter '{ipc_filter}'.")

def display_patents(limit=10, keyword=None, ipc=None):
    patents = get_patents(limit, keyword, ipc)
    if not patents:
        print("No patents found matching the criteria.")
        return
    
    print(f"\nDisplaying {len(patents)} patents:\n")
    for i, patent in enumerate(patents, 1):
        print(f"[{i}] {patent['title']} (Patent: {patent['patent_number']})")
        print(f"    Published: {patent['publication_date']} | Keywords: {patent['search_keyword']}")
        if patent['ipc_filter'] and patent['ipc_filter'] != 'None':
            print(f"    IPC Filter: {patent['ipc_filter']}")
        if patent['assignees']:
            print(f"    Assignees: {patent['assignees']}")
        if patent['inventors']:
            print(f"    Inventors: {patent['inventors']}")
        if patent['abstract']:
            abstract = patent['abstract']
            if len(abstract) > 200:
                abstract = abstract[:200] + "..."
            print(f"    Abstract: {abstract}")
        print()

def display_database_stats():
    stats = get_database_stats()
    print("\nDatabase Statistics:")
    print(f"Total patents: {stats['total_patents']}")
    print(f"Unique keywords: {stats['unique_keywords']}")
    
    if stats['top_keywords']:
        print("\nTop keywords:")
        for keyword, count in stats['top_keywords']:
            print(f"  - {keyword}: {count} patents")
    
    if stats['top_ipc_filters']:
        print("\nTop IPC filters:")
        for ipc, count in stats['top_ipc_filters']:
            print(f"  - {ipc}: {count} patents")
    
    if stats['earliest_fetch'] and stats['latest_fetch']:
        print(f"\nDate range: {stats['earliest_fetch']} to {stats['latest_fetch']}")

def display_database_info():
    info = get_database_info()
    print("\nDatabase Information:")
    print(f"Database file size: {info['file_size']:.2f} MB")
    
    if info['schema']:
        print("\nSchema:")
        for col in info['schema']:
            col_id, name, type_name, not_null, default_val, pk = col
            print(f"  - {name} ({type_name}){' PRIMARY KEY' if pk else ''}{' NOT NULL' if not_null else ''}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Google Patents scraper and database tool.")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch patents from Google Patents")
    fetch_parser.add_argument("keyword", help="Search keyword")
    fetch_parser.add_argument("--limit", type=int, default=10, help="Number of patents to fetch")
    fetch_parser.add_argument("--ipc", nargs="*", help="IPC codes to filter by (e.g., C09 C23C)")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show patents from database")
    show_parser.add_argument("--limit", type=int, default=10, help="Number of patents to display")
    show_parser.add_argument("--keyword", help="Filter by keyword")
    show_parser.add_argument("--ipc", help="Filter by IPC code")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show database statistics")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show database information")
    
    args = parser.parse_args()
    
    create_database()  # Ensure database exists
    
    if args.command == "fetch":
        fetch_and_store_patents(args.keyword, args.limit, args.ipc)
    elif args.command == "show":
        display_patents(args.limit, args.keyword, args.ipc)
    elif args.command == "stats":
        display_database_stats()
    elif args.command == "info":
        display_database_info()
    else:
        # For backward compatibility, assume fetch if no command and keyword is given
        parser.print_help()

if __name__ == "__main__":
    main()
