"""Mock NER model - no actual model loading needed."""

from ..config import ENTITY_TYPES

def load_ner_model(model_path: str = None):
    """Mock model loading - returns None since we're using mock inference."""
    return None, None

def get_label_list():
    """Get the label list for NER model."""
    label_list = ["O"] + [f"B-{et}" for et in ENTITY_TYPES] + [f"I-{et}" for et in ENTITY_TYPES]
    return label_list

def get_id2label_mapping():
    """Get ID to label mapping."""
    label_list = get_label_list()
    return {i: label for i, label in enumerate(label_list)}
