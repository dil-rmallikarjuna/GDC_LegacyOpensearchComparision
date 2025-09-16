# AGILENT TECHNOLOGIES Regression Test

## What This Does
Single file that contains:
1. **Baseline data** (your original system results from 2025-09-12)
2. **Live OpenSearch API call** to fetch current results for "AGILENT TECHNOLOGIES"
3. **Comparison** between baseline and live OpenSearch results
4. **Report generation** (Excel + HTML)

## Files
- `agilent_technologies_regression.py` - Main test file
- `requirements.txt` - Dependencies
- `results/` - Generated reports

## How to Use

### 1. Install Dependencies
```bash
pip install pandas openpyxl requests
```

### 2. Configure OpenSearch API
Edit `agilent_technologies_regression.py` and update the API configuration:
```python
self.api_config = {
    "url": "https://your-opensearch-endpoint.com/api/search",  # Your actual OpenSearch API URL
    "api_key": "your-api-key-here",  # Your API key (or None if not needed)
    "timeout": 30
}
```

### 3. Run Test
```bash
python3 agilent_technologies_regression.py
```

## What Happens When You Run It

1. **Calls OpenSearch API** with entity name "AGILENT TECHNOLOGIES"
2. **Gets live results** from your current OpenSearch system
3. **Compares with baseline** (your original results from 2025-09-12)
4. **Shows differences**:
   - **Old Hits**: Records in baseline but missing from current OpenSearch
   - **New OpenSearch Hits**: Records in current OpenSearch but not in baseline
   - **Common Ones**: Records present in both (exact matches or modified)
   - **Missing Ones**: Records that disappeared

## Output Reports
- **Console**: Summary of changes with counts
- **Excel Report**: Detailed comparison with separate sheets per data source
- **HTML Report**: Beautiful web-based report with visual styling

## Report Categories
- **Exact Matches**: Records identical in both baseline and current
- **Modified**: Records that exist in both but have changed data
- **New Records**: Present only in current OpenSearch results
- **Missing Records**: Present only in baseline (removed from OpenSearch)

## API Integration
The test automatically:
- Calls your OpenSearch API with the same payload structure you provided
- Handles API errors gracefully (falls back to mock data for testing)
- Transforms the API response to match the expected format
- Compares across all data sources (WATCH, ICIJ, MEX, RIGHTS, PEP, SANCTION, SOE, COL, MEDIA, OFAC)

## Adding More Entities
Copy `agilent_technologies_regression.py` to `new_entity_regression.py` and update:
1. Entity name in `__init__`
2. Baseline data with your entity's current results
3. API configuration (same endpoint, different entity name)
