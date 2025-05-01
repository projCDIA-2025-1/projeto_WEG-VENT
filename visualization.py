import html
import os
from collections import defaultdict

ENTITY_STYLES = {
    "EXAMPLE_LABEL": "background-color: #FFFF99;",  # Light yellow
    "OTHER_COMPOUND": "background-color: #ADD8E6;",  # Light blue
    "REACTION_PRODUCT": "background-color: #98FB98;",  # Pale green
    "STARTING_MATERIAL": "background-color: #FFDAB9;",  # Peach
    "SOLVENT": "background-color: #E6E6FA;",  # Lavender
    "TEMPERATURE": "background-color: #FFB6C1;",  # Light pink
    "TIME": "background-color: #B0E0E6;",  # Powder blue
    "YIELD_PERCENT": "background-color: #D8BFD8;",  # Thistle
    "YIELD_OTHER": "background-color: #F0E68C;"  # Khaki
}

def generate_html(text, annotations, output_file):
    ann_list = []
    for line in annotations.splitlines():
        if line.startswith("T"):
            parts = line.split()
            entity_id = parts[0]
            entity_type = parts[1]
            start = int(parts[2])
            end = int(parts[3])
            ann_list.append((start, end, entity_type))
    
    ann_list.sort(key=lambda x: x[0])
    
    entity_dict = defaultdict(list)
    for start, end, etype in ann_list:
        entity_dict[etype].append(text[start:end])
    
    html_content = "<!DOCTYPE html>\n<html>\n<head>\n<style>\n"
    for entity_type, style in ENTITY_STYLES.items():
        html_content += f".entity_{entity_type.lower()} {{ {style} padding: 2px; }}\n"

    html_content += """
    body { font-family: Arial, sans-serif; }
    h1 { color: navy; }
    h2 { color: darkgreen; }
    ul { list-style-type: none; }
    li { margin-bottom: 5px; }
    .reaction-flow { display: flex; align-items: center; }
    .arrow { font-size: 24px; margin: 0 20px; }
    pre { white-space: pre-wrap; }
    """
    html_content += "</style>\n</head>\n<body>\n"
    
    if "EXAMPLE_LABEL" in entity_dict:
        html_content += f"<h1>Example {', '.join(entity_dict['EXAMPLE_LABEL'])}</h1>\n"
    
    starting_entities = entity_dict["STARTING_MATERIAL"]
    conditions = {
        "Solvent": entity_dict["SOLVENT"],
        "Temperature": entity_dict["TEMPERATURE"],
        "Time": entity_dict["TIME"]
    }
    product_entities = entity_dict["REACTION_PRODUCT"]
    
    if starting_entities or product_entities:
        html_content += '<div class="reaction-flow">\n'
        if starting_entities:
            html_content += '<div class="starting-materials">\n<h2>Starting Materials</h2>\n<ul>\n'
            for entity in starting_entities:
                html_content += f"<li>{html.escape(entity)}</li>\n"
            html_content += '</ul>\n</div>\n'
        if any(conditions.values()):
            html_content += '<span class="arrow">→</span>\n<div class="conditions">\n<h2>Conditions</h2>\n'
            for condition_type, entities in conditions.items():
                if entities:
                    html_content += f"<p>{condition_type}: {', '.join([html.escape(e) for e in entities])}</p>\n"
            html_content += '</div>\n'
        if product_entities:
            html_content += '<span class="arrow">→</span>\n<div class="products">\n<h2>Products</h2>\n<ul>\n'
            for entity in product_entities:
                html_content += f"<li>{html.escape(entity)}</li>\n"
            html_content += '</ul>\n</div>\n'
        html_content += '</div>\n'
    
    yield_info = {
        "Percent": entity_dict["YIELD_PERCENT"],
        "Other": entity_dict["YIELD_OTHER"]
    }
    if yield_info["Percent"] or yield_info["Other"]:
        html_content += '<h2>Yields</h2>\n'
        if yield_info["Percent"]:
            html_content += f"<p>Percent: {', '.join([html.escape(e) for e in yield_info['Percent']])}</p>\n"
        if yield_info["Other"]:
            html_content += f"<p>Other: {', '.join([html.escape(e) for e in yield_info['Other']])}</p>\n"
    
    other_entities = entity_dict["OTHER_COMPOUND"]
    if other_entities:
        html_content += '<h2>Other Compounds</h2>\n<ul>\n'
        for entity in other_entities:
            html_content += f"<li>{html.escape(entity)}</li>\n"
        html_content += '</ul>\n'
    
    html_content += "<h2>Full Text with Annotations</h2>\n<pre>\n"
    current_pos = 0
    annotated_text = ""
    for start, end, entity_type in ann_list:
        if current_pos < start:
            annotated_text += html.escape(text[current_pos:start])
        annotated_text += f"<span class='entity_{entity_type.lower()}'>{html.escape(text[start:end])}</span>"
        current_pos = end
    if current_pos < len(text):
        annotated_text += html.escape(text[current_pos:])
    html_content += annotated_text + "\n</pre>\n"
    
    html_content += "</body>\n</html>"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

def process_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            base_name = filename[:-4]
            txt_path = os.path.join(directory, filename)
            ann_path = os.path.join(directory, base_name + ".ann")
            html_path = os.path.join(directory, base_name + ".html")
            
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read()
            with open(ann_path, "r", encoding="utf-8") as f:
                annotations = f.read()
            
            generate_html(text, annotations, html_path)
            print(f"Generated visualization: {html_path}")

if __name__ == "__main__":
    sample_dir = "./chemu_sample/ner"
    process_directory(sample_dir)
