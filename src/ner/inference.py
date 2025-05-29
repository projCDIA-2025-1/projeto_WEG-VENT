"""NER inference functionality."""

import torch
import nltk
from typing import List, Dict, Any
from .model import load_ner_model, get_id2label_mapping
from ..config import NER_MODEL_PATH

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def run_ner_inference(text: str, model_path: str = NER_MODEL_PATH) -> List[Dict[str, Any]]:
    """
    Run NER inference on input text using the trained model.
    
    Args:
        text (str): Input text for entity recognition
        model_path (str): Path to the saved model and tokenizer
    
    Returns:
        list: List of dictionaries containing entity text, label, start, and end positions
    """
    model, tokenizer = load_ner_model(model_path)
    id2label = get_id2label_mapping()
    
    sentences = nltk.sent_tokenize(text)
    all_entities = []
    
    for sentence in sentences:
        encoding = tokenizer(
            sentence,
            return_offsets_mapping=True,
            add_special_tokens=True,
            max_length=128,
            truncation=True,
            return_tensors="pt"
        )
        
        input_ids = encoding["input_ids"]
        offset_mapping = encoding["offset_mapping"][0]
        
        with torch.no_grad():
            outputs = model(input_ids)
            logits = outputs.logits
        
        predictions = torch.argmax(logits, dim=2)[0].cpu().numpy()
        
        entities = []
        current_entity = None
        current_label = None
        
        for idx, (pred_id, (start, end)) in enumerate(zip(predictions, offset_mapping)):
            label = id2label[pred_id]
            if start == end or label == "O":
                if current_entity:
                    entities.append(current_entity)
                    current_entity = None
                    current_label = None
                continue
            
            label_type = label[2:] if label.startswith(("B-", "I-")) else label
            
            if label.startswith("B-"):
                if current_entity:
                    entities.append(current_entity)
                current_entity = {
                    "text": sentence[start:end],
                    "label": label_type,
                    "start": start,
                    "end": end
                }
                current_label = label_type
            elif label.startswith("I-") and current_entity and label_type == current_label:
                current_entity["text"] += " " + sentence[start:end]
                current_entity["end"] = end
            else:
                if current_entity:
                    entities.append(current_entity)
                    current_entity = None
                    current_label = None
        
        if current_entity:
            entities.append(current_entity)
        
        sentence_start = text.find(sentence)
        for entity in entities:
            entity["start"] += sentence_start
            entity["end"] += sentence_start
            all_entities.append(entity)
    
    return all_entities

def process_patent_abstract(patent_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process a patent's abstract with NER."""
    abstract = patent_data.get('abstract', '')
    if not abstract:
        return []
    
    return run_ner_inference(abstract)
