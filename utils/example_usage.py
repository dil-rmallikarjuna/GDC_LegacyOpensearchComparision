#!/usr/bin/env python3
"""
Example usage of the reusable ReportGenerator
This shows how any test case can use the report generator
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.report_generator import ReportGenerator


def example_usage():
    """
    Example of how to use the ReportGenerator in any test case
    """
    
    # Initialize the report generator
    results_dir = "/Users/rmallikarjuna/Documents/GDC automation excel driven/results"
    report_gen = ReportGenerator(results_dir)
    
    # Example comparison data (this would come from your test case)
    comparison_data = [
        {
            'search_term': 'Example Entity 1',
            'entity_type': 'E',
            'opensearch_results': {
                'watch': [
                    {'ID': '12345', 'Full_Name': 'Example Entity 1', 'recid': 1}
                ],
                'pep': [
                    {'ID': '67890', 'Full_Name': 'Example Person 1', 'recid': 2}
                ]
            },
            'legacy_results': {
                'watch': [
                    {'ID': '12345', 'Full_Name': 'Example Entity 1', 'recid': 1}
                ],
                'pep': [
                    {'ID': '67890', 'Full_Name': 'Example Person 1', 'recid': 2}
                ]
            }
        },
        {
            'search_term': 'Example Entity 2',
            'entity_type': 'P',
            'opensearch_results': {
                'sanction': [
                    {'ID': '11111', 'Full_Name': 'Example Person 2', 'recid': 3}
                ]
            },
            'legacy_results': {
                'sanction': [
                    {'ID': '11111', 'Full_Name': 'Example Person 2', 'recid': 3}
                ]
            }
        }
    ]
    
    # Generate unified comparison report
    excel_file, html_file = report_gen.generate_unified_comparison_report(
        comparison_data,
        "example_comparison"
    )
    
    print(f"Generated reports:")
    print(f"  Excel: {excel_file}")
    print(f"  HTML: {html_file}")
    
    # Generate entity-specific report
    entity_data = comparison_data[0]  # First entity
    entity_excel, entity_html = report_gen.generate_entity_specific_report(
        entity_data['search_term'],
        entity_data,
        "entity_specific"
    )
    
    print(f"\nEntity-specific reports:")
    print(f"  Excel: {entity_excel}")
    print(f"  HTML: {entity_html}")


if __name__ == "__main__":
    example_usage()
