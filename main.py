from fetcher import fetch_patents
from database import create_database, insert_patent

def main(keyword, limit=10, ipc_codes=None):
    create_database()
    patents, ipc_filter = fetch_patents(keyword, ipc_codes, limit)
    for patent in patents:
        insert_patent(patent, keyword, ipc_filter)
    print(f"Fetched and stored {len(patents)} patents for keyword '{keyword}' with IPC filter '{ipc_filter}'.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Scrape patents from Google Patents.")
    parser.add_argument("keyword", help="Search keyword")
    parser.add_argument("--limit", type=int, default=10, help="Number of patents to fetch")
    parser.add_argument("--ipc", nargs="*", help="IPC codes to filter by (e.g., C09 C23C)")
    args = parser.parse_args()
    main(args.keyword, args.limit, args.ipc)
