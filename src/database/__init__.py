"""Database module for patent storage and retrieval."""

from .models import create_database, get_database_info
from .operations import (
    insert_patent, insert_ner_results, get_patents, 
    get_ner_results, get_patents_with_ner, get_database_stats
)

__all__ = [
    'create_database', 'get_database_info', 'insert_patent', 
    'insert_ner_results', 'get_patents', 'get_ner_results', 
    'get_patents_with_ner', 'get_database_stats'
]
