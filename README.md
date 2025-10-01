# GDC Automation Excel-Driven Regression Testing Framework

## Overview
A comprehensive regression testing framework that compares OpenSearch API results with Legacy GDC system data. The framework reads test entities from an Excel file and generates detailed comparison reports in both Excel and HTML formats.

## What This Framework Does
1. **Reads test entities** from `Test terms.xlsx` Excel file
2. **Fetches current data** from OpenSearch API for each entity
3. **Compares results** between OpenSearch and Legacy GDC systems(Which is addded manully)
4. **Generates unified reports** showing matches, differences, and missing records
5. **Excludes OFAC data** and handles ICIJ records with special schema handling

## Project Structure
```
GDC automation excel driven/
├── Test terms.xlsx                     # Main Excel input file
├── GDC Old System Result copy.xlsx    # Backup copy
├── README.md                          # This documentation
├── requirements.txt                   # Dependencies
├── config.py                          # Configuration management
├── config.json                        # Configuration file (optional)
├── env.template                       # Environment variables template
├── test_config.py                     # Configuration testing script
├── results/                           # Generated reports
│   ├── unified_opensearch_vs_legacy_comparison_*.xlsx
│   └── unified_opensearch_vs_legacy_comparison_*.html
└── testcases/
    └── excel_driven_regression_test.py # Main testing framework
```

## Architecture Improvements

### ✅ Configuration Management
- **Centralized Configuration**: All settings managed in `config.py`
- **Multiple Configuration Sources**: Environment variables, JSON file, or direct code
- **Validation**: Automatic configuration validation before running tests
- **Security**: API keys can be stored in environment variables

### ✅ Better Error Handling
- **Retry Logic**: Automatic retry on API failures
- **Graceful Degradation**: Continues processing even if individual entities fail
- **Detailed Logging**: Clear error messages and progress indicators

### ✅ Maintainability
- **Separation of Concerns**: Configuration separate from business logic
- **Easy Updates**: Change API endpoints without touching test code
- **Environment Support**: Different configs for dev/staging/prod

## Excel Input Format
The framework reads from `Test terms.xlsx` with the following columns:
- **Name**: Entity name to search for
- **Type**: Entity type (P for Person, E for Entity)
- **Current GDC response**: Legacy GDC data in JSON format

## How to Use

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure the Framework
You have multiple options for configuration:

#### Option A: Environment Variables (Recommended)
Create a `.env` file in the project root:
```bash
cp env.template .env
# Edit .env with your actual values
```

#### Option B: Configuration File
Edit `config.json` with your settings:
```json
{
  "api": {
    "url": "https://your-api-endpoint.com/search",
    "api_key": "your-api-key-here",
    "timeout": 30
  }
}
```

#### Option C: Direct Code Modification
Edit `config.py` and update the default values.

### 3. Test Configuration
```bash
python test_config.py
```

### 4. Prepare Excel File
Ensure your `Test terms.xlsx` file contains:
- Test entities in the "Name" column
- Entity types (P/E) in the "Type" column
- Legacy GDC JSON data in the "Current GDC response" column

### 5. Run Tests
```bash
cd testcases
python3 excel_driven_regression_test.py
```

## What Happens When You Run It

1. **Loads entities** from the Excel file
2. **Calls OpenSearch API** for each entity with appropriate schemas
3. **Compares results** between OpenSearch and Legacy GDC systems
4. **Generates unified reports** with detailed comparison data
5. **Shows summary statistics** in the console

## Output Reports

### Excel Report
- **Unified Comparison Sheet**: Complete comparison with all columns
- **Test Key**: Clean entity name (without _P/_E suffixes)
- **Search Term**: Original search term
- **Type**: Person or Entity
- **Status**: Present in Both, OpenSearch Only, Legacy Only
- **OpenSearch Data**: Name, ID, Schema
- **Legacy Data**: Name, ID, Schema

### HTML Report
- **Visual interface** with color-coded status badges
- **Summary statistics** cards
- **Interactive table** with hover effects
- **Responsive design** for different screen sizes
- **Status indicators**:
  - 🟢 **Present in Both** (Green)
  - 🔵 **OpenSearch Only** (Blue)  
  - 🟡 **Legacy Only** (Yellow)

## Data Sources Supported
- **WATCH**: Watchlist data
- **PEP**: Politically Exposed Persons
- **SANCTION**: Sanctions data
- **ICIJ**: ICIJ database (special schema handling)
- **MEX**: Mexico-specific data
- **RIGHTS**: Human rights data
- **SOE**: State-Owned Enterprises
- **COL**: Colombia-specific data
- **MEDIA**: Media-related data
- **OFAC**: Excluded as requested

## Special Features

### ICIJ Handling
- Special schema processing for ICIJ records
- Includes `Entity_Name` and `Entity_Type` fields
- Different data structure handling

### Name Construction
- Automatically constructs full names from First_Name + Last_Name when Full_Name is empty
- Handles legacy data with missing name fields

### Data Filtering
- Excludes OFAC data as requested
- Handles empty values by showing "Not Present" instead of blanks

## Report Columns
1. **Test Key**: Clean entity name
2. **Search Term**: Original search term
3. **Type**: Person or Entity
4. **Status**: Presence status with color coding
5. **OpenSearch Name**: Name from OpenSearch
6. **OpenSearch ID**: ID from OpenSearch
7. **OpenSearch Schema**: Schema type from OpenSearch
8. **Legacy Name**: Name from Legacy GDC
9. **Legacy ID**: ID from Legacy GDC
10. **Legacy Schema**: Schema type from Legacy GDC

## Summary Statistics
- **Total Records**: All comparison records
- **OpenSearch Records**: Records found in OpenSearch
- **Legacy GDC Records**: Records found in Legacy system
- **Matched Records**: Records present in both systems
- **OpenSearch Only**: Records only in OpenSearch
- **Legacy Only**: Records only in Legacy GDC

## Error Handling
- Graceful API error handling
- Fallback to empty data on API failures
- Detailed error logging
- Continues processing even if individual entities fail

## Customization
To add more test entities:
1. Add rows to `Test terms.xlsx`
2. Include Name, Type, and Current GDC response columns
3. Run the framework - it will automatically process all entities

## Requirements
- Python 3.6+
- pandas
- openpyxl
- requests

## API Configuration
The framework is configured to work with AWS API Gateway endpoints and includes proper authentication headers. Update the API configuration in the `__init__` method to match your OpenSearch setup.

## Recent Updates
- ✅ Simplified framework with only Excel-driven regression testing
- ✅ Moved results folder to root directory for easier access
- ✅ Updated all file references and documentation
- ✅ Clean codebase focused on core testing functionality
- ✅ Comprehensive HTML and Excel reporting with status indicators