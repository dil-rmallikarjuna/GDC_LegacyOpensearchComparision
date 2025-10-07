# Utils Module - Reusable Report Generation

This module contains reusable components for GDC automation testing, specifically focused on report generation.

## Components

### 1. ReportGenerator (`report_generator.py`)

A reusable class for generating Excel and HTML reports from comparison data.

#### Features:
- **Excel Reports**: Creates separate sheets for each entity (like `ExactMatches.xlsx`)
- **HTML Reports**: Generates styled HTML reports with status indicators
- **Flexible**: Can be used by any test case that provides comparison data
- **Modular**: Report generation logic is separate from test logic

#### Usage:

```python
from utils.report_generator import ReportGenerator

# Initialize
report_gen = ReportGenerator("/path/to/results")

# Generate unified comparison report
excel_file, html_file = report_gen.generate_unified_comparison_report(
    comparison_data,
    "my_test_report"
)

# Generate entity-specific report
entity_excel, entity_html = report_gen.generate_entity_specific_report(
    "Entity Name",
    entity_comparison_data,
    "entity_report"
)
```

#### Comparison Data Format:

```python
comparison_data = [
    {
        'search_term': 'Entity Name',
        'entity_type': 'E',  # or 'P' for Person
        'opensearch_results': {
            'watch': [{'ID': '123', 'Full_Name': 'Name', 'recid': 1}],
            'pep': [{'ID': '456', 'Full_Name': 'Name2', 'recid': 2}]
        },
        'legacy_results': {
            'watch': [{'ID': '123', 'Full_Name': 'Name', 'recid': 1}],
            'pep': [{'ID': '456', 'Full_Name': 'Name2', 'recid': 2}]
        }
    }
]
```

### 2. HTMLReportGenerator (`html_report_generator.py`)

Handles HTML report generation with styling and status indicators.

### 3. Example Usage (`example_usage.py`)

Shows how to use the ReportGenerator in any test case.

## Benefits

1. **Separation of Concerns**: Test logic is separate from report generation
2. **Reusability**: Any test case can use the same report generator
3. **Maintainability**: Report changes don't affect test cases
4. **Consistency**: All reports use the same format and styling
5. **Flexibility**: Can generate different types of reports (unified, entity-specific, summary)

## Integration with Test Cases

To use in any test case:

1. Import the ReportGenerator
2. Initialize with results directory
3. Collect comparison data in the required format
4. Call the appropriate report generation method

The test case only needs to focus on:
- Loading test data
- Running tests
- Collecting results
- Calling the report generator

Report generation logic is completely abstracted away!
