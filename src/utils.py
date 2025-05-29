"""Utility functions for the patent analysis system."""

import os
import re
from datetime import datetime
from typing import List, Dict, Any

def ensure_directory_exists(directory: str) -> None:
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_country_code(patent_number: str) -> str:
    """Extract country code from patent number."""
    if not patent_number:
        return ""
    # Handle formats like US10526204B2, EP1234567A1, etc.
    match = re.match(r'^([A-Z]{2})', patent_number)
    return match.group(1) if match else patent_number[:2]

def format_date(date_str: str) -> str:
    """Format date string to consistent format."""
    if not date_str:
        return ""
    try:
        # Try to parse and reformat date
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return date_str

def generate_filename(base_name: str, extension: str = "html") -> str:
    """Generate filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"
