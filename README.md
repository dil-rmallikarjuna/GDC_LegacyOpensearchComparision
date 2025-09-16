# GDC Automation Test

This repository contains automated testing tools for Global Database Compliance (GDC) systems, focusing on OpenSearch entity regression testing.

## Overview

The project provides comprehensive testing capabilities for:
- **OpenSearch Entity Regression Testing**: Compare current OpenSearch results with existing GDC baseline data
- **Multi-language Support**: Handle entities in various languages (Arabic, Chinese, Cyrillic, Hebrew, etc.)
- **Comprehensive Reporting**: Generate Excel and HTML reports with detailed analysis

## Project Structure

```
├── GDC Old System Result.xlsx          # Input data for regression testing
├── testcases/                           # Testing framework
│   ├── consolidated_regression_test.py  # Main consolidated testing framework
│   ├── excel_driven_regression_test.py  # Individual entity testing
│   ├── results/                         # Generated test reports
│   └── requirements.txt                 # Testing dependencies
└── requirements.txt                     # Main dependencies
```

## Features

### OpenSearch Regression Testing
- **Excel-driven testing**: Read entities from Excel input file
- **API integration**: Call OpenSearch API with appropriate entity types
- **Baseline comparison**: Compare results with existing GDC data
- **Multi-source analysis**: Handle different data sources (WATCH, PEP, RIGHTS, SOE, etc.)
- **Comprehensive reporting**: Generate detailed Excel and HTML reports

### Reporting Features
- **Excel Reports**: Multi-sheet reports with summary, details, and "All Hits" consolidated view
- **HTML Reports**: Web-friendly reports with Unicode support for multi-language content
- **Visual indicators**: Color-coded status indicators for different record types
- **Comprehensive coverage**: Show common records, missing records, and new records

## Quick Start

### 1. Setup Environment
```bash
pip install -r requirements.txt
```

### 2. Configure API Settings
Update the API configuration in the testing scripts:
```python
self.api_config = {
    'url': 'https://your-opensearch-endpoint.com/search',
    'headers': {
        'x-api-key': 'your-api-key',
        'Content-Type': 'application/json'
    }
}
```

### 3. Run Consolidated Regression Testing
```bash
cd testcases
python3 consolidated_regression_test.py
```

This will:
- Read entities from `GDC Old System Result.xlsx`
- Call OpenSearch API for each entity
- Compare results with existing GDC baseline data
- Generate comprehensive Excel and HTML reports

## Input Data Format

The Excel input file (`GDC Old System Result.xlsx`) should contain:
- **Entity Name**: Name to search for
- **Type**: "E" for entities, "P" for persons  
- **Existing GDC Results**: Baseline data in JSON format

## Output Reports

### Excel Reports
- **Overall Summary**: High-level statistics across all entities
- **All Hits - Comprehensive**: Every record from both GDC and OpenSearch with status indicators
- **Entity Summary**: One row per entity with totals
- **Individual Entity Sheets**: Detailed breakdown per entity with source-specific results

### HTML Reports
- **Table of Contents**: Easy navigation between entities
- **Multi-language Support**: Proper Unicode rendering for Arabic, Chinese, Cyrillic, Hebrew text
- **Color-coded Results**: Visual status indicators (Common, Missing from OpenSearch, Missing from GDC)
- **Detailed Comparisons**: Side-by-side result analysis

## Configuration

### API Configuration
Update the OpenSearch API endpoint and authentication in the testing scripts:
```python
self.api_config = {
    'url': 'https://15krnwu233.execute-api.us-east-1.amazonaws.com/prod/search',
    'headers': {
        'x-api-key': 'your-api-key-here',
        'Content-Type': 'application/json'
    }
}
```

### Entity Type Mapping
- **Type "E"**: Searches entities/organizations
- **Type "P"**: Searches persons

## Dependencies

- **pandas**: Data manipulation and Excel generation
- **openpyxl**: Excel file handling
- **requests**: HTTP API calls
- **datetime**: Timestamp generation
- **json**: JSON data processing
- **html**: HTML escaping for Unicode support

## Recent Updates

- ✅ Consolidated regression testing framework
- ✅ Excel-driven entity testing from input file
- ✅ Multi-language Unicode support in HTML reports
- ✅ Comprehensive "All Hits" reporting with status indicators
- ✅ Clean codebase focused on core testing functionality

## Usage Examples

### Running the Main Test Suite
```bash
cd testcases
python3 consolidated_regression_test.py
```

This generates:
- `results/consolidated_regression_report_[timestamp].xlsx`
- `results/consolidated_regression_report_[timestamp].html`

### Running Individual Entity Tests
```bash
cd testcases
python3 excel_driven_regression_test.py
```

## Report Interpretation

### Status Categories
- **Common**: Records found in both existing GDC and current OpenSearch
- **Missing from OpenSearch**: Records only in existing GDC data
- **Missing from Existing GDC**: Records only in current OpenSearch

### Excel "All Hits" Sheet
Shows every record with columns:
- Entity Name, Entity Type, Source
- Status (Common/Missing from OpenSearch/Missing from Existing GDC)
- ID, Full Name, Other Names
- Presence indicators (✓ Yes / ✗ No for each system)

## Latest Test Results

**Last Run:** September 16, 2025
- **Total Entities Tested:** 17 (10 organizations, 7 persons)
- **Common Records:** 3
- **New in OpenSearch:** 3
- **Missing from OpenSearch:** 106

The testing framework successfully processes multi-language entities and generates comprehensive reports for analysis.

## Support

For questions or issues, refer to the testcases/README.md file or review the generated reports for detailed analysis results.