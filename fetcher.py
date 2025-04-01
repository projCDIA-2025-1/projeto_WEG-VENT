import requests
import urllib.parse
import time
import re
from bs4 import BeautifulSoup
from google_patent_scraper import scraper_class
import json

def build_search_params(keyword, ipc_codes=None, page=None):
    """Build search parameters for Google Patents XHR query."""
    params = {"q": keyword}
    if ipc_codes:
        params["classification"] = "+OR+".join(ipc_codes)
    if page is not None:
        params["page"] = page
    return params

def fetch_patents_data(search_params):
    """Fetch patent search results from Google Patents XHR endpoint."""
    xhr_url = "https://patents.google.com/xhr/query"
    query_string = urllib.parse.urlencode(search_params)
    params = {"url": query_string, "exp": "", "tags": ""}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Referer": "https://patents.google.com/",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9"
    }
    response = requests.get(xhr_url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

def extract_patent_numbers_from_json(json_data):
    """Extract patent numbers from search results JSON."""
    patent_numbers = []
    if isinstance(json_data, dict) and "results" in json_data:
        results = json_data["results"]
        if isinstance(results, dict) and "cluster" in results:
            for result_item in results["cluster"]:
                if "result" in result_item and isinstance(result_item["result"], list):
                    for item in result_item["result"]:
                        if "patent" in item:
                            patent = item["patent"]
                            patent_numbers.append(patent.get("publication_number"))
    return patent_numbers

class ExtendedScraper(scraper_class):
    """Extended scraper class to include additional fields."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def request_single_patent(self, patent):
        """Override to use html.parser instead of lxml."""
        url = f'https://patents.google.com/patent/{patent}'
        webpage = requests.get(url)
        soup = BeautifulSoup(webpage.text, 'html.parser')
        return 'Success', soup, url

    def scrape_all_patents(self, fetch_full_text=False):
        """Scrape all patents, adding custom fields."""
        for patent in self.list_of_patents:
            err, soup, url = self.request_single_patent(patent)
            if err == 'Success':
                patent_dict = self.get_scraped_data(soup, patent, url)
                patent_dict['assignee_location'] = self.extract_location(soup)
                patent_dict['full_text'] = self.extract_full_text(soup) if fetch_full_text else None
                self.parsed_patents[patent] = patent_dict
            else:
                print(f'Error scraping patent {patent}')
            time.sleep(2)  # Delay to prevent server overload

    def extract_location(self, soup):
        """Extract assignee location from patent page."""
        assignee_section = soup.find('section', {'itemprop': 'assignees'})
        if assignee_section:
            assignee_text = assignee_section.get_text(strip=True)
            match = re.search(r'\((.*?)\)', assignee_text)
            if match:
                return match.group(1)
        assignee_orig = soup.find('dd', {'itemprop': 'assigneeOriginal'})
        if assignee_orig:
            text = assignee_orig.get_text(strip=True)
            match = re.search(r'[\w\s]+,\s\w{2,}(?:\s\w+)?$', text)
            if match:
                return match.group(0)
        return None

    def extract_full_text(self, soup):
        """Extract full description text from patent page."""
        description_section = soup.find('section', {'itemprop': 'description'})
        if description_section:
            return description_section.get_text(separator='\n', strip=True)
        return None

def fetch_patents(keyword, ipc_codes=None, limit=10, fetch_full_text=False):
    """Fetch patents matching keyword and IPC codes, with detailed scraping."""
    scraper = ExtendedScraper(return_abstract=True)
    search_params = build_search_params(keyword, ipc_codes)
    page = 0
    patent_numbers = []

    # Collect patent numbers from search results
    while len(patent_numbers) < limit:
        if page > 0:
            search_params["page"] = page
        else:
            search_params.pop("page", None)
        json_data = fetch_patents_data(search_params)
        page_patents = extract_patent_numbers_from_json(json_data)
        if not page_patents:
            break
        patent_numbers.extend(page_patents[:limit - len(patent_numbers)])
        if len(page_patents) < 10:
            break
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
            jurisdiction = pn.split('-')[0] if '-' in pn else pn[:2]
            
            # Parse international patent family
            forward_cites = json.loads(parsed.get('forward_cite_no_family', '[]')) + json.loads(parsed.get('forward_cite_yes_family', '[]'))
            backward_cites = json.loads(parsed.get('backward_cite_no_family', '[]')) + json.loads(parsed.get('backward_cite_yes_family', '[]'))
            intl_family = list(set([cite['patent_number'] for cite in forward_cites + backward_cites if cite['patent_number'] != pn]))
            intl_family_str = ", ".join(intl_family) if intl_family else None
            
            # Calculate citation count
            citation_count = len(forward_cites)
            
            data = {
                "patent_number": pn,
                "title": parsed.get('title', ''),
                "abstract": parsed.get('abstract_text', ''),
                "publication_date": parsed.get('pub_date', ''),
                "filing_date": parsed.get('priority_date', ''),  # Use priority_date as filing_date
                "inventors": ", ".join([inv['inventor_name'] for inv in json.loads(parsed['inventor_name'])] if parsed.get('inventor_name') else []),
                "assignees": ", ".join([ass['assignee_name'] for ass in json.loads(parsed['assignee_name_current'])] if parsed.get('assignee_name_current') else []),
                "ipc_codes": ", ".join(parsed.get('ipc_code', [])),
                "assignee_location": parsed.get('assignee_location', ''),
                "full_text": parsed.get('full_text', ''),
                "jurisdiction": jurisdiction,
                "international_family": intl_family_str,
                "citation_count": citation_count
            }
            patents.append(data)

    ipc_filter = ",".join(ipc_codes) if ipc_codes else "None"
    return patents, ipc_filter
