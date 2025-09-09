"""
Report generator for creating Excel and HTML reports.
"""
import pandas as pd
from typing import List, Dict
import os
from datetime import datetime
from jinja2 import Template
from comparison_engine import ComparisonResult
from config import Config

class ReportGenerator:
    """Generator for Excel and HTML reports."""
    
    def __init__(self):
        self.output_dir = Config.REPORT_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_excel_report(self, results: List[ComparisonResult]) -> str:
        """
        Generate Excel report from comparison results.
        
        Args:
            results: List of ComparisonResult objects
            
        Returns:
            Path to the generated Excel file
        """
        # Summary data
        summary_data = []
        detailed_data = []
        
        for result in results:
            summary_data.append({
                'Query': result.query,
                'Old Results Count': result.old_results_count,
                'New Results Count': result.new_results_count,
                'True Positives': result.true_positives,
                'False Positives': result.false_positives,
                'False Negatives': result.false_negatives,
                'Similarity Score': f"{result.similarity_score:.2%}",
                'Status': 'Good Match' if result.similarity_score >= 0.8 else 'Needs Review'
            })
            
            # Detailed comparison data
            for match in result.common_matches:
                detailed_data.append({
                    'Query': result.query,
                    'Match Type': 'Relevant Result',
                    'Entity Name': match['new']['name'],
                    'Entity Type': match['new']['type'],
                    'Score': match['new']['score'],
                    'Relevance': 'High'
                })
            
            for irrelevant in result.only_in_new:
                detailed_data.append({
                    'Query': result.query,
                    'Match Type': 'Irrelevant Result (False Positive)',
                    'Entity Name': irrelevant['name'],
                    'Entity Type': irrelevant['type'],
                    'Score': irrelevant['score'],
                    'Relevance': 'Low'
                })
        
        # Create DataFrames
        summary_df = pd.DataFrame(summary_data)
        detailed_df = pd.DataFrame(detailed_data)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"search_comparison_report_{timestamp}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
        # Write to Excel with multiple sheets
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            detailed_df.to_excel(writer, sheet_name='Detailed Comparison', index=False)
            
            # Auto-adjust column widths
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return filepath
    
    def generate_html_report(self, results: List[ComparisonResult]) -> str:
        """
        Generate HTML report from comparison results.
        
        Args:
            results: List of ComparisonResult objects
            
        Returns:
            Path to the generated HTML file
        """
        # Calculate overall statistics
        total_queries = len(results)
        total_true_positives = sum(r.true_positives for r in results)
        total_false_positives = sum(r.false_positives for r in results)
        total_false_negatives = sum(r.false_negatives for r in results)
        avg_similarity = sum(r.similarity_score for r in results) / total_queries if total_queries > 0 else 0
        
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>OpenSearch Relevance Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f8f9fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 10px; margin-bottom: 25px; }
        .header h1 { margin: 0; font-size: 28px; }
        .header p { margin: 5px 0; opacity: 0.9; }
        .summary { background-color: #e8f4fd; padding: 20px; border-radius: 10px; margin-bottom: 25px; border-left: 5px solid #2c5aa0; }
        .metric { display: inline-block; margin: 15px 25px; text-align: center; }
        .metric-value { font-size: 28px; font-weight: bold; color: #2c5aa0; }
        .metric-label { font-size: 13px; color: #666; margin-top: 5px; }
        .data-sources { background-color: #fff3cd; padding: 20px; border-radius: 10px; margin-bottom: 25px; border-left: 5px solid #ffc107; }
        .source-box { display: inline-block; width: 45%; margin: 10px 2%; padding: 15px; background: white; border-radius: 8px; vertical-align: top; }
        .source-title { font-weight: bold; color: #495057; margin-bottom: 10px; font-size: 16px; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 25px; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        th, td { border: 1px solid #dee2e6; padding: 12px; text-align: left; }
        th { background-color: #495057; color: white; font-weight: bold; }
        .true-match { background-color: #d4edda; }
        .needs-review { background-color: #f8d7da; }
        .details { margin-top: 30px; }
        .query-section { margin-bottom: 40px; border: 2px solid #dee2e6; padding: 25px; border-radius: 10px; background: white; }
        .query-title { color: #495057; border-bottom: 2px solid #e9ecef; padding-bottom: 10px; margin-bottom: 20px; }
        .results-comparison { display: flex; gap: 20px; margin: 20px 0; }
        .result-column { flex: 1; }
        .result-header { background-color: #6c757d; color: white; padding: 10px; border-radius: 5px 5px 0 0; font-weight: bold; text-align: center; }
        .opensearch-header { background-color: #28a745; }
        .gdc-header { background-color: #dc3545; }
        .result-content { border: 1px solid #dee2e6; border-top: none; padding: 15px; border-radius: 0 0 5px 5px; min-height: 200px; background-color: #f8f9fa; }
        .result-item { background: white; margin: 8px 0; padding: 10px; border-radius: 5px; border-left: 4px solid #007bff; }
        .result-name { font-weight: bold; color: #495057; }
        .result-details { font-size: 12px; color: #6c757d; margin-top: 5px; }
        .match-explanation { background-color: #e7f3ff; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #007bff; }
        .explanation-title { font-weight: bold; color: #0056b3; margin-bottom: 8px; }
        .true-matches { background-color: #d1e7dd; border-left-color: #28a745; }
        .false-positives { background-color: #f8d7da; border-left-color: #dc3545; }
        .false-negatives { background-color: #fff3cd; border-left-color: #ffc107; }
        .no-results { text-align: center; color: #6c757d; font-style: italic; padding: 20px; }
        .stats-box { background: white; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #17a2b8; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenSearch Relevance Analysis Report</h1>
        <p>Generated on: {{ timestamp }}</p>
        <p>Analyzing OpenSearch API result relevance and accuracy</p>
    </div>
    
    <div class="data-sources">
        <h2>Analysis Overview</h2>
        <div class="source-box" style="width: 90%; margin: 10px auto;">
            <div class="source-title">OpenSearch API Analysis</div>
            <p><strong>Purpose:</strong> Test search result relevance and accuracy</p>
            <p><strong>Endpoint:</strong> AWS Lambda API</p>
            <p><strong>Method:</strong> Analyze if search results match the query intent</p>
            <p><strong>Criteria:</strong> True Match = result name contains or closely matches query term</p>
            <p><strong>Example:</strong> Query "infosys" returning "Infosys Limited" = True Match, returning "InfoTech Corp" = False Positive</p>
        </div>
    </div>
    
    <div class="summary">
        <h2>Overall Summary</h2>
        <div class="metric">
            <div class="metric-value">{{ total_queries }}</div>
            <div class="metric-label">Total Queries</div>
        </div>
        <div class="metric">
            <div class="metric-value">{{ total_true_positives }}</div>
            <div class="metric-label">Relevant Results</div>
        </div>
        <div class="metric">
            <div class="metric-value">{{ total_false_positives }}</div>
            <div class="metric-label">Irrelevant Results</div>
        </div>
        <div class="metric">
            <div class="metric-value">{{ "%.1f"|format(avg_similarity * 100) }}%</div>
            <div class="metric-label">Avg Relevance</div>
        </div>
    </div>
    
    <h2>Query Results Summary</h2>
    <table>
        <thead>
            <tr>
                <th>Query</th>
                <th>Total Results</th>
                <th>Relevant Results</th>
                <th>Irrelevant Results</th>
                <th>Relevance %</th>
                <th>Assessment</th>
            </tr>
        </thead>
        <tbody>
            {% for result in results %}
            <tr class="{{ 'true-match' if result.similarity_score >= 0.8 else 'needs-review' }}">
                <td><strong>{{ result.query }}</strong></td>
                <td>{{ result.new_results_count }}</td>
                <td>{{ result.true_positives }}</td>
                <td>{{ result.false_positives }}</td>
                <td>{{ "%.1f"|format(result.similarity_score * 100) }}%</td>
                <td>{{ 'Good Relevance' if result.similarity_score >= 0.8 else 'Needs Review' }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <div class="details">
        <h2>Detailed Query Analysis</h2>
        {% for result in results %}
        <div class="query-section">
            <h3 class="query-title">Query: "{{ result.query }}"</h3>
            
            <div class="stats-box">
                <strong>Results Summary:</strong> 
                OpenSearch returned {{ result.new_results_count }} results for "{{ result.query }}"
                - {{ result.true_positives }} relevant, {{ result.false_positives }} irrelevant
                ({{ "%.1f"|format(result.similarity_score * 100) }}% relevance rate)
            </div>
            
            <div class="results-comparison">
                <div class="result-column">
                    <div class="result-header opensearch-header">Relevant Results (True Matches)</div>
                    <div class="result-content">
                        {% if result.common_matches %}
                            {% for match in result.common_matches %}
                            <div class="result-item">
                                <div class="result-name">{{ match.new.name or 'Unknown Entity' }}</div>
                                <div class="result-details">
                                    Type: {{ match.new.type or 'Unknown' }} | 
                                    Score: {{ match.new.score }}
                                    {% if match.new.raw_data.llm_analysis %}
                                    <br><strong>LLM Analysis:</strong> {{ match.new.raw_data.llm_analysis.explanation }}
                                    <br><em>Confidence: {{ "%.0f"|format(match.new.raw_data.llm_analysis.confidence * 100) }}%</em>
                                    {% else %}
                                    <br><em>Relevant match for "{{ result.query }}"</em>
                                    {% endif %}
                                </div>
                            </div>
                            {% endfor %}
                        {% else %}
                            <div class="no-results">No relevant results found</div>
                        {% endif %}
                    </div>
                </div>
                
                <div class="result-column">
                    <div class="result-header gdc-header">Irrelevant Results (False Positives)</div>
                    <div class="result-content">
                        {% if result.only_in_new %}
                            {% for item in result.only_in_new[:10] %}
                            <div class="result-item">
                                <div class="result-name">{{ item.name or 'Unknown Entity' }}</div>
                                <div class="result-details">
                                    Type: {{ item.type or 'Unknown' }} | 
                                    Score: {{ item.score }}
                                    {% if item.raw_data.llm_analysis %}
                                    <br><strong>LLM Analysis:</strong> {{ item.raw_data.llm_analysis.explanation }}
                                    <br><em>Confidence: {{ "%.0f"|format(item.raw_data.llm_analysis.confidence * 100) }}%</em>
                                    {% else %}
                                    <br><em>Not relevant to "{{ result.query }}"</em>
                                    {% endif %}
                                </div>
                            </div>
                            {% endfor %}
                            {% if result.only_in_new|length > 10 %}
                            <div class="no-results">... and {{ result.only_in_new|length - 10 }} more irrelevant results</div>
                            {% endif %}
                        {% else %}
                            <div class="no-results">No irrelevant results found</div>
                        {% endif %}
                    </div>
                </div>
            </div>
            
            {% if result.true_positives > 0 %}
            <div class="match-explanation true-matches">
                <div class="explanation-title">Relevant Results Analysis</div>
                Found {{ result.true_positives }} relevant results that match the search intent for "{{ result.query }}". These results contain the query term or are closely related to it, indicating good search relevance.
            </div>
            {% endif %}
            
            {% if result.false_positives > 0 %}
            <div class="match-explanation false-positives">
                <div class="explanation-title">Irrelevant Results Analysis</div>
                Found {{ result.false_positives }} irrelevant results that don't match the search intent for "{{ result.query }}". These are false positives that could indicate:
                <ul>
                    <li><strong>Broad Matching:</strong> Search algorithm returning loosely related results</li>
                    <li><strong>Keyword Overlap:</strong> Results sharing some keywords but different context</li>
                    <li><strong>Search Tuning Needed:</strong> Search parameters may need adjustment for better precision</li>
                </ul>
            </div>
            {% endif %}
            
            {% if result.true_positives == 0 %}
            <div class="match-explanation false-negatives">
                <div class="explanation-title">No Relevant Results Found</div>
                OpenSearch returned {{ result.new_results_count }} results but none were relevant to "{{ result.query }}". This could indicate:
                <ul>
                    <li><strong>Search Algorithm Issues:</strong> The search logic may not be optimized for this query type</li>
                    <li><strong>Data Coverage:</strong> The target entity may not exist in the database</li>
                    <li><strong>Query Processing:</strong> The query may need different formatting or parameters</li>
                </ul>
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    
    <div class="summary" style="margin-top: 40px;">
        <h2>Key Insights & Recommendations</h2>
        <div style="text-align: left;">
            <h4>What This Analysis Shows:</h4>
            <ul>
                <li><strong>Search Relevance:</strong> {{ "%.1f"|format(avg_similarity * 100) }}% average relevance rate across all queries</li>
                <li><strong>Result Quality:</strong> {{ total_true_positives }} relevant results out of {{ total_true_positives + total_false_positives }} total results</li>
                <li><strong>Search Precision:</strong> Analysis shows how well OpenSearch matches user intent</li>
            </ul>
            
            <h4>Recommendations:</h4>
            <ul>
                <li><strong>Improve Search Precision:</strong> Tune search parameters to reduce irrelevant results</li>
                <li><strong>Review False Positives:</strong> Analyze irrelevant results to understand search algorithm behavior</li>
                <li><strong>Optimize Query Processing:</strong> Consider query preprocessing for better matching</li>
                <li><strong>Monitor Search Quality:</strong> Regular testing with diverse queries to maintain relevance</li>
            </ul>
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_queries=total_queries,
            total_true_positives=total_true_positives,
            total_false_positives=total_false_positives,
            total_false_negatives=total_false_negatives,
            avg_similarity=avg_similarity,
            results=results
        )
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"search_comparison_report_{timestamp}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
