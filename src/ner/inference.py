"""Mock NER inference functionality."""

from typing import List, Dict, Any

def run_ner_inference(text: str, model_path: str = None) -> List[Dict[str, Any]]:
    """
    Mock NER inference that returns fixed example entities.
    
    Args:
        text (str): Input text for entity recognition (ignored in mock)
        model_path (str): Path to the saved model (ignored in mock)
    
    Returns:
        list: List of dictionaries containing mock entity data
    """
    # Return mock entities for demonstration
    mock_entities = [
        {
            "text": "graphene oxide",
            "label": "STARTING_MATERIAL",
            "start": 10,
            "end": 24
        },
        {
            "text": "sodium hydroxide",
            "label": "REAGENT_CATALYST", 
            "start": 30,
            "end": 46
        },
        {
            "text": "reduced graphene oxide",
            "label": "REACTION_PRODUCT",
            "start": 60,
            "end": 82
        },
        {
            "text": "water",
            "label": "SOLVENT",
            "start": 90,
            "end": 95
        },
        {
            "text": "ethanol",
            "label": "SOLVENT", 
            "start": 100,
            "end": 107
        },
        {
            "text": "2 hours",
            "label": "TIME",
            "start": 120,
            "end": 127
        },
        {
            "text": "80°C",
            "label": "TEMPERATURE",
            "start": 135,
            "end": 139
        },
        {
            "text": "95%",
            "label": "YIELD_PERCENT",
            "start": 150,
            "end": 153
        },
        {
            "text": "Example 1",
            "label": "EXAMPLE_LABEL",
            "start": 0,
            "end": 9
        }
    ]
    
    return mock_entities

def process_patent_abstract(patent_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process a patent's abstract with mock NER."""
    abstract = patent_data.get('abstract', '')
    if not abstract:
        return []
    
    return run_ner_inference(abstract)
