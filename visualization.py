import html
import os
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from textwrap import wrap

ENTITY_STYLES = {
    "EXAMPLE_LABEL": "background-color: #FFFF99;",
    "OTHER_COMPOUND": "background-color: #ADD8E6;",
    "REACTION_PRODUCT": "background-color: #98FB98;",
    "STARTING_MATERIAL": "background-color: #FFDAB9;",
    "SOLVENT": "background-color: #E6E6FA;",
    "TEMPERATURE": "background-color: #FFB6C1;",
    "TIME": "background-color: #B0E0E6;",
    "YIELD_PERCENT": "background-color: #D8BFD8;",
    "YIELD_OTHER": "background-color: #F0E68C;"
}

def wrap_label(label, width=20):
    """Wrap text to fit within node, returning a newline-separated string."""
    return '\n'.join(wrap(label, width))

def generate_html(text, annotations, output_file, base_name):
    # Parse annotations
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
    
    # Start HTML content
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
    img { max-width: 100%; height: auto; }
    """
    html_content += "</style>\n</head>\n<body>\n"
    
    # Example label (title)
    if "EXAMPLE_LABEL" in entity_dict:
        html_content += f"<h1>Example {', '.join(entity_dict['EXAMPLE_LABEL'])}</h1>\n"
    
    # Reaction flow section
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
    
    # Yield information
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
    
    # Other compounds
    other_entities = entity_dict["OTHER_COMPOUND"]
    if other_entities:
        html_content += '<h2>Other Compounds</h2>\n<ul>\n'
        for entity in other_entities:
            html_content += f"<li>{html.escape(entity)}</li>\n"
        html_content += '</ul>\n'
    
    # Annotated full text
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
    
    # Generate and add reaction graph image
    if starting_entities or product_entities:
        # Create graph
        G = nx.DiGraph()
        wrapped_labels = {}
        for sm in starting_entities:
            wrapped_labels[sm] = wrap_label(sm)
            G.add_node(sm, subset=0, color="#FFDAB9")
        for prod in product_entities:
            wrapped_labels[prod] = wrap_label(prod)
            G.add_node(prod, subset=1, color="#98FB98")
        for sm in starting_entities:
            for prod in product_entities:
                G.add_edge(sm, prod, relation="Reaction")
        
        # Use bipartite layout for better positioning
        pos = nx.bipartite_layout(G, starting_entities, scale=2.0)
        
        # Draw graph
        node_colors = [G.nodes[node]["color"] for node in G.nodes]
        plt.figure(figsize=(12, 10))
        plt.title("Reaction Graph: Starting Materials to Products", fontsize=14, pad=20)
        nx.draw(G, pos, with_labels=False, node_color=node_colors, node_size=6000, arrowsize=25)
        
        # Draw wrapped labels
        for node, (x, y) in pos.items():
            plt.text(x, y, wrapped_labels[node], fontsize=10, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
        
        edge_labels = nx.get_edge_attributes(G, "relation")
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
        
        # Save image
        image_filename = f"{base_name}_graph.png"
        image_path = os.path.join(os.path.dirname(output_file), image_filename)
        plt.savefig(image_path, bbox_inches='tight')
        plt.close()
        
        # Add to HTML
        html_content += f'<h2>Reaction Graph</h2>\n<img src="{image_filename}" alt="Reaction Graph">\n'
    
    # Close HTML
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
            
            generate_html(text, annotations, html_path, base_name)
            print(f"Generated visualization: {html_path}")

if __name__ == "__main__":
    sample_dir = "./chemu_sample/ner"
    process_directory(sample_dir)
