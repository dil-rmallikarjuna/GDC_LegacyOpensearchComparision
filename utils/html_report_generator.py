#!/usr/bin/env python3
"""
HTML Report Generator Utility
Generates styled HTML reports from pandas DataFrames for GDC automation testing
"""

import pandas as pd
from datetime import datetime
import os

class HTMLReportGenerator:
    """Utility class for generating HTML reports from test data"""
    
    def __init__(self):
        """Initialize the HTML report generator"""
        self.status_colors = {
            "present_in_both": "#d4edda",
            "opensearch_only": "#cce5ff", 
            "legacy_only": "#fff3cd"
        }
        
        self.schema_colors = {
            "watch": "#fff3cd",
            "pep": "#d1ecf1", 
            "sanction": "#f8d7da",
            "icij": "#d4edda",
            "mex": "#e2e3e5",
            "rights": "#fce4ec",
            "soe": "#f3e5f5",
            "col": "#fff8e1",
            "media": "#e0f2f1"
        }
    
    def generate_unified_comparison_report(self, df, filename):
        """
        Generate HTML report from DataFrame for unified comparison
        """
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unified OpenSearch vs Legacy GDC Comparison Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2.5em; font-weight: 300; }}
        .header p {{ margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9; }}
        .summary {{ padding: 20px 30px; background-color: #f8f9fa; border-bottom: 1px solid #dee2e6; }}
        .summary h2 {{ margin: 0 0 15px 0; color: #495057; font-size: 1.5em; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .stat-card {{ background: white; padding: 15px; border-radius: 6px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #6c757d; font-size: 0.9em; margin-top: 5px; }}
        .table-container {{ padding: 30px; overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.9em; }}
        th {{ background-color: #495057; color: white; padding: 12px 8px; text-align: left; font-weight: 600; position: sticky; top: 0; z-index: 10; }}
        td {{ padding: 10px 8px; border-bottom: 1px solid #dee2e6; vertical-align: top; }}
        tr:nth-child(even) {{ background-color: #f8f9fa; }}
        tr:hover {{ background-color: #e3f2fd; }}
        .type-person {{ background-color: #e8f5e8; color: #2e7d32; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; font-weight: 500; }}
        .type-entity {{ background-color: #e3f2fd; color: #1565c0; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; font-weight: 500; }}
        .schema-badge {{ display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; font-weight: 500; margin: 1px; }}
        .schema-watch {{ background-color: #fff3cd; color: #856404; }}
        .schema-pep {{ background-color: #d1ecf1; color: #0c5460; }}
        .schema-sanction {{ background-color: #f8d7da; color: #721c24; }}
        .schema-icij {{ background-color: #d4edda; color: #155724; }}
        .schema-mex {{ background-color: #e2e3e5; color: #383d41; }}
        .schema-rights {{ background-color: #fce4ec; color: #c2185b; }}
        .schema-soe {{ background-color: #f3e5f5; color: #7b1fa2; }}
        .schema-col {{ background-color: #fff8e1; color: #f57f17; }}
        .schema-media {{ background-color: #e0f2f1; color: #00695c; }}
        .empty-cell {{ color: #6c757d; font-style: italic; }}
        .status-badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 600; text-align: center; min-width: 80px; }}
        .status-both {{ background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .status-opensearch-only {{ background-color: #cce5ff; color: #004085; border: 1px solid #b3d7ff; }}
        .status-legacy-only {{ background-color: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
        .search-term-section {{ margin-bottom: 40px; }}
        .search-term-header {{ background: #f8f9fa; padding: 20px; border-radius: 8px 8px 0 0; border-bottom: 2px solid #dee2e6; }}
        .search-term-header h3 {{ margin: 0 0 10px 0; color: #495057; font-size: 1.5em; font-weight: 600; }}
        .term-summary {{ display: flex; flex-wrap: wrap; gap: 15px; }}
        .summary-item {{ background: white; padding: 8px 12px; border-radius: 4px; font-size: 0.9em; font-weight: 500; color: #495057; border: 1px solid #dee2e6; }}
        .search-term-table {{ width: 100%; border-collapse: collapse; font-size: 0.9em; }}
        .search-term-table th {{ background-color: #495057; color: white; padding: 12px 8px; text-align: left; font-weight: 600; }}
        .search-term-table td {{ padding: 10px 8px; border-bottom: 1px solid #dee2e6; vertical-align: top; }}
        .search-term-table tr:nth-child(even) {{ background-color: #f8f9fa; }}
        .search-term-table tr:hover {{ background-color: #e3f2fd; }}
        .footer {{ padding: 20px 30px; background-color: #f8f9fa; text-align: center; color: #6c757d; border-top: 1px solid #dee2e6; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Unified OpenSearch vs Legacy GDC Comparison</h1>
            <p>Comprehensive Analysis Report - Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="table-container">
            <h2>Search Results by Term</h2>
"""
            
            # Generate separate tables for each search term
            for search_term in df['Search Term'].unique():
                term_df = df[df['Search Term'] == search_term].copy()
                
                # Calculate statistics for this term
                total_records = len(term_df)
                opensearch_records = len(term_df[term_df['OpenSearch ID'] != ''])
                legacy_records = len(term_df[term_df['Legacy ID'] != ''])
                matched_records = len(term_df[(term_df['OpenSearch ID'] != '') & (term_df['Legacy ID'] != '')])
                opensearch_only = len(term_df[(term_df['OpenSearch ID'] != '') & (term_df['Legacy ID'] == '')])
                legacy_only = len(term_df[(term_df['OpenSearch ID'] == '') & (term_df['Legacy ID'] != '')])
                
                html_content += f"""
            <div class="search-term-section">
                <div class="search-term-header">
                    <h3>{search_term}</h3>
                    <div class="term-summary">
                        <span class="summary-item">Total: {total_records}</span>
                        <span class="summary-item">OpenSearch: {opensearch_records}</span>
                        <span class="summary-item">Legacy: {legacy_records}</span>
                        <span class="summary-item">Matched: {matched_records}</span>
                        <span class="summary-item">OpenSearch Only: {opensearch_only}</span>
                        <span class="summary-item">Legacy Only: {legacy_only}</span>
                    </div>
                </div>
                <table class="search-term-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Type</th>
                            <th>Status</th>
                            <th>OpenSearch Name</th>
                            <th>OpenSearch ID</th>
                            <th>OpenSearch Schema</th>
                            <th>Legacy Name</th>
                            <th>Legacy ID</th>
                            <th>Legacy Schema</th>
                        </tr>
                    </thead>
                    <tbody>
"""
                
                # Add rows for this search term
                row_number = 1
                for _, row in term_df.iterrows():
                    type_class = "type-person" if row['Type'] == 'Person' else "type-entity"
                    opensearch_schema_class = f"schema-{row['OpenSearch Schema'].lower()}" if row['OpenSearch Schema'] else ""
                    legacy_schema_class = f"schema-{row['Legacy Schema'].lower()}" if row['Legacy Schema'] else ""
                    
                    # Convert to string and check for "Not Present" text
                    opensearch_name = str(row['OpenSearch Name']) if row['OpenSearch Name'] else ''
                    opensearch_id = str(row['OpenSearch ID']) if row['OpenSearch ID'] else ''
                    opensearch_schema = str(row['OpenSearch Schema']) if row['OpenSearch Schema'] else ''
                    legacy_name = str(row['Legacy Name']) if row['Legacy Name'] else ''
                    legacy_id = str(row['Legacy ID']) if row['Legacy ID'] else ''
                    legacy_schema = str(row['Legacy Schema']) if row['Legacy Schema'] else ''
                    
                    # Check if values indicate presence (not empty and not "Not Present")
                    has_opensearch = opensearch_id and 'Not Present' not in opensearch_id
                    has_legacy = legacy_id and 'Not Present' not in legacy_id
                    
                    if has_opensearch and has_legacy:
                        status = "Present in Both"
                        status_class = "status-both"
                    elif has_opensearch and not has_legacy:
                        status = "OpenSearch Only"
                        status_class = "status-opensearch-only"
                    elif not has_opensearch and has_legacy:
                        status = "Legacy Only"
                        status_class = "status-legacy-only"
                    else:
                        status = "Not Present"
                        status_class = "status-legacy-only"
                    
                    # Keep existing "Not Present" text or set to "Not Present" if empty
                    opensearch_name = opensearch_name if opensearch_name else 'Not Present'
                    opensearch_id = opensearch_id if opensearch_id else 'Not Present'
                    opensearch_schema = opensearch_schema if opensearch_schema else 'Not Present'
                    legacy_name = legacy_name if legacy_name else 'Not Present'
                    legacy_id = legacy_id if legacy_id else 'Not Present'
                    legacy_schema = legacy_schema if legacy_schema else 'Not Present'
                    
                    html_content += f"""
                        <tr>
                            <td><strong>{row_number}</strong></td>
                            <td><span class="{type_class}">{row['Type']}</span></td>
                            <td><span class="status-badge {status_class}">{status}</span></td>
                            <td>{opensearch_name}</td>
                            <td>{opensearch_id}</td>
                            <td><span class="schema-badge {opensearch_schema_class}">{opensearch_schema}</span></td>
                            <td>{legacy_name}</td>
                            <td>{legacy_id}</td>
                            <td><span class="schema-badge {legacy_schema_class}">{legacy_schema}</span></td>
                        </tr>
"""
                    row_number += 1
                
                html_content += """
                    </tbody>
                </table>
            </div>
"""
            
            html_content += """
        </div>
        
        <div class="footer">
            <p>Generated by GDC Automation Excel-Driven Regression Testing Framework</p>
            <p>This report compares OpenSearch API results with Legacy GDC system data</p>
        </div>
    </div>
</body>
</html>
"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            print(f"✅ HTML report generated: {filename}")
                
        except Exception as e:
            print(f"❌ Error generating HTML report: {e}")
            raise
    
    def generate_entity_report(self, entity_name, entity_type, comparison_data, filename):
        """
        Generate HTML report for individual entity comparison
        """
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Entity Comparison Report - {entity_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2em; }}
        .content {{ padding: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #495057; border-bottom: 2px solid #dee2e6; padding-bottom: 10px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; }}
        .stat-number {{ font-size: 1.5em; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #6c757d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Entity Comparison Report</h1>
            <p>{entity_name} ({entity_type})</p>
        </div>
        <div class="content">
            <div class="section">
                <h2>Summary</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{comparison_data.get('common_records', 0)}</div>
                        <div class="stat-label">Common Records</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{comparison_data.get('new_in_opensearch', 0)}</div>
                        <div class="stat-label">New in OpenSearch</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{comparison_data.get('missing_from_opensearch', 0)}</div>
                        <div class="stat-label">Missing from OpenSearch</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        except Exception as e:
            print(f"Error generating entity HTML report: {e}")
            raise
