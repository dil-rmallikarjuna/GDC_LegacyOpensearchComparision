"""
Reusable Report Generation Module
Handles Excel and HTML report generation for GDC automation testing
"""

import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from .html_report_generator import HTMLReportGenerator


class ReportGenerator:
    """
    Reusable report generator for GDC automation testing
    Can be used by any test case that provides comparison data
    """
    
    def __init__(self, results_directory: str):
        """
        Initialize the report generator
        
        Args:
            results_directory: Path to directory where reports will be saved
        """
        self.results_directory = results_directory
        self.html_generator = HTMLReportGenerator()
        
        # Ensure results directory exists
        os.makedirs(results_directory, exist_ok=True)
    
    def generate_unified_comparison_report(self, 
                                         comparison_data: List[Dict[str, Any]], 
                                         report_name: str = "unified_comparison",
                                         create_excel_sheets: bool = True,
                                         create_html_report: bool = True) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate unified comparison reports (Excel and HTML) with the specified format:
        Test Key, Search Term, Type, OpenSearch Name, OpenSearch ID, OpenSearch Schema, Legacy Name, Legacy ID, Legacy Schema
        
        Args:
            comparison_data: List of comparison data dictionaries
            report_name: Base name for the report files
            create_excel_sheets: Whether to create Excel report with separate sheets
            create_html_report: Whether to create HTML report
            
        Returns:
            Tuple of (excel_filename, html_filename) or (None, None) if no data
        """
        if not comparison_data:
            print("❌ No comparison data available to generate report")
            return None, None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create unified comparison data
        unified_data = []
        
        for comparison_item in comparison_data:
            search_term = comparison_item['search_term']
            entity_type = comparison_item['entity_type']
            test_key = search_term  # Remove _E and _P suffixes if needed
            type_label = "Person" if entity_type == "P" else "Entity"
            
            # Get OpenSearch results
            opensearch_results = comparison_item.get('opensearch_results', {})
            # Get Legacy GDC results
            legacy_results = comparison_item.get('legacy_results', {})
            
            # Process each source
            all_sources = set(opensearch_results.keys()) | set(legacy_results.keys())
            
            for source in all_sources:
                opensearch_records = opensearch_results.get(source, [])
                legacy_records = legacy_results.get(source, [])
                
                # Create lookup for matching records
                legacy_by_id = {record.get("ID", ""): record for record in legacy_records}
                
                # Process OpenSearch records
                for opensearch_record in opensearch_records:
                    opensearch_id = opensearch_record.get("ID", "")
                    opensearch_name = opensearch_record.get("Full_Name", "") or opensearch_record.get("Entity_Name", "")
                    opensearch_schema = source.upper()
                    
                    # Find matching legacy record
                    legacy_record = legacy_by_id.get(opensearch_id)
                    if legacy_record:
                        legacy_name = legacy_record.get("Full_Name", "") or legacy_record.get("Entity_Name", "")
                        legacy_id = legacy_record.get("ID", "")
                        legacy_schema = source.upper()
                    else:
                        legacy_name = ""
                        legacy_id = ""
                        legacy_schema = ""
                    
                    unified_data.append({
                        "Test Key": test_key,
                        "Search Term": search_term,
                        "Type": type_label,
                        "OpenSearch Name": opensearch_name,
                        "OpenSearch ID": opensearch_id,
                        "OpenSearch Schema": opensearch_schema,
                        "Legacy Name": legacy_name,
                        "Legacy ID": legacy_id,
                        "Legacy Schema": legacy_schema
                    })
                
                # Process legacy-only records (not found in OpenSearch)
                opensearch_ids = {record.get("ID", "") for record in opensearch_records}
                for legacy_record in legacy_records:
                    legacy_id = legacy_record.get("ID", "")
                    if legacy_id not in opensearch_ids:
                        legacy_name = legacy_record.get("Full_Name", "") or legacy_record.get("Entity_Name", "")
                        legacy_schema = source.upper()
                        
                        unified_data.append({
                            "Test Key": test_key,
                            "Search Term": search_term,
                            "Type": type_label,
                            "OpenSearch Name": "",
                            "OpenSearch ID": "",
                            "OpenSearch Schema": "",
                            "Legacy Name": legacy_name,
                            "Legacy ID": legacy_id,
                            "Legacy Schema": legacy_schema
                        })
        
        # Create DataFrame
        df = pd.DataFrame(unified_data)
        
        # Sort by Test Key, then by OpenSearch Schema, then by OpenSearch ID
        df = df.sort_values(['Test Key', 'OpenSearch Schema', 'OpenSearch ID'])
        
        excel_filename = None
        html_filename = None
        
        # Generate Excel report with separate sheets for each entity
        if create_excel_sheets:
            excel_filename = os.path.join(self.results_directory, f"{report_name}_{timestamp}.xlsx")
            
            # Group data by Test Key (entity name) and create separate sheets
            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                for test_key in df['Test Key'].unique():
                    entity_df = df[df['Test Key'] == test_key].copy()
                    
                    # Remove 'Test Key' column since it's now the sheet name
                    entity_df = entity_df.drop(columns=['Test Key'])
                    
                    # Truncate sheet name to 31 characters (Excel limit)
                    sheet_name = test_key[:31] if len(test_key) > 31 else test_key
                    
                    # Write to sheet
                    entity_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Generate HTML report
        if create_html_report:
            html_filename = os.path.join(self.results_directory, f"{report_name}_{timestamp}.html")
            self.html_generator.generate_unified_comparison_report(df, html_filename)
        
        # Print summary
        self._print_report_summary(df, excel_filename, html_filename, unified_data)
        
        return excel_filename, html_filename
    
    def _print_report_summary(self, df: pd.DataFrame, excel_filename: Optional[str], 
                            html_filename: Optional[str], unified_data: List[Dict]) -> None:
        """Print summary statistics for the generated reports"""
        
        if excel_filename:
            print(f"\n✅ Excel report generated: {excel_filename}")
        if html_filename:
            print(f"✅ HTML report generated: {html_filename}")
        
        print(f"📊 Total comparison records: {len(unified_data)}")
        
        # Print summary statistics
        total_opensearch_records = len([r for r in unified_data if r['OpenSearch ID']])
        total_legacy_records = len([r for r in unified_data if r['Legacy ID']])
        matched_records = len([r for r in unified_data if r['OpenSearch ID'] and r['Legacy ID']])
        
        print(f"📈 Summary Statistics:")
        print(f"  OpenSearch records: {total_opensearch_records}")
        print(f"  Legacy GDC records: {total_legacy_records}")
        print(f"  Matched records: {matched_records}")
        print(f"  OpenSearch-only records: {total_opensearch_records - matched_records}")
        print(f"  Legacy-only records: {total_legacy_records - matched_records}")
    
    def generate_entity_specific_report(self, 
                                      entity_name: str,
                                      comparison_data: Dict[str, Any],
                                      report_name: str = "entity_comparison") -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a report for a specific entity
        
        Args:
            entity_name: Name of the entity
            comparison_data: Comparison data for the entity
            report_name: Base name for the report files
            
        Returns:
            Tuple of (excel_filename, html_filename)
        """
        return self.generate_unified_comparison_report(
            [comparison_data], 
            f"{report_name}_{entity_name.replace(' ', '_').lower()}"
        )
    
    def generate_summary_report(self, 
                            all_comparison_data: List[Dict[str, Any]],
                            report_name: str = "summary_comparison") -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a summary report across all entities
        
        Args:
            all_comparison_data: List of all comparison data
            report_name: Base name for the report files
            
        Returns:
            Tuple of (excel_filename, html_filename)
        """
        return self.generate_unified_comparison_report(
            all_comparison_data, 
            report_name,
            create_excel_sheets=True,
            create_html_report=True
        )
