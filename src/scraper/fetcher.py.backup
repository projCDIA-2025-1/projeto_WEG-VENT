"""Google Patents fetching functionality."""

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
