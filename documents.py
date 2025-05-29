import html
from typing import List, Dict
from datetime import datetime

class Entities:
    def __init__(self, entities_dict: Dict[str, List[str]]):
        self.entities = entities_dict

class Patent:
    def __init__(self,
                 title: str,
                 published_date: str,
                 keywords: List[str],
                 assignees: List[str],
                 inventors: List[str],
                 jurisdiction: str,
                 international_family: List[str],
                 citation_count: int,
                 abstract: str,
                 full_text: bool,
                 entities: Entities):
        self.title = title
        self.published_date = published_date
        self.keywords = keywords
        self.assignees = assignees
        self.inventors = inventors
        self.jurisdiction = jurisdiction
        self.international_family = international_family
        self.citation_count = citation_count
        self.abstract = abstract
        self.full_text = full_text
        self.entities = entities

    def get_countries(self) -> List[str]:
        """Extract unique country codes from title and international family."""
        countries = set()
        if self.title:
            countries.add(self.title[:2])
        for patent in self.international_family:
            if patent:
                countries.add(patent[:2])
        return sorted(list(countries))

def generate_patent_html(patent: Patent) -> str:
    """Generate HTML content for a single patent."""
    html_content = f"<h2>{html.escape(patent.title)}</h2>\n"
    html_content += '<div class="patent-info">\n'
    html_content += f"<p><strong>Published:</strong> {html.escape(patent.published_date)}</p>\n"
    html_content += f"<p><strong>Citation Count:</strong> {patent.citation_count}</p>\n"
    countries = patent.get_countries()
    html_content += f"<p><strong>Countries:</strong> {', '.join(countries)}</p>\n"
    html_content += '</div>\n'
    
    html_content += '<details>\n'
    html_content += '<summary>More Information</summary>\n'
    html_content += '<div class="more-info">\n'
    
    if patent.entities.entities:
        html_content += "<h3>Entities Recognized</h3>\n<ul>\n"
        for entity_type, values in patent.entities.entities.items():
            escaped_values = [html.escape(v) for v in values]
            formatted_type = entity_type.replace('_', ' ').title()
            html_content += f"<li><strong>{html.escape(formatted_type)}:</strong> {', '.join(escaped_values)}</li>\n"
        html_content += "</ul>\n"
    
    if patent.keywords:
        html_content += "<h3>Keywords</h3>\n"
        html_content += f"<p>{', '.join([html.escape(k) for k in patent.keywords])}</p>\n"
    
    if patent.abstract:
        html_content += "<h3>Abstract</h3>\n"
        html_content += f"<p>{html.escape(patent.abstract)}</p>\n"
    
    html_content += '</div>\n'
    html_content += '</details>\n'
    return html_content

def generate_report(patents: List[Patent]) -> str:
    """Generate the full HTML report for a list of patents."""
    current_date = datetime.now().strftime("%Y-%m-%d")
    html_content = "<!DOCTYPE html>\n<html>\n<head>\n"
    html_content += f"<title>Patents Report - {current_date}</title>\n"
    html_content += "<style>\n"
    html_content += """
    body { font-family: Arial, sans-serif; margin: 20px; }
    h1 { color: navy; }
    h2 { color: darkgreen; margin-top: 20px; }
    .patent-info { margin-bottom: 10px; }
    .more-info { margin-left: 20px; }
    ul { list-style-type: none; padding-left: 0; }
    li { margin-bottom: 5px; }
    """
    html_content += "</style>\n</head>\n<body>\n"
    html_content += f"<h1>Patents Report - {current_date}</h1>\n"
    
    for patent in patents:
        html_content += generate_patent_html(patent)
    
    html_content += "</body>\n</html>"
    return html_content

if __name__ == "__main__":
    # Sample patent data for testing
    sample_entities = Entities({
        "OTHER_COMPOUND": ["DMSO"],
        "TIME": ["16 h"],
        "REACTION_PRODUCT": ["title compound", "3-Isobutyl-5-methyl-1-(oxetan-2-ylmethyl)-6-[(2-oxoimidazolidin-1-yl)methyl]thieno[2,3-d]pyrimidine-2,4(1H,3H)-dione (racemate)"],
        "YIELD_PERCENT": ["42%"],
        "STARTING_MATERIAL": ["CDI", "compound from Example 243A"],
        "TEMPERATURE": ["RT"],
        "SOLVENT": ["dioxane"],
        "EXAMPLE_LABEL": ["194"],
        "YIELD_OTHER": ["383 mg"]
    })
    
    sample_patent = Patent(
        title="US10526204B2",
        published_date="2019-03-14",
        keywords=["graphene"],
        assignees=["Global Graphene Group Inc"],
        inventors=["Aruna Zhamu", "Bor Z. Jang"],
        jurisdiction="US",
        international_family=["US11121398B2", "US11742475B2", "CN117964366B", "KR102341186B1"],
        citation_count=41,
        abstract="Provided is a method of producing isolated graphene sheets directly from a carbon/graphite precursor. The method comprises: (a) providing a mass of aromatic molecules wherein the aromatic molecuasdihaskdhaskjdhksajhdkjashdkjashdkjashdkjashdkjsahkjdhaskjdhsakjdhsakjhdjksahdkjsahdkjashdkjsahdjkashdkjashdkjash",
        full_text=False,
        entities=sample_entities
    )
    
    patents = [sample_patent]
    
    # Generate and save the report
    report_html = generate_report(patents)
    with open("patents_report.html", "w", encoding="utf-8") as f:
        f.write(report_html)
    print("Patent report generated as 'patents_report.html'")


