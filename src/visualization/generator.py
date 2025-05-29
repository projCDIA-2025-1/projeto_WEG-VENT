"""Visualization generation for NER results."""

import os
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict
from textwrap import wrap
from typing import List, Dict, Any
from ..config import ENTITY_STYLES, IMAGES_OUTPUT_DIR
from ..utils import ensure_directory_exists

def wrap_label(label: str, width: int = 20) -> str:
    """Wrap text to fit within node, returning a newline-separated string."""
    return '\n'.join(wrap(label, width))

def create_reaction_graph(entities: List[Dict[str, Any]], output_path: str, patent_number: str) -> str:
    """Create a reaction graph from NER entities and save as image."""
    ensure_directory_exists(os.path.dirname(output_path))
    
    # Group entities by type
    entity_dict = defaultdict(list)
    for entity in entities:
        entity_dict[entity['entity_type']].append(entity['entity_text'])
    
    starting_materials = entity_dict.get("STARTING_MATERIAL", [])
    products = entity_dict.get("REACTION_PRODUCT", [])
    
    if not starting_materials and not products:
        return None
    
    # Create graph
    G = nx.DiGraph()
    wrapped_labels = {}
    
    # Add starting materials
    for sm in starting_materials:
        wrapped_labels[sm] = wrap_label(sm)
        G.add_node(sm, subset=0, color=ENTITY_STYLES.get("STARTING_MATERIAL", "#FFDAB9"))
    
    # Add products
    for prod in products:
        wrapped_labels[prod] = wrap_label(prod)
        G.add_node(prod, subset=1, color=ENTITY_STYLES.get("REACTION_PRODUCT", "#98FB98"))
    
    # Add edges from starting materials to products
    for sm in starting_materials:
        for prod in products:
            G.add_edge(sm, prod, relation="Reaction")
    
    if not G.nodes():
        return None
    
    # Use bipartite layout for better positioning
    pos = nx.bipartite_layout(G, starting_materials, scale=2.0) if starting_materials else nx.spring_layout(G)
    
    # Draw graph
    node_colors = [G.nodes[node]["color"] for node in G.nodes]
    plt.figure(figsize=(12, 10))
    plt.title(f"Reaction Graph: {patent_number}", fontsize=14, pad=20)
    nx.draw(G, pos, with_labels=False, node_color=node_colors, node_size=6000, arrowsize=25)
    
    # Draw wrapped labels
    for node, (x, y) in pos.items():
        plt.text(x, y, wrapped_labels[node], fontsize=10, ha='center', va='center', 
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, "relation")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    
    # Save image
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    return output_path

def create_entity_distribution_chart(all_entities: List[Dict[str, Any]], output_path: str) -> str:
    """Create a bar chart showing entity type distribution."""
    ensure_directory_exists(os.path.dirname(output_path))
    
    # Count entities by type
    entity_counts = defaultdict(int)
    for entity in all_entities:
        entity_counts[entity['entity_type']] += 1
    
    if not entity_counts:
        return None
    
    # Create bar chart
    entity_types = list(entity_counts.keys())
    counts = list(entity_counts.values())
    colors = [ENTITY_STYLES.get(et, "#CCCCCC") for et in entity_types]
    
    plt.figure(figsize=(12, 8))
    bars = plt.bar(entity_types, counts, color=colors)
    plt.title("Entity Type Distribution", fontsize=16)
    plt.xlabel("Entity Type", fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    # Add count labels on bars
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                str(count), ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    return output_path

def generate_visualizations_for_patent(patent_number: str, entities: List[Dict[str, Any]], 
                                     output_dir: str) -> Dict[str, str]:
    """Generate all visualizations for a patent."""
    ensure_directory_exists(output_dir)
    
    visualizations = {}
    
    # Generate reaction graph
    graph_path = os.path.join(output_dir, f"{patent_number}_reaction_graph.png")
    if create_reaction_graph(entities, graph_path, patent_number):
        visualizations['reaction_graph'] = graph_path
    
    return visualizations
