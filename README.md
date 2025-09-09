# Search Results Comparison Automation

This tool automates the comparison between old MySQL search results and new OpenSearch API results to identify true matches vs false positives.

## Features

- 🔍 Automated comparison of search results
- 📊 Excel and HTML report generation
- 🎯 True positive/false positive analysis
- 📈 Similarity scoring and metrics
- 🔄 Batch processing of multiple queries
- 🎨 Colored console output with progress bars

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Database and API Settings**
   - Update `config.py` with your actual database name
   - Ensure your API token is valid and not expired
   - Verify database connection details

3. **Update Table Structure**
   - Modify `mysql_client.py` to match your actual MySQL table structure
   - Update field mappings in `comparison_engine.py` based on your data schema

## Usage

### Basic Usage
```bash
python3 main.py
```

### Custom Configuration
Edit `main.py` to specify:
- Custom queries to test
- MySQL table name
- Comparison parameters

## File Structure

```
├── main.py                 # Main automation script
├── config.py              # Configuration settings
├── api_client.py          # OpenSearch API client
├── mysql_client.py        # MySQL database client
├── comparison_engine.py   # Result comparison logic
├── report_generator.py    # Excel/HTML report generation
├── requirements.txt       # Python dependencies
└── reports/              # Generated reports directory
```

## Configuration

### Database Settings
Update these in `config.py`:
- `DB_NAME`: Your actual database name
- Table structure in `mysql_client.py`

### API Settings
- `API_TOKEN`: Ensure token is not expired
- `API_URL`: Verify endpoint is correct

### Comparison Settings
- `similarity_threshold`: Adjust in `comparison_engine.py` (default: 0.8)
- Field mappings for old vs new result structures

## Reports

The tool generates two types of reports:

### Excel Report
- **Summary Sheet**: Overview of all queries with metrics
- **Detailed Comparison Sheet**: Line-by-line comparison results

### HTML Report
- Interactive web report with:
  - Overall statistics dashboard
  - Query-by-query breakdown
  - Detailed false positive/negative analysis

## Customization

### Adding New Comparison Logic
Modify `comparison_engine.py` to:
- Add custom similarity algorithms
- Include additional matching criteria
- Adjust scoring mechanisms

### Custom Report Formats
Extend `report_generator.py` to:
- Add new report formats (PDF, CSV, etc.)
- Customize report styling
- Include additional metrics

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify host, port, username, password
   - Check network connectivity
   - Ensure database exists

2. **API Authentication Failed**
   - Check if token is expired
   - Verify token format and permissions
   - Test API endpoint manually

3. **No Results Found**
   - Verify table name and structure
   - Check query format
   - Ensure data exists in database

### Debug Mode
Add debug prints or use Python debugger to trace issues:
```python
import pdb; pdb.set_trace()
```

## Next Steps

1. **Update Database Schema**: Modify `mysql_client.py` to match your actual table structure
2. **Test with Real Data**: Run with a small subset of real queries first
3. **Tune Parameters**: Adjust similarity thresholds based on your data
4. **Schedule Automation**: Set up cron jobs or scheduled tasks for regular comparisons
5. **Add Monitoring**: Implement alerts for significant changes in match rates

## Support

For issues or questions:
1. Check the console output for error messages
2. Review the generated reports for insights
3. Verify configuration settings
4. Test individual components separately
