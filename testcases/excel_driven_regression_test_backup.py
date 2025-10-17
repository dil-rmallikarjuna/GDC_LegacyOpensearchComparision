#!/usr/bin/env python3
"""
Excel-Driven Regression Testing Framework
Reads entity data from Excel file and performs regression testing for each entity.
Generates a single unified comparison report between OpenSearch and GDC legacy data.
"""

import requests
import json
import pandas as pd
from datetime import datetime
import os
import hashlib
import sys
import time
import re

# Add parent directory to path to import config and utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config
from utils.report_generator import ReportGenerator

def clean_json_string(json_str):
    """
    Clean malformed JSON string by fixing common issues
    """
    if not isinstance(json_str, str):
        return json_str
    
    try:
        # Fix invalid Unicode escapes
        json_str = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), json_str)
        
        # Fix unterminated strings
        json_str = re.sub(r'"[^"]*$', '"', json_str)
        
        # Fix missing closing braces
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        if open_braces > close_braces:
            json_str += '}' * (open_braces - close_braces)
        
        # Fix missing closing brackets
        open_brackets = json_str.count('[')
        close_brackets = json_str.count(']')
        if open_brackets > close_brackets:
            json_str += ']' * (open_brackets - close_brackets)
        
        return json_str
    except Exception as e:
        print(f"Error cleaning JSON string: {e}")
        return json_str

class ExcelDrivenRegressionTest:
    def __init__(self, excel_path=None):
        # Load configuration from parent directory
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
        config.load_from_file(config_path)
        
        # Use provided path or config default
        self.excel_path = excel_path or config.excel_file_path
        
        # Validate configuration
        if not config.validate():
            raise ValueError("Configuration validation failed. Please check your settings.")
        
        # Results storage for unified comparison
        self.unified_comparison_data = []
        
        # Track entities with corrupted JSON
        self.skipped_entities = []
        
        # Initialize report generator
        self.report_generator = ReportGenerator(config.results_directory)
    
    def load_entities_from_excel(self):
        """
        Load entity data from Excel file
        """
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Sheet1')
            
            # Clean the data - remove NaN rows
            df = df.dropna(subset=['Name', 'Type'])
            
            entities = []
            for index, row in df.iterrows():
                entity = {
                    "name": row['Name'],
                    "type": row['Type'],  # E for Entity, P for Person
                    "current_gdc_response": row.get('Current GDC respose', ''),
                    "row_index": index
                }
                
                # Parse the current GDC response if it's not "No Hits"
                if entity["current_gdc_response"] and entity["current_gdc_response"] != "No Hits":
                    try:
                        if isinstance(entity["current_gdc_response"], str):
                            # Check if JSON looks corrupted (common patterns)
                            if any(pattern in entity["current_gdc_response"] for pattern in [
                                "Invalid \\uXXXX escape", "Unterminated string", "Expecting value"
                            ]):
                                print(f"Skipping {entity['name']} - corrupted JSON detected")
                                self.skipped_entities.append(entity['name'])
                                entity["baseline_data"] = {}
                            else:
                            gdc_data = json.loads(entity["current_gdc_response"])
                                entity["baseline_data"] = self.parse_gdc_response(gdc_data, entity["name"])
                        else:
                            entity["baseline_data"] = {}
                    except (json.JSONDecodeError, Exception) as e:
                        print(f"Error parsing GDC response for {entity['name']}: {e}")
                        entity["baseline_data"] = {}
                else:
                    entity["baseline_data"] = {}
                
                entities.append(entity)
            
            print(f"Loaded {len(entities)} entities from Excel file")
            return entities
            
        except Exception as e:
            print(f"Error loading Excel file: {e}")
            return []
    
    def parse_gdc_response(self, gdc_data, entity_name=""):
        """
        Parse GDC response JSON to extract baseline data with robust error handling
        Excludes OFAC data as requested
        """
        baseline_data = {
            "col": [],
            "rights": [],
            "mex": [],
            "watch": [],
            "soe": [],
            "pep": [],
            "sanction": [],
            "icij": [],
            "media": []
            # Note: OFAC excluded as requested
        }
        
        try:
            # Handle malformed JSON gracefully with multiple fallback strategies
            if isinstance(gdc_data, str):
                try:
                    # First attempt: Standard JSON parsing
                    gdc_data = json.loads(gdc_data)
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error for {entity_name}: {e}")
                    # Skip entities with malformed JSON completely
                    print(f"Skipping {entity_name} due to corrupted JSON data")
                    return baseline_data
            
            # Navigate through the GDC response structure
            if "Args" in gdc_data and len(gdc_data["Args"]) > 0:
                args = gdc_data["Args"][0]
                if "nameSearch" in args and "Preview" in args["nameSearch"]:
                    preview = args["nameSearch"]["Preview"]
                    
                    # Extract data from each source
                    for source, records in preview.items():
                        # Skip OFAC data as requested
                        if source.lower() == "ofac":
                            continue
                            
                        if source.lower() in baseline_data and isinstance(records, list):
                            for record in records:
                                # Handle ICIJ differently - it has different schema
                                if source.lower() == "icij":
                                    # Construct full name if not present
                                    full_name = record.get("Full_Name", "")
                                    if not full_name:
                                        first_name = record.get("First_Name", "")
                                        last_name = record.get("Last_Name", "")
                                        if first_name or last_name:
                                            full_name = f"{first_name} {last_name}".strip()
                                        else:
                                            full_name = record.get("Entity_Name", "")
                                    
                                    normalized_record = {
                                        "recid": record.get("recid", 0),
                                        "ID": record.get("ID", ""),
                                        "First_Name": record.get("First_Name", ""),
                                        "Last_Name": record.get("Last_Name", ""),
                                        "Full_Name": full_name,
                                        "Other_Names": record.get("Other_Names", ""),
                                        "AltScript": record.get("AltScript", ""),
                                        "RecType": "ICIJ",  # Special handling for ICIJ
                                        "Entity_Name": record.get("Entity_Name", ""),  # ICIJ specific field
                                        "Entity_Type": record.get("Entity_Type", "")   # ICIJ specific field
                                    }
                                else:
                                    # Construct full name if not present
                                    full_name = record.get("Full_Name", "")
                                    if not full_name:
                                        first_name = record.get("First_Name", "")
                                        last_name = record.get("Last_Name", "")
                                        if first_name or last_name:
                                            full_name = f"{first_name} {last_name}".strip()
                                    
                                    # Standard record structure for other sources
                                normalized_record = {
                                    "recid": record.get("recid", 0),
                                    "ID": record.get("ID", ""),
                                    "First_Name": record.get("First_Name", ""),
                                    "Last_Name": record.get("Last_Name", ""),
                                        "Full_Name": full_name,
                                    "Other_Names": record.get("Other_Names", ""),
                                    "AltScript": record.get("AltScript", ""),
                                    "RecType": record.get("RecType", "")
                                }
                                baseline_data[source.lower()].append(normalized_record)
            
        except Exception as e:
            print(f"Error parsing GDC response for {entity_name}: {e}")
            # Continue processing other entities even if one fails
        
        return baseline_data
    
    def fetch_current_data(self, entity_name, entity_type):
        """
        Fetch current data from OpenSearch API with retry logic
        """
        max_retries = config.test_config["max_retries"]
        retry_delay = config.test_config["retry_delay"]
        
        # Generate payload using config with correct schemas based on entity type
        payload = config.get_search_payload(entity_name, entity_type)
        
        # Get headers with authentication
        headers = config.get_api_headers()
        
        for attempt in range(max_retries):
            try:
                print(f"Calling OpenSearch API for {entity_name} (Type: {entity_type})... (Attempt {attempt + 1}/{max_retries})")
            print(f"Payload: {payload}")
            
                response = requests.post(
                    config.api_config["url"],
                    json=payload,
                    headers=headers,
                    timeout=config.api_config["timeout"]
                )
            response.raise_for_status()
            
            api_result = response.json()
            print(f"API Response received successfully")
            
            # Transform API response to match our expected format
            return self.transform_opensearch_response(api_result)
            
        except requests.exceptions.RequestException as e:
                print(f"Error calling OpenSearch API (Attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print("All retry attempts failed. Returning empty data...")
                    break
        
        # Return empty data structure if all API calls fail
            return {
            "col": [],
            "rights": [],
            "mex": [],
                "watch": [],
            "soe": [],
                "pep": [],
                "sanction": [],
            "icij": [],
                "media": [],
                "ofac": []
            }
    
    def transform_opensearch_response(self, api_response):
        """
        Transform OpenSearch API response to match our expected format
        """
        
        try:
            print(f"Raw API response keys: {list(api_response.keys()) if isinstance(api_response, dict) else type(api_response)}")
            
            # Initialize transformed data structure (excluding OFAC as requested)
            transformed_data = {
                "col": [],
                "rights": [],
                "mex": [],
                "watch": [],
                "soe": [],
                "pep": [],
                "sanction": [],
                "icij": [],
                "media": []
            }
            
            # Check if API response has results
            if isinstance(api_response, dict):
                # Look for results in various possible structures
                results = None
                
                # Try different possible response structures
                if "results" in api_response:
                    results = api_response["results"]
                elif "data" in api_response:
                    results = api_response["data"]
                elif "hits" in api_response:
                    results = api_response["hits"]
                
                if results and isinstance(results, list):
                    print(f"Processing results structure: {type(results)}")
                    
                    # Debug: Print sample data structure
                    if len(results) > 0:
                        sample_record = results[0]
                        print(f"Sample _source fields: {list(sample_record.get('_source', {}).keys()) if '_source' in sample_record else 'No _source field'}")
                    
                    for record in results:
                        normalized_record = self.normalize_api_record(record)
                        if normalized_record:
                            source = self.determine_record_source(record)
                            if source in transformed_data:
                                transformed_data[source].append(normalized_record)
                
                # Print summary of transformed data
                for source, records in transformed_data.items():
                    if records:
                        print(f"  {source.upper()}: {len(records)} records")
                
                return transformed_data
            
            print("No valid results structure found in API response")
            return transformed_data
            
        except Exception as e:
            print(f"Error transforming API response: {e}")
            return None
    
    def normalize_api_record(self, record):
        """
        Normalize a single API record to match our expected format
        """
        try:
            # Extract data from _source field if it exists
            source_data = record.get("_source", record)
            
            # Extract recid - try multiple possible fields
            recid = None
            if "recid" in source_data:
                recid = source_data["recid"]
            elif "record_id" in source_data:
                recid = source_data["record_id"]
            elif "_id" in record:
                # Fallback: use hash of _id if no recid found
                recid = hash(record["_id"]) % 10000000  # Convert to reasonable number
            
            if not recid:
                return None
            
            # Construct full name if not present
            full_name = source_data.get("Full_Name", "")
            if not full_name:
                first_name = source_data.get("First_Name", "")
                last_name = source_data.get("Last_Name", "")
                if first_name or last_name:
                    full_name = f"{first_name} {last_name}".strip()
            
            # Handle ICIJ differently - it has different schema
            if source_data.get("RecType") == "ICIJ" or "icij" in str(source_data.get("_index", "")).lower():
                # For ICIJ, try to get name from multiple possible fields
                icij_name = (source_data.get("name", "") or 
                            source_data.get("Entity_Name", "") or 
                            source_data.get("Full_Name", "") or 
                            full_name or 
                            source_data.get("First_Name", "") or 
                            source_data.get("Last_Name", ""))
                
                return {
                    "recid": recid,
                    "ID": source_data.get("ID", ""),
                    "First_Name": source_data.get("First_Name", ""),
                    "Last_Name": source_data.get("Last_Name", ""),
                    "Full_Name": icij_name,  # Use the best available name
                    "Other_Names": source_data.get("Other_Names", source_data.get("otherNames", "")),
                    "AltScript": source_data.get("AltScript", ""),
                    "RecType": "ICIJ",  # Special handling for ICIJ
                    "Entity_Name": source_data.get("Entity_Name", ""),  # ICIJ specific field
                    "Entity_Type": source_data.get("Entity_Type", "")   # ICIJ specific field
                }
            else:
            return {
                "recid": recid,
                "ID": source_data.get("ID", ""),
                "First_Name": source_data.get("First_Name", ""),
                "Last_Name": source_data.get("Last_Name", ""),
                "Full_Name": full_name,
                "Other_Names": source_data.get("Other_Names", source_data.get("otherNames", "")),
                "AltScript": source_data.get("AltScript", ""),
                "RecType": source_data.get("RecType", "")
            }
            
        except Exception as e:
            print(f"Error normalizing record: {e}")
            return None
    
    def determine_record_source(self, record):
        """
        Determine which source/schema this record belongs to
        """
        # Check _source field first
        source_data = record.get("_source", record)
        
        # Try to determine source from various indicators
        if "_index" in record:
            index_name = record["_index"].lower()
            if "pep" in index_name:
                return "pep"
            elif "watch" in index_name:
                return "watch"
            elif "sanction" in index_name:
                return "sanction"
            elif "icij" in index_name:
                return "icij"
            elif "mex" in index_name:
                return "mex"
            elif "soe" in index_name:
                return "soe"
            elif "rights" in index_name:
                return "rights"
            elif "col" in index_name:
                return "col"
            elif "media" in index_name:
                return "media"
            elif "ofac" in index_name:
                return "ofac"
        
        # Fallback: try to determine from ID pattern or other fields
        record_id = source_data.get("ID", "")
        if record_id.startswith("101"):
            return "pep"
        elif record_id.startswith("202"):
            return "watch"
        elif record_id.startswith("901"):
            return "soe"
        elif record_id.startswith("307"):
            return "rights"
        elif record_id.startswith("801"):
            return "icij"
        
        # Default fallback
        return "watch"
    
    def compare_data(self, entity_name, baseline_data, current_data):
        """
        Compare baseline data with current API data
        """
        comparison_result = {
            "entity_name": entity_name,
            "test_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sources": {}
        }
        
        # Get all unique sources from both datasets
        all_sources = set(baseline_data.keys()) | set(current_data.keys())
        
        for source in all_sources:
            baseline_records = baseline_data.get(source, [])
            current_records = current_data.get(source, [])
            
            # Create lookup dictionaries by recid
            baseline_by_id = {record["recid"]: record for record in baseline_records}
            current_by_id = {record["recid"]: record for record in current_records}
            
            matches = []
            missing_records = []
            new_records = []
            
            # Find matches and missing records
            for recid, baseline_record in baseline_by_id.items():
                if recid in current_by_id:
                    current_record = current_by_id[recid]
                    
                    # Compare records for changes
                    changes = {}
                    for key in ["Full_Name", "Other_Names", "First_Name", "Last_Name"]:
                        if baseline_record.get(key) != current_record.get(key):
                            changes[key] = {
                                "old": baseline_record.get(key),
                                "new": current_record.get(key)
                            }
                    
                    # Construct full name from first and last name if Full_Name is empty
                    full_name = baseline_record.get("Full_Name", "")
                    if not full_name:
                        first_name = baseline_record.get("First_Name", "")
                        last_name = baseline_record.get("Last_Name", "")
                        if first_name or last_name:
                            full_name = f"{first_name} {last_name}".strip()
                    
                    # Construct other names including AltScript
                    other_names_parts = []
                    if baseline_record.get("Other_Names"):
                        other_names_parts.append(baseline_record.get("Other_Names"))
                    if baseline_record.get("otherNames"):
                        other_names_parts.append(baseline_record.get("otherNames"))
                    if baseline_record.get("AltScript"):
                        other_names_parts.append(baseline_record.get("AltScript"))
                    other_names = "; ".join(filter(None, other_names_parts))
                    
                    matches.append({
                        "recid": recid,
                        "ID": baseline_record.get("ID", ""),
                        "Full_Name": full_name,
                        "Other_Names": other_names,
                        "First_Name": baseline_record.get("First_Name", ""),
                        "Last_Name": baseline_record.get("Last_Name", ""),
                        "AltScript": baseline_record.get("AltScript", ""),
                        "status": "exact_match" if not changes else "modified",
                        "changes": changes
                    })
                else:
                    # Record missing in current
                    # Construct full name from first and last name if Full_Name is empty
                    full_name = baseline_record.get("Full_Name", "")
                    if not full_name:
                        first_name = baseline_record.get("First_Name", "")
                        last_name = baseline_record.get("Last_Name", "")
                        if first_name or last_name:
                            full_name = f"{first_name} {last_name}".strip()
                    
                    # Construct other names including AltScript
                    other_names_parts = []
                    if baseline_record.get("Other_Names"):
                        other_names_parts.append(baseline_record.get("Other_Names"))
                    if baseline_record.get("otherNames"):
                        other_names_parts.append(baseline_record.get("otherNames"))
                    if baseline_record.get("AltScript"):
                        other_names_parts.append(baseline_record.get("AltScript"))
                    other_names = "; ".join(filter(None, other_names_parts))
                    
                    missing_records.append({
                        "recid": recid,
                        "ID": baseline_record.get("ID", ""),
                        "Full_Name": full_name,
                        "Other_Names": other_names,
                        "First_Name": baseline_record.get("First_Name", ""),
                        "Last_Name": baseline_record.get("Last_Name", ""),
                        "AltScript": baseline_record.get("AltScript", "")
                    })
            
            # Find new records
            for recid, current_record in current_by_id.items():
                if recid not in baseline_by_id:
                    # Construct full name from first and last name if Full_Name is empty
                    full_name = current_record.get("Full_Name", "")
                    if not full_name:
                        first_name = current_record.get("First_Name", "")
                        last_name = current_record.get("Last_Name", "")
                        if first_name or last_name:
                            full_name = f"{first_name} {last_name}".strip()
                    
                    # Construct other names including AltScript
                    other_names_parts = []
                    if current_record.get("Other_Names"):
                        other_names_parts.append(current_record.get("Other_Names"))
                    if current_record.get("otherNames"):
                        other_names_parts.append(current_record.get("otherNames"))
                    if current_record.get("AltScript"):
                        other_names_parts.append(current_record.get("AltScript"))
                    other_names = "; ".join(filter(None, other_names_parts))
                    
                    new_records.append({
                        "recid": recid,
                        "ID": current_record.get("ID", ""),
                        "Full_Name": full_name,
                        "Other_Names": other_names,
                        "First_Name": current_record.get("First_Name", ""),
                        "Last_Name": current_record.get("Last_Name", ""),
                        "AltScript": current_record.get("AltScript", "")
                    })
            
            comparison_result["sources"][source] = {
                "baseline_count": len(baseline_records),
                "current_count": len(current_records),
                "matches": matches,
                "missing_records": missing_records,
                "new_records": new_records,
                "summary": {
                    "exact_matches": len([m for m in matches if m["status"] == "exact_match"]),
                    "modified_records": len([m for m in matches if m["status"] == "modified"]),
                    "missing_records": len(missing_records),
                    "new_records": len(new_records)
                }
            }
        
        return comparison_result
    
    def generate_unified_comparison_report(self):
        """
        Generate unified comparison reports using the reusable report generator
        """
        # Use the reusable report generator
        excel_filename, html_filename = self.report_generator.generate_unified_comparison_report(
            self.unified_comparison_data,
            "unified_opensearch_vs_legacy_comparison"
        )
        
        # Report skipped entities due to corrupted JSON
        if self.skipped_entities:
            print(f"\n⚠️  Skipped Entities (Corrupted JSON): {len(self.skipped_entities)}")
            for entity in self.skipped_entities[:10]:  # Show first 10
                print(f"    - {entity}")
            if len(self.skipped_entities) > 10:
                print(f"    ... and {len(self.skipped_entities) - 10} more")
        
        return excel_filename, html_filename
    
    
    
    
    def run_all_tests(self):
        """
        Run regression tests for all entities in the Excel file
        """
        print("Excel-Driven Regression Testing Framework - Unified Comparison")
        print("=" * 80)
        
        # Load entities from Excel
        entities = self.load_entities_from_excel()
        
        if not entities:
            print("No entities found in Excel file. Exiting.")
            return
        
        all_results = []
        
        for i, entity in enumerate(entities, 1):
            print(f"\n[{i}/{len(entities)}] Processing: {entity['name']} (Type: {entity['type']})")
            
            # Fetch current data from API
            current_data = self.fetch_current_data(entity['name'], entity['type'])
            
            if current_data is None:
                print(f"Failed to fetch current data for {entity['name']}. Skipping.")
                continue
            
            # Compare data
            comparison_result = self.compare_data(entity['name'], entity['baseline_data'], current_data)
            
            # Store data for unified comparison
            self.unified_comparison_data.append({
                'search_term': entity['name'],
                'entity_type': entity['type'],
                'opensearch_results': current_data,
                'legacy_results': entity['baseline_data']
            })
            
            # Print simple summary
            print(f"✅ Processed {entity['name']} - OpenSearch: {len([r for source in current_data.values() for r in source])} records, Legacy: {len([r for source in entity['baseline_data'].values() for r in source])} records")
            
        # Generate unified comparison report
        print(f"\n{'='*80}")
        print("Generating unified comparison report...")
        excel_file, html_file = self.generate_unified_comparison_report()
        if excel_file and html_file:
            print(f"✅ Reports generated successfully!")
        print("All tests completed!")
    

if __name__ == "__main__":
    # Run the Excel-driven regression test framework
    framework = ExcelDrivenRegressionTest()
    framework.run_all_tests()
