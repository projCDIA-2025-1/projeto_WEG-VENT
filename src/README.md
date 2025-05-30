# Patent Analysis System

## Project Structure

```
src/
├── __init__.py
├── main.py                 # Main entry point
├── config.py              # Configuration settings
├── utils.py               # Utility functions
├── scraper/               # Patent scraping functionality
│   ├── __init__.py
│   ├── fetcher.py         # Google Patents API interaction
│   └── patent_scraper.py  # Main scraping logic
├── ner/                   # Named Entity Recognition
│   ├── __init__.py
│   ├── model.py           # Model definitions and loading
│   ├── inference.py       # NER inference on patent text
│   └── train.py           # Model training (optional)
├── database/              # Database operations
│   ├── __init__.py
│   ├── models.py          # Database schema/models
│   └── operations.py      # CRUD operations
├── visualization/         # Chart and graph generation
│   ├── __init__.py
│   ├── generator.py       # Main visualization logic
│   └── charts.py          # Specific chart types
└── reports/               # HTML report generation
    ├── __init__.py
    ├── generator.py       # Report generation logic
    └── templates.py       # HTML templates
```

## Workflow

1. **Input**: Keywords for patent search
2. **Scraping**: Fetch patents from Google Patents (check DB first)
3. **NER**: Run inference on patent abstracts
4. **Storage**: Store results in database
5. **Visualization**: Generate charts/graphs from NER results
6. **Reporting**: Create HTML report with expandable sections and images

## Ways to Use

### Generate HTML Report
To generate the HTML report:
```bash
python3 -m src.main report
```

### Get Database Statistics
To get database information, such as keywords, number of patents scraped for each keyword, and number of entities:
```bash
python3 -m src.main stats
```

### Fetch Patents (Web Scraping)
To perform web scraping for patents:
```bash
python3 -m src.main fetch [keywords] [arguments]
```
**Arguments:**
*   `keywords`: A keyword to search for (e.g., "graphene"). This is a required positional argument.
*   `--limit <number>`: Maximum number of patents to scrape.
*   `--ipc <IPC_code>`: A desired IPC (International Patent Classification) to be scraped.
*   `--full-text`: A boolean flag. If present, scrapes the entire text of the patent. If absent, only the abstract is saved.

**Example:**
```bash
python3 -m src.main fetch "carbon nanotubes" --limit 100 --ipc C01B32/15
```

### Fetch and Report
To perform both fetching and report generation in one command (requires the same arguments as `fetch`, unless full-text, process only uses abstract):
```bash
python3 -m src.main process [keywords] [arguments]
```
**Example:**
```bash
python3 -m src.main process "renewable energy" --limit 50
```