#!/usr/bin/env python3
"""
Test script to demonstrate the improved configuration management
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config

def main():
    print("🔧 GDC Automation Configuration Test")
    print("=" * 50)
    
    # Load configuration
    config.load_from_file()
    
    # Display current configuration
    print("\n📋 Current Configuration:")
    print(f"  Excel File: {config.excel_file_path}")
    print(f"  Results Directory: {config.results_directory}")
    print(f"  API URL: {config.api_config['url']}")
    print(f"  API Key: {'***' + config.api_config['api_key'][-4:] if config.api_config['api_key'] else 'Not set'}")
    print(f"  Timeout: {config.api_config['timeout']}s")
    print(f"  Max Retries: {config.test_config['max_retries']}")
    print(f"  Search Limit: {config.test_config['limit']}")
    
    # Validate configuration
    print("\n✅ Configuration Validation:")
    if config.validate():
        print("  All checks passed!")
    else:
        print("  Some issues found. Please check your configuration.")
    
    # Test API headers
    print("\n🔑 API Headers:")
    headers = config.get_api_headers()
    for key, value in headers.items():
        if key.lower() in ['x-api-key', 'authorization']:
            print(f"  {key}: {'***' + str(value)[-4:] if value else 'Not set'}")
        else:
            print(f"  {key}: {value}")
    
    # Test search payload
    print("\n📤 Sample Search Payload:")
    payload = config.get_search_payload("Test Entity", "P")
    print(f"  {payload}")

if __name__ == "__main__":
    main()
