"""Patent scraping module."""

from .patent_scraper import fetch_patents
from .fetcher import ExtendedScraper

__all__ = ['fetch_patents', 'ExtendedScraper']
