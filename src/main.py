"""Main application entry point for the patent analysis system."""

import argparse
import os
from typing import List, Optional

from .config import DEFAULT_PATENT_LIMIT, REPORTS_OUTPUT_DIR
from .database import (
    create_database, insert_patent, insert_ner_results, 
    get_patents_with_ner, get_database_stats
)
from .scraper import fetch_patents
from .ner import Model
from .reports import generate_patent_report
from .utils import ensure_directory_exists

def fetch_and_process_patents(keywords: str, ipc_codes: Optional[List[str]] = None, 
                            limit: int = DEFAULT_PATENT_LIMIT, 
                            fetch_full_text: bool = False) -> None:
    """Fetch patents, run NER, and store results."""
    print(f"Fetching patents for keywords: {keywords}")
    
    # Fetch patents
    patents, ipc_filter = fetch_patents(keywords, ipc_codes, limit, fetch_full_text)
    print(f"Found {len(patents)} patents")

    model = Model()
    
    # Process each patent
    for patent in patents:
        # Store patent in database
        insert_patent(patent, keywords, ipc_filter)
        print(f"Stored patent: {patent['patent_number']}")
        
        # Run NER on abstract
        #  entities = process_patent_abstract(patent)
        print(patent)
        txt = patent["abstract"] or ""
        entities = model.predict(txt)
        if entities:
            insert_ner_results(patent['patent_number'], entities)
            print(f"Stored {len(entities)} entities for patent {patent['patent_number']}")
        else:
            print(f"No entities found for patent {patent['patent_number']}")

def generate_report_for_keywords(keywords: str, output_dir: str = None) -> str:
    """Generate a report for patents matching keywords."""
    if output_dir is None:
        output_dir = REPORTS_OUTPUT_DIR
    
    ensure_directory_exists(output_dir)
    
    # Get patents with NER results
    patents_with_entities = get_patents_with_ner(keyword=keywords)
    
    if not patents_with_entities:
        print(f"No patents found for keywords: {keywords}")
        return None
    
    print(f"Generating report for {len(patents_with_entities)} patents")
    
    # Generate the report
    report_path = generate_patent_report(patents_with_entities, keywords, output_dir)
    return report_path

def show_database_statistics():
    """Display database statistics."""
    stats = get_database_stats()
    
    print("\n=== Database Statistics ===")
    print(f"Total patents: {stats['total_patents']}")
    print(f"Total entities: {stats['total_entities']}")
    print(f"Unique keywords: {stats['unique_keywords']}")
    
    # Citation statistics
    print(f"\n=== Citation Statistics ===")
    print(f"Total citations: {stats.get('total_citations', 0)}")
    print(f"Average citations per patent: {stats.get('avg_citations', 0)}")
    
    # Region statistics
    print(f"\n=== Regional Distribution ===")
    print(f"Unique jurisdictions: {stats.get('unique_jurisdictions', 0)}")
    
    if stats.get('jurisdiction_counts'):
        print("\nPatents by jurisdiction:")
        for jurisdiction, count in stats['jurisdiction_counts']:
            print(f"  - {jurisdiction}: {count} patents")
    
    if stats['top_keywords']:
        print("\n=== Top Keywords ===")
        for keyword, count in stats['top_keywords']:
            print(f"  - {keyword}: {count} patents")
    
    if stats['entity_counts']:
        print("\n=== Entity Type Distribution ===")
        for entity_type, count in stats['entity_counts']:
            print(f"  - {entity_type}: {count} entities")
    
    if stats['earliest_fetch'] and stats['latest_fetch']:
        print(f"\nData range: {stats['earliest_fetch']} to {stats['latest_fetch']}")

def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Patent Analysis System - Fetch, analyze, and report on patents"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch and process patents")
    fetch_parser.add_argument("keywords", help="Search keywords")
    fetch_parser.add_argument("--limit", type=int, default=DEFAULT_PATENT_LIMIT, 
                            help="Number of patents to fetch")
    fetch_parser.add_argument("--ipc", nargs="*", help="IPC codes to filter by")
    fetch_parser.add_argument("--full-text", action="store_true", 
                            help="Fetch full patent text (slower)")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate HTML report")
    report_parser.add_argument("keywords", help="Keywords to filter patents")
    report_parser.add_argument("--output", help="Output directory for report")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show database statistics")
    
    # Process command (fetch + report)
    process_parser = subparsers.add_parser("process", 
                                         help="Fetch patents and generate report")
    process_parser.add_argument("keywords", help="Search keywords")
    process_parser.add_argument("--limit", type=int, default=DEFAULT_PATENT_LIMIT,
                              help="Number of patents to fetch")
    process_parser.add_argument("--ipc", nargs="*", help="IPC codes to filter by")
    process_parser.add_argument("--output", help="Output directory for report")
    
    args = parser.parse_args()
    
    # Initialize database
    create_database()
    
    if args.command == "fetch":
        fetch_and_process_patents(args.keywords, args.ipc, args.limit, args.full_text)
        
    elif args.command == "report":
        report_path = generate_report_for_keywords(args.keywords, args.output)
        if report_path:
            print(f"Report saved to: {report_path}")
            
    elif args.command == "stats":
        show_database_statistics()
        
    elif args.command == "process":
        # Fetch and process patents
        fetch_and_process_patents(args.keywords, args.ipc, args.limit, False)
        # Generate report
        report_path = generate_report_for_keywords(args.keywords, args.output)
        if report_path:
            print(f"Complete! Report saved to: {report_path}")
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
