"""Main patent scraping logic."""

import time
import json
from typing import List, Dict, Optional, Tuple
from .fetcher import ExtendedScraper, build_search_params, fetch_patents_data, extract_patent_numbers_from_json
from ..config import DEFAULT_PATENT_LIMIT, SCRAPING_DELAY
from ..utils import extract_country_code
from .prompt_eng import summarize_with_ollama
from langdetect import detect

def is_english_text(text: str) -> bool:
    try:
        return detect(text) == "en"
    except Exception:
        return False

def fetch_patents(keyword: str, ipc_codes: Optional[List[str]] = None, 
                 limit: int = DEFAULT_PATENT_LIMIT, fetch_full_text: bool = False) -> Tuple[List[Dict], str]:
    """Fetch patents matching keyword and IPC codes, with detailed scraping."""
    scraper = ExtendedScraper(return_abstract=True)
    search_params = build_search_params(keyword, ipc_codes)
    page = 0
    patent_numbers = []
    aux = []
    # Collect patent numbers from search results
    while len(patent_numbers) < limit:
        if page > 0:
            search_params["page"] = page
        else:
            search_params.pop("page", None)
        json_data = fetch_patents_data(search_params)
        page_patents = extract_patent_numbers_from_json(json_data)
        
        for patent in page_patents:
            print("Processing patent:", patent)
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
        # if not page_patents:
            # break
        patent_numbers.extend(aux[:limit - len(patent_numbers)])
        # if len(page_patents) < 10:
            # break
        page += 1
        time.sleep(1)

    # Add patent numbers to scraper
    for pn in patent_numbers:
        scraper.add_patents(pn)

    # Scrape detailed data for all patents
    scraper.scrape_all_patents(fetch_full_text=fetch_full_text)

    # Collect and format patent data
    patents = []
    for pn in patent_numbers:
        if pn in scraper.parsed_patents:
            parsed = scraper.parsed_patents[pn]
            # Extract jurisdiction from patent number
            jurisdiction = extract_country_code(pn)
            
            # Parse international patent family
            forward_cites = json.loads(parsed.get('forward_cite_no_family', '[]')) + json.loads(parsed.get('forward_cite_yes_family', '[]'))
            backward_cites = json.loads(parsed.get('backward_cite_no_family', '[]')) + json.loads(parsed.get('backward_cite_yes_family', '[]'))
            intl_family = list(set([cite['patent_number'] for cite in forward_cites + backward_cites if cite['patent_number'] != pn]))
            intl_family_str = ", ".join(intl_family) if intl_family else None
            
            # Calculate citation count
            citation_count = len(forward_cites)
            abstract = parsed.get('abstract_text', '')
            full_text = parsed.get('full_text', '')
            print(is_english_text(abstract))
            data = {
                "patent_number": pn,
                "title": parsed.get('title', ''),
                "abstract": abstract,
                "publication_date": parsed.get('pub_date', ''),
                "filing_date": parsed.get('priority_date', ''),
                "inventors": ", ".join([inv['inventor_name'] for inv in json.loads(parsed['inventor_name'])] if parsed.get('inventor_name') else []),
                "assignees": ", ".join([ass['assignee_name'] for ass in json.loads(parsed['assignee_name_current'])] if parsed.get('assignee_name_current') else []),
                "ipc_codes": ", ".join(parsed.get('ipc_code', [])),
                "assignee_location": parsed.get('assignee_location', ''),
                "full_text": full_text,
                "jurisdiction": jurisdiction,
                "international_family": intl_family_str,
                "citation_count": citation_count,
                "ai_summary" : summarize_with_ollama(abstract, full_text)
            }
            print(data["ai_summary"])
            patents.append(data)

    ipc_filter = ",".join(ipc_codes) if ipc_codes else "None"
    return patents, ipc_filter
