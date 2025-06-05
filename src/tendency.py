"""Patent tendency detection system for market trend analysis."""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import Counter
import time

from .scraper.fetcher import build_search_params, fetch_patents_data, extract_patent_numbers_from_json
from .scraper.fetcher import ExtendedScraper
from .utils import ensure_directory_exists
from .scraper.patent_scraper import is_english_text
# IPC codes with relevant search keywords
TARGET_IPC_CODES = {
    "C09": ["coating", "paint", "dye", "adhesive", "polymer coating"],    # Dyes, paints, polishes, natural resins, adhesives
    "C23C": ["metal coating", "surface treatment", "plating", "corrosion protection"],   # Coating metallic material
    "C08F": ["polymerization", "polymer synthesis", "monomer", "plastic"],   # Macromolecular compounds from C-C bonds
    "C08G": ["polymer", "resin", "condensation", "polyester", "polyurethane"],   # Other macromolecular compounds
}

MONTHS_LOOKBACK = 2
TENDENCIES_DIR = "tendencies_data"
MAX_PATENTS_PER_IPC = 30  # Reduced for faster testing
MIN_KEYWORD_LENGTH = 3
COMMON_WORDS_TO_EXCLUDE = {
    'the', 'and', 'for', 'are', 'with', 'from', 'that', 'this', 'can', 'may',
    'said', 'such', 'one', 'two', 'more', 'than', 'least', 'about', 'other',
    'method', 'system', 'device', 'apparatus', 'process', 'invention', 'present',
    'example', 'embodiment', 'according', 'wherein', 'comprising', 'including',
    'patent', 'application', 'claim', 'figure', 'step', 'first', 'second',
    'third', 'plurality', 'substantially', 'preferably', 'particularly'
}

def get_date_range(months_back: int = MONTHS_LOOKBACK) -> Tuple[str, str]:
    """Get date range for patent search (YYYY-MM-DD format)."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months_back * 30)  # Approximate months
    
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

def extract_keywords_from_text(text: str) -> List[str]:
    """Extract meaningful keywords from patent text."""
    if not text:
        return []
    
    # Convert to lowercase and remove special characters
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Split into words
    words = text.split()
    
    # Filter words
    keywords = []
    for word in words:
        # Skip if too short, too long, or common word
        if (len(word) >= MIN_KEYWORD_LENGTH and 
            len(word) <= 20 and 
            word not in COMMON_WORDS_TO_EXCLUDE and
            not word.isdigit()):
            keywords.append(word)
    
    return keywords

def extract_technical_phrases(text: str) -> List[str]:
    """Extract technical phrases (2-3 word combinations) from patent text."""
    if not text:
        return []
    
    # Clean text
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = [w for w in text.split() if len(w) >= 3 and w not in COMMON_WORDS_TO_EXCLUDE]
    
    phrases = []
    
    # Extract 2-word phrases
    for i in range(len(words) - 1):
        phrase = f"{words[i]} {words[i+1]}"
        if len(phrase) <= 30:  # Reasonable phrase length
            phrases.append(phrase)
    
    # Extract 3-word phrases
    for i in range(len(words) - 2):
        phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
        if len(phrase) <= 40:  # Reasonable phrase length
            phrases.append(phrase)
    
    return phrases

def scrape_patents_for_ipc(ipc_code: str, keywords: List[str], limit: int = MAX_PATENTS_PER_IPC) -> List[Dict]:
    """Scrape patents for a specific IPC code using relevant keywords."""
    print(f"Scraping patents for IPC: {ipc_code} with keywords: {keywords}")
    
    scraper = ExtendedScraper(return_abstract=True)
    all_patent_numbers = []
    
    incremental_delay = 1
    # Try each keyword for this IPC code
    for keyword in keywords:
        print(f"  Searching with keyword: '{keyword}'")
        
        # Build search parameters with keyword and IPC filter
        search_params = build_search_params(keyword, [ipc_code])
        
        patent_numbers = []
        page = 0
        # Collect patent numbers for this keyword
        while len(patent_numbers) < limit // len(keywords) and page < 3:  # Distribute limit across keywords
            if page > 0:
                search_params["page"] = page
            else:
                search_params.pop("page", None)
                
            try:
                aux = []
                json_data = fetch_patents_data(search_params)
                page_patents = extract_patent_numbers_from_json(json_data)
                
                # if not page_patents:
                    # break
                for patent in page_patents:
            # print("Processing patent:", patent)
                    result, soup, url =  scraper.request_single_patent(patent)
                    if result != 'Success':
                        print(f"Error fetching patent {patent}: {result}")
                        page_patents.remove(patent)
                        continue
                    patent_dict = scraper.get_scraped_data(soup, patent, url)
                    abstract = patent_dict.get('abstract_text', '')
                    if(not is_english_text(abstract)):
                        page_patents.remove(patent)
                        continue
                    else:
                        aux.append(patent) # this process right here might be a bottleneck, as it deletes patents that are not in English and this process is kinda slow by now, we might 
                                   # investigate to see if we can do this in parallel or something like that   
                patent_numbers.extend(aux[:limit // len(keywords) - len(patent_numbers)])
                page += 1
                time.sleep(1)  # Rate limiting
                print(f"time waited :: {1} seconds")
                incremental_delay += 1
            except Exception as e:
                print(f"    Error fetching patents for {ipc_code} with keyword '{keyword}': {e}")
                break
        
        all_patent_numbers.extend(patent_numbers)
        print(f"    Found {len(patent_numbers)} patents for keyword '{keyword}'")
        
        if len(all_patent_numbers) >= limit:
            break
    
    # Remove duplicates while preserving order
    unique_patents = []
    seen = set()
    for pn in all_patent_numbers:
        if pn not in seen:
            unique_patents.append(pn)
            seen.add(pn)
    
    if not unique_patents:
        return []
    
    # Limit to max patents
    unique_patents = unique_patents[:limit]
    
    # Add patents to scraper
    for pn in unique_patents:
        scraper.add_patents(pn)
    
    # Scrape patent details (abstracts only for speed)
    scraper.scrape_all_patents(fetch_full_text=False)
    
    # Extract relevant data
    patents_data = []
    for pn in unique_patents:
        if pn in scraper.parsed_patents:
            parsed = scraper.parsed_patents[pn]
            
            # Filter by publication date if available
            pub_date = parsed.get('pub_date', '')
            
            patent_data = {
                'patent_number': pn,
                'title': parsed.get('title', ''),
                'abstract': parsed.get('abstract_text', ''),
                'publication_date': pub_date,
                'ipc_code': ipc_code
            }
            patents_data.append(patent_data)
    
    print(f"Successfully scraped {len(patents_data)} patents for {ipc_code}")
    return patents_data

def analyze_patent_keywords(patents_data: List[Dict]) -> Dict[str, any]:
    """Analyze keywords and phrases from patent data."""
    all_keywords = []
    all_phrases = []
    
    for patent in patents_data:
        # Extract from title and abstract
        title_text = patent.get('title', '')
        abstract_text = patent.get('abstract', '')
        combined_text = f"{title_text} {abstract_text}"
        
        # Extract keywords and phrases
        keywords = extract_keywords_from_text(combined_text)
        phrases = extract_technical_phrases(combined_text)
        
        all_keywords.extend(keywords)
        all_phrases.extend(phrases)
    
    # Count frequencies
    keyword_counts = Counter(all_keywords)
    phrase_counts = Counter(all_phrases)
    
    # Get top results
    top_keywords = keyword_counts.most_common(50)
    top_phrases = phrase_counts.most_common(30)
    
    return {
        'total_patents': len(patents_data),
        'total_keywords': len(all_keywords),
        'unique_keywords': len(keyword_counts),
        'top_keywords': top_keywords,
        'top_phrases': top_phrases,
        'keyword_distribution': dict(keyword_counts),
        'phrase_distribution': dict(phrase_counts)
    }

def run_tendency_analysis() -> Dict[str, any]:
    """Run complete tendency analysis for all target IPC codes."""
    print("Starting patent tendency analysis...")
    
    start_date, end_date = get_date_range(MONTHS_LOOKBACK)
    print(f"Analyzing patents from {start_date} to {end_date}")
    
    analysis_results = {
        'analysis_date': datetime.now().isoformat(),
        'date_range': {
            'start': start_date,
            'end': end_date,
            'months_back': MONTHS_LOOKBACK
        },
        'ipc_codes_analyzed': list(TARGET_IPC_CODES.keys()),
        'ipc_results': {},
        'global_trends': {}
    }
    
    all_patents = []
    
    # Analyze each IPC code
    for ipc_code, keywords in TARGET_IPC_CODES.items():
        try:
            patents_data = scrape_patents_for_ipc(ipc_code, keywords, MAX_PATENTS_PER_IPC)
            
            if patents_data:
                ipc_analysis = analyze_patent_keywords(patents_data)
                analysis_results['ipc_results'][ipc_code] = ipc_analysis
                all_patents.extend(patents_data)
                
                print(f"IPC {ipc_code}: {ipc_analysis['total_patents']} patents, "
                      f"{ipc_analysis['unique_keywords']} unique keywords")
            else:
                print(f"No patents found for IPC {ipc_code}")
                
        except Exception as e:
            print(f"Error analyzing IPC {ipc_code}: {e}")
            continue
    
    # Global trend analysis
    if all_patents:
        global_analysis = analyze_patent_keywords(all_patents)
        analysis_results['global_trends'] = global_analysis
        
        print(f"\nGlobal analysis: {global_analysis['total_patents']} total patents, "
              f"{global_analysis['unique_keywords']} unique keywords")
    
    return analysis_results

def save_tendency_results(results: Dict[str, any], filename: str = None) -> str:
    """Save tendency analysis results to JSON file."""
    ensure_directory_exists(TENDENCIES_DIR)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m")
        filename = f"tendencies_{timestamp}.json"
    
    filepath = os.path.join(TENDENCIES_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Tendency analysis saved to: {filepath}")
    return filepath

def get_tendencies(month: str = None) -> Optional[Dict[str, any]]:
    """
    Get tendency analysis results for a specific month.
    
    Args:
        month (str): Month in YYYYMM format. If None, uses current month.
    
    Returns:
        Dict containing tendency analysis or None if not found.
    """
    if month is None:
        month = datetime.now().strftime("%Y%m")
    
    filename = f"tendencies_{month}.json"
    filepath = os.path.join(TENDENCIES_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"Tendency file not found: {filepath}")
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading tendency file: {e}")
        return None

def get_latest_tendencies() -> Optional[Dict[str, any]]:
    """Get the most recent tendency analysis available."""
    ensure_directory_exists(TENDENCIES_DIR)
    
    # Find all tendency files
    tendency_files = [f for f in os.listdir(TENDENCIES_DIR) if f.startswith('tendencies_') and f.endswith('.json')]
    
    if not tendency_files:
        return None
    
    # Sort by filename (which includes date) and get the latest
    latest_file = sorted(tendency_files)[-1]
    filepath = os.path.join(TENDENCIES_DIR, latest_file)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading latest tendency file: {e}")
        return None

def print_tendency_summary(results: Dict[str, any]):
    """Print a summary of tendency analysis results."""
    if not results:
        print("No tendency results to display")
        return
    
    print("\n" + "="*60)
    print("PATENT TENDENCY ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"Analysis Date: {results.get('analysis_date', 'Unknown')}")
    date_range = results.get('date_range', {})
    print(f"Date Range: {date_range.get('start')} to {date_range.get('end')}")
    print(f"Months Analyzed: {date_range.get('months_back', 'Unknown')}")
    
    global_trends = results.get('global_trends', {})
    if global_trends:
        print(f"\nGlobal Statistics:")
        print(f"  Total Patents: {global_trends.get('total_patents', 0)}")
        print(f"  Unique Keywords: {global_trends.get('unique_keywords', 0)}")
        
        print(f"\nTop 10 Trending Keywords:")
        for i, (keyword, count) in enumerate(global_trends.get('top_keywords', [])[:10], 1):
            print(f"  {i:2d}. {keyword}: {count}")
        
        print(f"\nTop 5 Trending Phrases:")
        for i, (phrase, count) in enumerate(global_trends.get('top_phrases', [])[:5], 1):
            print(f"  {i}. {phrase}: {count}")
    
    print("\nIPC Code Analysis:")
    ipc_results = results.get('ipc_results', {})
    for ipc_code, ipc_data in ipc_results.items():
        print(f"  {ipc_code}: {ipc_data.get('total_patents', 0)} patents")

def main():
    """Main function to run tendency analysis."""
    print("Patent Tendency Detector")
    print("Analyzing recent patent trends...")
    
    # Run analysis
    results = run_tendency_analysis()
    
    # Save results
    filepath = save_tendency_results(results)
    
    # Print summary
    print_tendency_summary(results)
    
    return results

if __name__ == "__main__":
    main()
