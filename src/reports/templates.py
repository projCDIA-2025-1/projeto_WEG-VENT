"""HTML templates for patent reports."""

import html
from typing import List, Dict, Any
from collections import Counter

def get_base_template() -> str:
    """Get the base HTML template for patent reports."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Patent Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #007bff;
        }}
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .header .meta {{
            color: #666;
            font-size: 14px;
        }}
        .summary {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .summary h2 {{
            color: #007bff;
            margin-top: 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        .patent-card {{
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-bottom: 25px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .patent-header {{
            background-color: #007bff;
            color: white;
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .patent-header:hover {{
            background-color: #0056b3;
        }}
        .patent-title {{
            font-size: 18px;
            font-weight: bold;
            margin: 0;
        }}
        .patent-number {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .expand-icon {{
            font-size: 20px;
            transition: transform 0.3s;
        }}
        .patent-content {{
            display: none;
            padding: 20px;
        }}
        .patent-content.expanded {{
            display: block;
        }}
        .patent-info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .info-section {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
        }}
        .info-section h4 {{
            margin-top: 0;
            color: #007bff;
        }}
        .abstract {{
            background-color: #fff;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 20px 0;
        }}
        .AI-Resume {{
            background-color: #fff;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 20px 0;
        }}
        .entities-section {{
            margin-top: 20px;
        }}
        .entity {{
            display: inline-block;
            padding: 4px 8px;
            margin: 2px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }}
        .visualizations {{
            margin-top: 20px;
        }}
        .visualization {{
            margin: 15px 0;
            text-align: center;
        }}
        .visualization img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .entity-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }}
        .entity-group {{
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 6px;
        }}
        .entity-group h5 {{
            margin: 0 0 8px 0;
            color: #007bff;
            font-size: 14px;
        }}
        .entity-group .entity {{
            font-size: 11px;
        }}
    </style>
    <script>
        function togglePatent(element) {{
            const content = element.nextElementSibling;
            const icon = element.querySelector('.expand-icon');
            
            if (content.classList.contains('expanded')) {{
                content.classList.remove('expanded');
                icon.style.transform = 'rotate(0deg)';
            }} else {{
                content.classList.add('expanded');
                icon.style.transform = 'rotate(180deg)';
            }}
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Patent Analysis Report</h1>
            <div class="meta">
                Generated on {date} | Keywords: "{keywords}"
            </div>
        </div>
        
        {summary_stats}
        
        <div class="patents-section">
            <h2>Patent Details</h2>
            {patents_content}
        </div>
    </div>
</body>
</html>
"""

def format_patent_card(patent: Dict[str, Any], entities: List[Dict[str, Any]], 
                      visualizations: Dict[str, str] = None) -> str:
    """Format a single patent card with entities and visualizations."""
    if visualizations is None:
        visualizations = {}
    print(patent)
    # Safe get with default values
    def safe_get(key, default="Not specified"):
        value = patent.get(key)
        return value if value is not None else default
    
    # Format entities by type
    entities_by_type = {}
    for entity in entities:
        entity_type = entity.get('entity_type', 'UNKNOWN')
        if entity_type not in entities_by_type:
            entities_by_type[entity_type] = []
        entities_by_type[entity_type].append(entity)
    
    # Generate entity HTML
    entities_html = ""
    if entities_by_type:
        entities_html = '<div class="entity-list">'
        for entity_type, type_entities in entities_by_type.items():
            entities_html += f'''
            <div class="entity-group">
                <h5>{entity_type.replace('_', ' ').title()}</h5>
                <div>
            '''
            for entity in type_entities:
                entity_text = entity.get('entity_text', '')
                entities_html += f'<span class="entity" style="background-color: #e9ecef;">{html.escape(entity_text)}</span>'
            entities_html += '</div></div>'
        entities_html += '</div>'
    else:
        entities_html = '<p>No entities found in abstract.</p>'
    
    # Generate visualizations HTML
    viz_html = ""
    if visualizations:
        viz_html = '<div class="visualizations"><h4>Entity Visualizations</h4>'
        for viz_name, viz_path in visualizations.items():
            viz_html += f'''
            <div class="visualization">
                <h5>{viz_name.replace('_', ' ').title()}</h5>
                <img src="{viz_path}" alt="{viz_name}">
            </div>
            '''
        viz_html += '</div>'
    
    return f'''
    <div class="patent-card">
        <div class="patent-header" onclick="togglePatent(this)">
            <div>
                <div class="patent-title">{html.escape(safe_get('title'))}</div>
                <div class="patent-number">Patent: {html.escape(safe_get('patent_number'))}</div>
            </div>
            <span class="expand-icon">▼</span>
        </div>
        <div class="patent-content">
            <div class="patent-info">
                <div class="info-section">
                    <h4>Patent Information</h4>
                    <p><strong>Publication Date:</strong> {html.escape(safe_get('publication_date'))}</p>
                    <p><strong>Assignee:</strong> {html.escape(safe_get('assignee'))}</p>
                    <p><strong>Inventor:</strong> {html.escape(safe_get('inventor'))}</p>
                    <p><strong>IPC Codes:</strong> {html.escape(safe_get('ipc_codes'))}</p>
                </div>
                <div class="info-section">
                    <h4>Analysis Results</h4>
                    <p><strong>Entities Found:</strong> {len(entities)}</p>
                    <p><strong>Entity Types:</strong> {len(entities_by_type)}</p>
                    <p><strong>Fetch Date:</strong> {html.escape(safe_get('fetch_date'))}</p>
                </div>
            </div>
            
            <div class="abstract">
                <h4>Abstract</h4>
                <p>{html.escape(safe_get('abstract'))}</p>
            </div>
            
            <div class="AI-Resume">
                <h4>AI resume</h4>
                <p>{html.escape(safe_get('ai_summary'))}</p>
            </div>
            <div class="entities-section">
                <h4>Named Entities</h4>
                {entities_html}
            </div>
            
            {viz_html}
        </div>
    </div>
    '''

def format_summary_stats(patents: List[Dict[str, Any]], all_entities: List[Dict[str, Any]]) -> str:
    """Format summary statistics section."""
    # Count entities by type
    entity_counts = Counter()
    for entity in all_entities:
        entity_type = entity.get('entity_type', 'UNKNOWN')
        entity_counts[entity_type] += 1
    
    # Get top entity types
    top_entities = entity_counts.most_common(5)
    
    # Generate entity type stats
    entity_stats_html = ""
    if top_entities:
        entity_stats_html = "<h4>Top Entity Types</h4><ul>"
        for entity_type, count in top_entities:
            entity_stats_html += f"<li>{entity_type.replace('_', ' ').title()}: {count}</li>"
        entity_stats_html += "</ul>"
    
    return f'''
    <div class="summary">
        <h2>Summary Statistics</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{len(patents)}</div>
                <div class="stat-label">Total Patents</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(all_entities)}</div>
                <div class="stat-label">Total Entities</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(entity_counts)}</div>
                <div class="stat-label">Entity Types</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len([p for p in patents if p.get('ner_results')])}</div>
                <div class="stat-label">Patents with Entities</div>
            </div>
        </div>
        {entity_stats_html}
    </div>
    '''
