"""HTML templates for patent reports."""

import html
from typing import List, Dict, Any
from collections import Counter
from ..database.operations import get_citation_and_region_stats

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
        .search-container {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .search-box {{
            width: 100%;
            max-width: 500px;
            padding: 12px 20px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 25px;
            outline: none;
            transition: border-color 0.3s;
        }}
        .search-box:focus {{
            border-color: #007bff;
        }}
        .search-info {{
            margin-top: 10px;
            color: #666;
            font-size: 14px;
        }}
        .search-results {{
            margin-top: 15px;
            color: #007bff;
            font-weight: bold;
        }}
        .search-navigation {{
            margin-top: 10px;
            color: #666;
            font-size: 13px;
        }}
        .nav-button {{
            background-color: #007bff;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            margin: 0 5px;
            font-size: 12px;
        }}
        .nav-button:hover {{
            background-color: #0056b3;
        }}
        .nav-button:disabled {{
            background-color: #ccc;
            cursor: not-allowed;
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
        .stat-card.citation {{
            border-left-color: #28a745;
        }}
        .stat-card.region {{
            border-left-color: #ffc107;
        }}
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-number.citation {{
            color: #28a745;
        }}
        .stat-number.region {{
            color: #ffc107;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        .detailed-stats {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }}
        .stat-section {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }}
        .stat-section h4 {{
            margin-top: 0;
            color: #007bff;
        }}
        .stat-section ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .patent-card {{
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-bottom: 25px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: opacity 0.3s;
        }}
        .patent-card.hidden {{
            display: none;
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
        .patent-meta {{
            font-size: 12px;
            opacity: 0.8;
            margin-top: 5px;
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
        .highlight {{
            background-color: #ffff00;
            padding: 2px 4px;
            border-radius: 3px;
        }}
        .highlight.current {{
            background-color: #ff6b6b;
            color: white;
            font-weight: bold;
            box-shadow: 0 0 5px rgba(255, 107, 107, 0.5);
        }}
    </style>
    <script>
        let currentHighlightIndex = -1;
        let allHighlights = [];

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

        function searchPatents() {{
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const patentCards = document.querySelectorAll('.patent-card');
            const searchResults = document.getElementById('searchResults');
            const searchNavigation = document.getElementById('searchNavigation');
            let visibleCount = 0;
            let totalMatches = 0;

            // Clear previous highlights and reset navigation
            clearHighlights();
            currentHighlightIndex = -1;
            allHighlights = [];

            patentCards.forEach(card => {{
                const searchableText = card.textContent.toLowerCase();
                const hasMatch = searchableText.includes(searchTerm);
                
                if (searchTerm === '' || hasMatch) {{
                    card.classList.remove('hidden');
                    visibleCount++;
                    
                    if (searchTerm !== '' && hasMatch) {{
                        // Highlight matches and expand card
                        highlightText(card, searchTerm);
                        const content = card.querySelector('.patent-content');
                        const icon = card.querySelector('.expand-icon');
                        if (content && !content.classList.contains('expanded')) {{
                            content.classList.add('expanded');
                            if (icon) icon.style.transform = 'rotate(180deg)';
                        }}
                        totalMatches++;
                    }}
                }} else {{
                    card.classList.add('hidden');
                }}
            }});

            // Update search results
            if (searchTerm === '') {{
                searchResults.textContent = '';
                searchNavigation.style.display = 'none';
            }} else {{
                searchResults.textContent = `Found ${{totalMatches}} patents matching "${{searchTerm}}"`;
                
                // Update navigation
                allHighlights = Array.from(document.querySelectorAll('.highlight'));
                if (allHighlights.length > 0) {{
                    searchNavigation.style.display = 'block';
                    updateNavigationInfo();
                    // Automatically go to first occurrence
                    if (allHighlights.length > 0) {{
                        currentHighlightIndex = 0;
                        jumpToHighlight(0);
                    }}
                }} else {{
                    searchNavigation.style.display = 'none';
                }}
            }}
        }}

        function highlightText(element, searchTerm) {{
            const walker = document.createTreeWalker(
                element,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );

            const textNodes = [];
            let node;
            while (node = walker.nextNode()) {{
                textNodes.push(node);
            }}

            textNodes.forEach(textNode => {{
                const text = textNode.textContent;
                const lowerText = text.toLowerCase();
                const lowerSearchTerm = searchTerm.toLowerCase();
                
                if (lowerText.includes(lowerSearchTerm)) {{
                    const regex = new RegExp(`(${{searchTerm.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&')}})`, 'gi');
                    const highlightedText = text.replace(regex, '<span class="highlight">$1</span>');
                    
                    const wrapper = document.createElement('div');
                    wrapper.innerHTML = highlightedText;
                    
                    const parent = textNode.parentNode;
                    while (wrapper.firstChild) {{
                        parent.insertBefore(wrapper.firstChild, textNode);
                    }}
                    parent.removeChild(textNode);
                }}
            }});
        }}

        function clearHighlights() {{
            const highlights = document.querySelectorAll('.highlight');
            highlights.forEach(highlight => {{
                const parent = highlight.parentNode;
                parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
                parent.normalize();
            }});
        }}

        function jumpToHighlight(index) {{
            if (allHighlights.length === 0) return;
            
            // Remove current class from all highlights
            allHighlights.forEach(h => h.classList.remove('current'));
            
            // Add current class to the target highlight
            if (index >= 0 && index < allHighlights.length) {{
                const targetHighlight = allHighlights[index];
                targetHighlight.classList.add('current');
                
                // Scroll to the highlight with some offset
                const rect = targetHighlight.getBoundingClientRect();
                const offset = window.innerHeight / 3; // Scroll to top third of screen
                window.scrollTo({{
                    top: window.pageYOffset + rect.top - offset,
                    behavior: 'smooth'
                }});
                
                currentHighlightIndex = index;
                updateNavigationInfo();
            }}
        }}

        function nextHighlight() {{
            if (allHighlights.length === 0) return;
            const nextIndex = (currentHighlightIndex + 1) % allHighlights.length;
            jumpToHighlight(nextIndex);
        }}

        function prevHighlight() {{
            if (allHighlights.length === 0) return;
            const prevIndex = currentHighlightIndex <= 0 ? allHighlights.length - 1 : currentHighlightIndex - 1;
            jumpToHighlight(prevIndex);
        }}

        function updateNavigationInfo() {{
            const navInfo = document.getElementById('navInfo');
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');
            
            if (allHighlights.length > 0) {{
                navInfo.textContent = `${{currentHighlightIndex + 1}} of ${{allHighlights.length}} occurrences`;
                prevBtn.disabled = false;
                nextBtn.disabled = false;
            }} else {{
                navInfo.textContent = '';
                prevBtn.disabled = true;
                nextBtn.disabled = true;
            }}
        }}

        // Add event listeners
        document.addEventListener('DOMContentLoaded', function() {{
            const searchBox = document.getElementById('searchBox');
            if (searchBox) {{
                searchBox.addEventListener('input', searchPatents);
                searchBox.addEventListener('keyup', function(event) {{
                    if (event.key === 'Escape') {{
                        searchBox.value = '';
                        searchPatents();
                    }} else if (event.key === ' ' && searchBox.value.trim() !== '') {{
                        event.preventDefault();
                        nextHighlight();
                    }}
                }});
            }}

            // Global keyboard shortcuts
            document.addEventListener('keydown', function(event) {{
                // Only trigger if search box has content and is not focused
                const searchBox = document.getElementById('searchBox');
                if (searchBox && searchBox.value.trim() !== '' && document.activeElement !== searchBox) {{
                    if (event.key === ' ') {{
                        event.preventDefault();
                        nextHighlight();
                    }} else if (event.key === 'ArrowUp' && event.shiftKey) {{
                        event.preventDefault();
                        prevHighlight();
                    }} else if (event.key === 'ArrowDown' && event.shiftKey) {{
                        event.preventDefault();
                        nextHighlight();
                    }}
                }}
            }});
        }});
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
        
        <div class="search-container">
            <input type="text" id="searchBox" class="search-box" placeholder="Search through all patent content..." />
            <div class="search-info">
                Search through titles, abstracts, inventors, assignees, and all other patent content<br>
                <strong>Navigation:</strong> Press Space to jump to next occurrence | Shift+↑/↓ for prev/next
            </div>
            <div id="searchResults" class="search-results"></div>
            <div id="searchNavigation" class="search-navigation" style="display: none;">
                <button id="prevBtn" class="nav-button" onclick="prevHighlight()">← Previous</button>
                <span id="navInfo"></span>
                <button id="nextBtn" class="nav-button" onclick="nextHighlight()">Next →</button>
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
    
    # Format citation and jurisdiction info
    citation_count = safe_get('citation_count', 0)
    jurisdiction = safe_get('jurisdiction', 'Unknown')
    
    return f'''
    <div class="patent-card">
        <div class="patent-header" onclick="togglePatent(this)">
            <div>
                <div class="patent-title">{html.escape(safe_get('title'))}</div>
                <div class="patent-number">Patent: {html.escape(safe_get('patent_number'))}</div>
                <div class="patent-meta">Citations: {citation_count} | Region: {jurisdiction}</div>
            </div>
            <span class="expand-icon">▼</span>
        </div>
        <div class="patent-content">
            <div class="patent-info">
                <div class="info-section">
                    <h4>Patent Information</h4>
                    <p><strong>Publication Date:</strong> {html.escape(safe_get('publication_date'))}</p>
                    <p><strong>Filing Date:</strong> {html.escape(safe_get('filing_date'))}</p>
                    <p><strong>Assignees:</strong> {html.escape(safe_get('assignees'))}</p>
                    <p><strong>Inventors:</strong> {html.escape(safe_get('inventors'))}</p>
                    <p><strong>IPC Codes:</strong> {html.escape(safe_get('ipc_codes'))}</p>
                    <p><strong>Jurisdiction:</strong> {html.escape(safe_get('jurisdiction'))}</p>
                </div>
                <div class="info-section">
                    <h4>Analysis Results</h4>
                    <p><strong>Entities Found:</strong> {len(entities)}</p>
                    <p><strong>Entity Types:</strong> {len(entities_by_type)}</p>
                    <p><strong>Citation Count:</strong> {citation_count}</p>
                    <p><strong>Assignee Location:</strong> {html.escape(safe_get('assignee_location'))}</p>
                    <p><strong>Fetch Date:</strong> {html.escape(safe_get('fetch_date'))}</p>
                </div>
            </div>
            
            <div class="abstract">
                <h4>Abstract</h4>
                <p>{html.escape(safe_get('abstract'))}</p>
            </div>
            
            <div class="AI-Resume">
                <h4>AI Summary</h4>
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
    
    # Get citation and region statistics
    citation_region_stats = get_citation_and_region_stats(patents)
    
    # Generate entity type stats
    entity_stats_html = ""
    if top_entities:
        entity_stats_html = "<h4>Top Entity Types</h4><ul>"
        for entity_type, count in top_entities:
            entity_stats_html += f"<li>{entity_type.replace('_', ' ').title()}: {count}</li>"
        entity_stats_html += "</ul>"
    
    # Generate region distribution
    region_stats_html = ""
    if citation_region_stats.get('region_distribution'):
        region_stats_html = "<h4>Regional Distribution</h4><ul>"
        for region, count in citation_region_stats['region_distribution']:
            region_stats_html += f"<li>{region}: {count} patents</li>"
        region_stats_html += "</ul>"
    
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
            <div class="stat-card citation">
                <div class="stat-number citation">{citation_region_stats.get('total_citations', 0)}</div>
                <div class="stat-label">Total Citations</div>
            </div>
            <div class="stat-card citation">
                <div class="stat-number citation">{citation_region_stats.get('avg_citations', 0)}</div>
                <div class="stat-label">Avg Citations</div>
            </div>
            <div class="stat-card region">
                <div class="stat-number region">{citation_region_stats.get('unique_regions', 0)}</div>
                <div class="stat-label">Unique Regions</div>
            </div>
            <div class="stat-card region">
                <div class="stat-number region">{citation_region_stats.get('max_citations', 0)}</div>
                <div class="stat-label">Max Citations</div>
            </div>
        </div>
        
        <div class="detailed-stats">
            <div class="stat-section">
                {entity_stats_html}
            </div>
            <div class="stat-section">
                {region_stats_html}
                {f'<p><strong>Regions:</strong> {", ".join(citation_region_stats.get("regions_list", []))}</p>' if citation_region_stats.get("regions_list") else ""}
            </div>
        </div>
    </div>
    '''
