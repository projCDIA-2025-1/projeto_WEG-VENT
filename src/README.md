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
