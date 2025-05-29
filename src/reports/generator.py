"""Report generation functionality."""

import os
from typing import List, Dict, Any
from datetime import datetime
from .templates import get_base_template, format_patent_card, format_summary_stats
from ..config import REPORTS_OUTPUT_DIR, IMAGES_OUTPUT_DIR
from ..utils import ensure_directory_exists, generate_filename
from ..visualization import generate_visualizations_for_patent

def generate_patent_report(patents_with_entities: List[Dict[str, Any]], 
                          keywords: str, output_dir: str = None) -> str:
    """Generate a comprehensive HTML report for patents with NER results."""
    if output_dir is None:
        output_dir = REPORTS_OUTPUT_DIR
    
    ensure_directory_exists(output_dir)
    
    images_dir = os.path.join(output_dir, IMAGES_OUTPUT_DIR)
    ensure_directory_exists(images_dir)
    
    all_entities = []
    patents_content = ""
    
    for patent_data in patents_with_entities:
        patent = patent_data
        entities = patent_data.get('ner_results', [])
        all_entities.extend(entities)
        
        visualizations = {}
        if entities:
            visualizations = generate_visualizations_for_patent(
                patent['patent_number'], entities, images_dir
            )
        
        patents_content += format_patent_card(patent, entities, visualizations)
    
    summary_stats = format_summary_stats(patents_with_entities, all_entities)
    
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    template = get_base_template()
    
    report_html = template.format(
        date=current_date,
        keywords=keywords,
        summary_stats=summary_stats,
        patents_content=patents_content
    )
    
    report_filename = generate_filename("patents_report", "html")
    report_path = os.path.join(output_dir, report_filename)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_html)
    
    print(f"Report generated: {report_path}")
    return report_path
