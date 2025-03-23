import requests
import urllib.parse
import time

def build_search_params(keyword, ipc_codes=None, page=0):
    """Build search parameters for the request."""
    params = {"q": keyword}
    if ipc_codes:
        params["classification"] = "+OR+".join(ipc_codes)
    if page > 0:
        params["page"] = page
    return params

def fetch_patents_data(search_params):
    xhr_url = "https://patents.google.com/xhr/query"
    query_string = urllib.parse.urlencode(search_params)
    params = {"url": query_string, "exp": "", "tags": ""}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(xhr_url, params=params, headers=headers)
    response.raise_for_status()
    json_data = response.json()
    print(f"Response type: {type(json_data)}")
    print(f"Response preview: {str(json_data)[:200]}")
    return json_data

def extract_patent_data_from_json(json_data):
    """Extract patent data from the JSON response."""
    patents = []
    if isinstance(json_data, dict) and "results" in json_data:
        results = json_data["results"]

        if isinstance(results, dict) and "cluster" in results:
            for result_item in results["cluster"]:
                if "result" in result_item and isinstance(result_item["result"], list):
                    for item in result_item["result"]:
                        if "patent" in item:
                            patent = item["patent"]
                            data = {
                                "patent_number": patent.get("publication_number"),
                                "title": patent.get("title"),
                                "abstract": patent.get("snippet"),
                                "publication_date": patent.get("publication_date"),
                                "filing_date": patent.get("priority_date"),  # Often the filing date
                                "inventors": ", ".join(patent.get("inventor", [])) if isinstance(patent.get("inventor"), list) else "",
                                "assignees": ", ".join(patent.get("assignee", [])) if isinstance(patent.get("assignee"), list) else "",
                                "ipc_codes": ", ".join(patent.get("classification", [])) if isinstance(patent.get("classification"), list) else "",
                            }
                            patents.append(data)
    
    return patents

def fetch_patents(keyword, ipc_codes=None, limit=10):
    """Fetch patents matching the keyword and IPC codes."""
    patents = []
    page = 0
    search_params = build_search_params(keyword, ipc_codes)
    while len(patents) < limit:
        search_params["page"] = page
        json_data = fetch_patents_data(search_params)
        page_patents = extract_patent_data_from_json(json_data)
        if not page_patents:
            break

        patents.extend(page_patents[:limit - len(patents)])
        if len(page_patents) < 10:
            break
        page += 1
        time.sleep(1) # avoid overload
    ipc_filter = ",".join(ipc_codes) if ipc_codes else "None"
    return patents, ipc_filter
