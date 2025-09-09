"""
Configuration settings for the OpenSearch relevance analysis tool.
"""
import os

class Config:
    """Configuration class for API settings."""
    
    # API Configuration
    API_URL = os.getenv('API_URL', 'https://15krnwu233.execute-api.us-east-1.amazonaws.com/prod/search')
    API_TOKEN = os.getenv('API_TOKEN', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJyZWFkLWNsaWVudCIsInJvbGUiOiJyZWFkIiwicGVybWlzc2lvbnMiOlsicmVhZCJdLCJleHAiOjE3NTY5ODEzNTYsImlhdCI6MTc1Njk3Nzc1NiwiaXNzIjoiZ2RjLXNlYXJjaC1pZGVudGl0eS1zZXJ2aWNlIn0.2GV0P-1-OWsTMFmL3rNOXJps6B1SuTS6DV97ADga5iA')
    
    # Report Configuration
    REPORT_OUTPUT_DIR = os.getenv('REPORT_OUTPUT_DIR', 'reports')
    EXCEL_FILENAME = os.getenv('EXCEL_FILENAME', 'opensearch_relevance_report.xlsx')
    HTML_FILENAME = os.getenv('HTML_FILENAME', 'opensearch_relevance_report.html')
    
    # Default search parameters
    DEFAULT_SCHEMAS = ["col", "rights", "mex", "watch", "soe", "pep", "sanctions"]
    DEFAULT_SEARCH_TYPES = ["keyword", "phonetic", "similarity"]
    DEFAULT_LIMIT = 10
    
    # API Headers
    API_HEADERS = {
        'accept': '*/*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'authorization': f'Bearer {API_TOKEN}',
        'content-type': 'application/json',
        'origin': 'https://15krnwu233.execute-api.us-east-1.amazonaws.com',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
    }
