#!/usr/bin/env python3
"""
Configuration management for GDC Automation Excel-Driven Regression Testing Framework
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for managing API settings and file paths"""
    
    def __init__(self):
        """Initialize configuration with default values"""
        self.excel_file_path = "/Users/rmallikarjuna/Documents/GDC automation excel driven/Test terms.xlsx"
        self.results_directory = "/Users/rmallikarjuna/Documents/GDC automation excel driven/results"
        
        # API Configuration
        self.api_config = {
            "url": os.getenv("OPENSEARCH_API_URL", "https://15krnwu233.execute-api.us-east-1.amazonaws.com/prod/search"),
            "api_key": os.getenv("OPENSEARCH_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJyZWFkLWNsaWVudCIsInJvbGUiOiJyZWFkIiwicGVybWlzc2lvbnMiOlsicmVhZCJdLCJleHAiOjE3NTgwODcyMzIsImlhdCI6MTc1ODA4MzYzMiwiaXNzIjoiZ2RjLXNlYXJjaC1pZGVudGl0eS1zZXJ2aWNlIn0.8-ffozf_8N1AmiWMgyG1y321K94EzKR_vyQ9VdhqcRM"),
            "timeout": int(os.getenv("API_TIMEOUT", "30")),
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        }
        
        # Test Configuration
        self.test_config = {
            "max_retries": int(os.getenv("MAX_RETRIES", "3")),
            "retry_delay": float(os.getenv("RETRY_DELAY", "1.0")),
            "batch_size": int(os.getenv("BATCH_SIZE", "10")),
            "schemas": ["col", "rights", "mex", "watch", "soe", "pep", "sanction", "icij"],
            "search_types": ["keyword", "phonetic", "similarity"],
            "limit": int(os.getenv("SEARCH_LIMIT", "100"))
        }
        
        # Report Configuration
        self.report_config = {
            "exclude_ofac": True,
            "include_html": True,
            "include_excel": True,
            "status_colors": {
                "present_in_both": "#d4edda",
                "opensearch_only": "#cce5ff", 
                "legacy_only": "#fff3cd"
            }
        }
    
    def load_from_file(self, config_file: str = "config.json"):
        """Load configuration from JSON file"""
        import json
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Update API config if present
                if "api" in config_data:
                    self.api_config.update(config_data["api"])
                
                # Update test config if present
                if "test" in config_data:
                    self.test_config.update(config_data["test"])
                
                # Update report config if present
                if "report" in config_data:
                    self.report_config.update(config_data["report"])
                    
                print(f"✅ Configuration loaded from {config_file}")
            except Exception as e:
                print(f"⚠️  Warning: Could not load config file {config_file}: {e}")
        else:
            print(f"ℹ️  No config file found at {config_file}, using defaults")
    
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        
        # Check API configuration
        if not self.api_config.get("url"):
            errors.append("API URL is required")
        
        if not self.api_config.get("api_key"):
            errors.append("API Key is required")
        
        # Check file paths
        if not os.path.exists(self.excel_file_path):
            errors.append(f"Excel file not found: {self.excel_file_path}")
        
        # Check results directory
        if not os.path.exists(self.results_directory):
            try:
                os.makedirs(self.results_directory, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create results directory: {e}")
        
        if errors:
            print("❌ Configuration validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print("✅ Configuration validation passed")
        return True
    
    def get_api_headers(self) -> Dict[str, str]:
        """Get API headers with authentication"""
        headers = self.api_config["headers"].copy()
        if self.api_config.get("api_key"):
            headers["x-api-key"] = self.api_config["api_key"]
        return headers
    
    def get_search_payload(self, query: str, entity_type: str) -> Dict[str, Any]:
        """Generate search payload for API request with all schemas for both Person and Entity"""
        # Fetch all schemas for both Person and Entity types
        schemas = ["col", "rights", "mex", "watch", "soe", "pep", "sanction", "icij"]
        
        return {
            "query": query,
            "schemas": schemas,
            "limit": self.test_config["limit"],
            "search_types": self.test_config["search_types"]
        }

# Global configuration instance
config = Config()
