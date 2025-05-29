"""Configuration settings for the patent analysis system."""

import os

# Database settings
DATABASE_PATH = "patents.db"

# NER Model settings
NER_MODEL_PATH = "./ner_results/saved_model"
ENTITY_TYPES = [
    "STARTING_MATERIAL", "REAGENT_CATALYST", "REACTION_PRODUCT", "SOLVENT", 
    "OTHER_COMPOUND", "TIME", "TEMPERATURE", "YIELD_PERCENT", "YIELD_OTHER", 
    "EXAMPLE_LABEL"
]

# Visualization settings
ENTITY_STYLES = {
    "STARTING_MATERIAL": "#FFDAB9",
    "REAGENT_CATALYST": "#FFE4B5", 
    "REACTION_PRODUCT": "#98FB98",
    "SOLVENT": "#E6E6FA",
    "OTHER_COMPOUND": "#ADD8E6",
    "TIME": "#B0E0E6",
    "TEMPERATURE": "#FFB6C1",
    "YIELD_PERCENT": "#D8BFD8",
    "YIELD_OTHER": "#F0E68C",
    "EXAMPLE_LABEL": "#FFFF99"
}

# Scraping settings
DEFAULT_PATENT_LIMIT = 10
SCRAPING_DELAY = 2  # seconds between requests

# Report settings
REPORTS_OUTPUT_DIR = "reports_output"
IMAGES_OUTPUT_DIR = "images"
