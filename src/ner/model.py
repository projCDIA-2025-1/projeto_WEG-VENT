"""NER model loading and management."""

import os
import torch
from transformers import BertTokenizerFast, BertForTokenClassification
from ..config import NER_MODEL_PATH, ENTITY_TYPES

def load_ner_model(model_path: str = NER_MODEL_PATH):
    """Load the trained NER model and tokenizer."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"NER model not found at {model_path}")
    
    tokenizer = BertTokenizerFast.from_pretrained(model_path)
    model = BertForTokenClassification.from_pretrained(model_path)
    model.eval()
    
    return model, tokenizer

def get_label_list():
    """Get the label list for NER model."""
    label_list = ["O"] + [f"B-{et}" for et in ENTITY_TYPES] + [f"I-{et}" for et in ENTITY_TYPES]
    return label_list

def get_id2label_mapping():
    """Get ID to label mapping."""
    label_list = get_label_list()
    return {i: label for i, label in enumerate(label_list)}
