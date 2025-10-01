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

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

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
        
        # Ensure results directory exists
        os.makedirs(config.results_directory, exist_ok=True)
    
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
                return {
                    "recid": recid,
                    "ID": source_data.get("ID", ""),
                    "First_Name": source_data.get("First_Name", ""),
                    "Last_Name": source_data.get("Last_Name", ""),
                    "Full_Name": full_name,
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
        Generate unified comparison reports (Excel and HTML) with the specified format:
        Test Key, Search Term, Type, OpenSearch Name, OpenSearch ID, OpenSearch Schema, Legacy Name, Legacy ID, Legacy Schema
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create unified comparison data
        unified_data = []
        
        for comparison_data in self.unified_comparison_data:
            search_term = comparison_data['search_term']
            entity_type = comparison_data['entity_type']
            test_key = search_term  # Remove _E and _P suffixes
            type_label = "Person" if entity_type == "P" else "Entity"
            
            # Get OpenSearch results
            opensearch_results = comparison_data.get('opensearch_results', {})
            # Get Legacy GDC results
            legacy_results = comparison_data.get('legacy_results', {})
            
            # Process each source
            all_sources = set(opensearch_results.keys()) | set(legacy_results.keys())
            
            for source in all_sources:
                opensearch_records = opensearch_results.get(source, [])
                legacy_records = legacy_results.get(source, [])
                
                # Create lookup for matching records
                legacy_by_id = {record.get("ID", ""): record for record in legacy_records}
                
                # Process OpenSearch records
                for opensearch_record in opensearch_records:
                    opensearch_id = opensearch_record.get("ID", "")
                    opensearch_name = opensearch_record.get("Full_Name", "") or opensearch_record.get("Entity_Name", "")
                    opensearch_schema = source.upper()
                    
                    # Find matching legacy record
                    legacy_record = legacy_by_id.get(opensearch_id)
                    if legacy_record:
                        legacy_name = legacy_record.get("Full_Name", "") or legacy_record.get("Entity_Name", "")
                        legacy_id = legacy_record.get("ID", "")
                        legacy_schema = source.upper()
                    else:
                        legacy_name = ""
                        legacy_id = ""
                        legacy_schema = ""
                    
                    unified_data.append({
                        "Test Key": test_key,
                        "Search Term": search_term,
                        "Type": type_label,
                        "OpenSearch Name": opensearch_name,
                        "OpenSearch ID": opensearch_id,
                        "OpenSearch Schema": opensearch_schema,
                        "Legacy Name": legacy_name,
                        "Legacy ID": legacy_id,
                        "Legacy Schema": legacy_schema
                    })
                
                # Process legacy-only records (not found in OpenSearch)
                opensearch_ids = {record.get("ID", "") for record in opensearch_records}
                for legacy_record in legacy_records:
                    legacy_id = legacy_record.get("ID", "")
                    if legacy_id not in opensearch_ids:
                        legacy_name = legacy_record.get("Full_Name", "") or legacy_record.get("Entity_Name", "")
                        legacy_schema = source.upper()
                        
                        unified_data.append({
                            "Test Key": test_key,
                            "Search Term": search_term,
                            "Type": type_label,
                            "OpenSearch Name": "",
                            "OpenSearch ID": "",
                            "OpenSearch Schema": "",
                            "Legacy Name": legacy_name,
                            "Legacy ID": legacy_id,
                            "Legacy Schema": legacy_schema
                        })
        
        # Create DataFrame and save to Excel
        if unified_data:
            df = pd.DataFrame(unified_data)
            
            # Sort by Test Key, then by OpenSearch Schema, then by OpenSearch ID
            df = df.sort_values(['Test Key', 'OpenSearch Schema', 'OpenSearch ID'])
            
            # Save to Excel
            excel_filename = os.path.join(config.results_directory, f"unified_opensearch_vs_legacy_comparison_{timestamp}.xlsx")
            df.to_excel(excel_filename, index=False, sheet_name='Unified Comparison')
            
            # Generate HTML report
            html_filename = os.path.join(config.results_directory, f"unified_opensearch_vs_legacy_comparison_{timestamp}.html")
            self.generate_html_report(df, html_filename)
            
            print(f"\n✅ Unified comparison reports generated:")
            print(f"  Excel: {excel_filename}")
            print(f"  HTML: {html_filename}")
            print(f"📊 Total comparison records: {len(unified_data)}")
            
            # Print summary statistics
            total_opensearch_records = len([r for r in unified_data if r['OpenSearch ID']])
            total_legacy_records = len([r for r in unified_data if r['Legacy ID']])
            matched_records = len([r for r in unified_data if r['OpenSearch ID'] and r['Legacy ID']])
            
            print(f"📈 Summary Statistics:")
            print(f"  OpenSearch records: {total_opensearch_records}")
            print(f"  Legacy GDC records: {total_legacy_records}")
            print(f"  Matched records: {matched_records}")
            print(f"  OpenSearch-only records: {total_opensearch_records - matched_records}")
            print(f"  Legacy-only records: {total_legacy_records - matched_records}")
            
            # Report skipped entities due to corrupted JSON
            if self.skipped_entities:
                print(f"\n⚠️  Skipped Entities (Corrupted JSON): {len(self.skipped_entities)}")
                for entity in self.skipped_entities[:10]:  # Show first 10
                    print(f"    - {entity}")
                if len(self.skipped_entities) > 10:
                    print(f"    ... and {len(self.skipped_entities) - 10} more")
            
            return excel_filename, html_filename
        else:
            print("❌ No comparison data available to generate report")
            return None, None
    
    def generate_html_report(self, df, filename):
        """
        Generate HTML report from DataFrame
        """
        try:
            # Create HTML content
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unified OpenSearch vs Legacy GDC Comparison Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .summary {{
            padding: 20px 30px;
            background-color: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        .summary h2 {{
            margin: 0 0 15px 0;
            color: #495057;
            font-size: 1.5em;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .table-container {{
            padding: 30px;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        th {{
            background-color: #495057;
            color: white;
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        td {{
            padding: 10px 8px;
            border-bottom: 1px solid #dee2e6;
            vertical-align: top;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e3f2fd;
        }}
        .type-person {{
            background-color: #e8f5e8;
            color: #2e7d32;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        .type-entity {{
            background-color: #e3f2fd;
            color: #1565c0;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        .schema-badge {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 500;
            margin: 1px;
        }}
        .schema-watch {{ background-color: #fff3cd; color: #856404; }}
        .schema-pep {{ background-color: #d1ecf1; color: #0c5460; }}
        .schema-sanction {{ background-color: #f8d7da; color: #721c24; }}
        .schema-icij {{ background-color: #d4edda; color: #155724; }}
        .schema-mex {{ background-color: #e2e3e5; color: #383d41; }}
        .schema-rights {{ background-color: #fce4ec; color: #c2185b; }}
        .schema-soe {{ background-color: #f3e5f5; color: #7b1fa2; }}
        .schema-col {{ background-color: #fff8e1; color: #f57f17; }}
        .schema-media {{ background-color: #e0f2f1; color: #00695c; }}
        .empty-cell {{
            color: #6c757d;
            font-style: italic;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
            text-align: center;
            min-width: 80px;
        }}
        .status-both {{
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .status-opensearch-only {{
            background-color: #cce5ff;
            color: #004085;
            border: 1px solid #b3d7ff;
        }}
        .status-legacy-only {{
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }}
        .footer {{
            padding: 20px 30px;
            background-color: #f8f9fa;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Unified OpenSearch vs Legacy GDC Comparison</h1>
            <p>Comprehensive Analysis Report - Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="summary">
            <h2>Summary Statistics</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(df)}</div>
                    <div class="stat-label">Total Records</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(df[df['OpenSearch ID'] != ''])}</div>
                    <div class="stat-label">OpenSearch Records</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(df[df['Legacy ID'] != ''])}</div>
                    <div class="stat-label">Legacy GDC Records</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(df[(df['OpenSearch ID'] != '') & (df['Legacy ID'] != '')])}</div>
                    <div class="stat-label">Matched Records</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(df[(df['OpenSearch ID'] != '') & (df['Legacy ID'] == '')])}</div>
                    <div class="stat-label">OpenSearch Only</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(df[(df['OpenSearch ID'] == '') & (df['Legacy ID'] != '')])}</div>
                    <div class="stat-label">Legacy Only</div>
                </div>
            </div>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Test Key</th>
                        <th>Search Term</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>OpenSearch Name</th>
                        <th>OpenSearch ID</th>
                        <th>OpenSearch Schema</th>
                        <th>Legacy Name</th>
                        <th>Legacy ID</th>
                        <th>Legacy Schema</th>
                    </tr>
                </thead>
                <tbody>
"""
            
            # Add table rows
            for _, row in df.iterrows():
                type_class = "type-person" if row['Type'] == 'Person' else "type-entity"
                opensearch_schema_class = f"schema-{row['OpenSearch Schema'].lower()}" if row['OpenSearch Schema'] else ""
                legacy_schema_class = f"schema-{row['Legacy Schema'].lower()}" if row['Legacy Schema'] else ""
                
                # Determine status
                has_opensearch = row['OpenSearch ID'] and row['OpenSearch ID'] != ''
                has_legacy = row['Legacy ID'] and row['Legacy ID'] != ''
                
                if has_opensearch and has_legacy:
                    status = "Present in Both"
                    status_class = "status-both"
                elif has_opensearch and not has_legacy:
                    status = "OpenSearch Only"
                    status_class = "status-opensearch-only"
                elif not has_opensearch and has_legacy:
                    status = "Legacy Only"
                    status_class = "status-legacy-only"
                else:
                    status = "Not Present"
                    status_class = "status-legacy-only"
                
                # Replace empty values with "Not Present"
                opensearch_name = row['OpenSearch Name'] if row['OpenSearch Name'] and row['OpenSearch Name'] != '' else 'Not Present'
                opensearch_id = row['OpenSearch ID'] if row['OpenSearch ID'] and row['OpenSearch ID'] != '' else 'Not Present'
                opensearch_schema = row['OpenSearch Schema'] if row['OpenSearch Schema'] and row['OpenSearch Schema'] != '' else 'Not Present'
                legacy_name = row['Legacy Name'] if row['Legacy Name'] and row['Legacy Name'] != '' else 'Not Present'
                legacy_id = row['Legacy ID'] if row['Legacy ID'] and row['Legacy ID'] != '' else 'Not Present'
                legacy_schema = row['Legacy Schema'] if row['Legacy Schema'] and row['Legacy Schema'] != '' else 'Not Present'
                
                html_content += f"""
                    <tr>
                        <td><strong>{row['Test Key']}</strong></td>
                        <td>{row['Search Term']}</td>
                        <td><span class="{type_class}">{row['Type']}</span></td>
                        <td><span class="status-badge {status_class}">{status}</span></td>
                        <td>{opensearch_name}</td>
                        <td>{opensearch_id}</td>
                        <td><span class="schema-badge {opensearch_schema_class}">{opensearch_schema}</span></td>
                        <td>{legacy_name}</td>
                        <td>{legacy_id}</td>
                        <td><span class="schema-badge {legacy_schema_class}">{legacy_schema}</span></td>
                    </tr>
"""
            
            html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Generated by GDC Automation Excel-Driven Regression Testing Framework</p>
            <p>This report compares OpenSearch API results with Legacy GDC system data</p>
        </div>
    </div>
</body>
</html>
"""
            
            # Write HTML file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        except Exception as e:
            print(f"Error generating HTML report: {e}")
    
    def generate_individual_reports(self, entity, comparison_result, main_folder=None):
        """
        Generate individual Excel and HTML reports for a single entity
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Use main folder if provided, otherwise create individual folder
        if main_folder:
            folder_path = main_folder
        else:
            folder_name = f"regression_test_{timestamp}"
            folder_path = f"results/{folder_name}"
            os.makedirs(folder_path, exist_ok=True)
        
        # Create safe filename from entity name
        safe_name = "".join(c for c in entity["name"] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')[:50]  # Limit length
        
        # Generate Excel report
        excel_filename = f"{folder_path}/{safe_name}_regression_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            # Create summary sheet
            summary_data = []
            for source, data in comparison_result["sources"].items():
                if data["baseline_count"] > 0 or data["current_count"] > 0:
                    summary_data.append({
                        "Source": source.upper(),
                        "Existing_GDC_Search_Count": data["baseline_count"],
                        "Current_OpenSearch_Count": data["current_count"],
                        "Common_Records": data["summary"]["exact_matches"] + data["summary"]["modified_records"],
                        "Uncommon_New_in_OpenSearch": data["summary"]["new_records"],
                        "Uncommon_Missing_from_OpenSearch": data["summary"]["missing_records"]
                    })
            
            # Always create summary sheet, even if empty
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
            else:
                # Create empty summary sheet
                summary_df = pd.DataFrame({
                    "Source": ["No Data"],
                    "Existing_GDC_Search_Count": [0],
                    "Current_OpenSearch_Count": [0],
                    "Common_Records": [0],
                    "Uncommon_New_in_OpenSearch": [0],
                    "Uncommon_Missing_from_OpenSearch": [0]
                })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Create "All Hits" sheet with combined data from all sources
            all_hits_data = []
            
            for source, data in comparison_result["sources"].items():
                if data["baseline_count"] == 0 and data["current_count"] == 0:
                    continue
                
                # Add matches (Common Ones)
                for record in data["matches"]:
                    status_text = "Common (Exact Match)" if record["status"] == "exact_match" else "Common (Modified)"
                    all_hits_data.append({
                        "Source": source.upper(),
                        "Status": status_text,
                        "Status_Order": 1,  # For sorting
                        "ID": record["ID"],
                        "Full_Name": record["Full_Name"],
                        "Other_Names": record["Other_Names"],
                        "Changes": "; ".join([f"{k}: {v['old']} -> {v['new']}" for k, v in record.get("changes", {}).items()])
                    })
                
                # Add new records (Uncommon - New in OpenSearch)
                for record in data["new_records"]:
                    all_hits_data.append({
                        "Source": source.upper(),
                        "Status": "Uncommon - New in OpenSearch",
                        "Status_Order": 2,  # For sorting
                        "ID": record["ID"],
                        "Full_Name": record["Full_Name"],
                        "Other_Names": record["Other_Names"],
                        "Changes": "New record in current OpenSearch"
                    })
                
                # Add missing records (Uncommon - Missing from OpenSearch)
                for record in data["missing_records"]:
                    all_hits_data.append({
                        "Source": source.upper(),
                        "Status": "Uncommon - Missing from OpenSearch",
                        "Status_Order": 2,  # For sorting
                        "ID": record["ID"],
                        "Full_Name": record["Full_Name"],
                        "Other_Names": record["Other_Names"],
                        "Changes": "Was in existing GDC search but missing from current OpenSearch"
                    })
            
            # Always create All Hits sheet, even if empty
            if all_hits_data:
                all_hits_df = pd.DataFrame(all_hits_data)
                all_hits_df = all_hits_df.sort_values(['Status_Order', 'Source', 'ID'])
                all_hits_df = all_hits_df.drop('Status_Order', axis=1)  # Remove sorting column
            else:
                # Create empty All Hits sheet
                all_hits_df = pd.DataFrame({
                    "Source": ["No Data"],
                    "Status": ["No Results"],
                    "ID": [""],
                    "Full_Name": [""],
                    "Other_Names": [""],
                    "Changes": ["No data available"]
                })
            all_hits_df.to_excel(writer, sheet_name='All Hits', index=False)
        
        # Generate HTML report
        html_filename = f"{folder_path}/{safe_name}_regression_{timestamp}.html"
        self.generate_entity_html_report(entity, comparison_result, html_filename)
        
        return excel_filename, html_filename
    
    def generate_entity_html_report(self, entity, comparison_result, filename):
        """
        Generate HTML report for a single entity
        """
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{entity['name']} (Type: {entity['type']}) Regression Test Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .summary-card {{ display: inline-block; margin: 10px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; min-width: 200px; }}
        .summary-names {{ font-size: 0.9em; color: #666; margin-top: 5px; }}
        .source-section {{ margin: 30px 0; }}
        .source-title {{ background-color: #e0e0e0; padding: 10px; font-weight: bold; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .status-common {{ background-color: #d4edda; }}
        .status-new {{ background-color: #cce5ff; }}
        .status-missing {{ background-color: #f8d7da; }}
        .badge {{ padding: 3px 8px; border-radius: 3px; font-size: 0.8em; font-weight: bold; }}
        .badge-common {{ background-color: #28a745; color: white; }}
        .badge-new {{ background-color: #007bff; color: white; }}
        .badge-missing {{ background-color: #dc3545; color: white; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{entity['name']} (Type: {entity['type']}) Regression Test Results</h1>
        <p><strong>Entity:</strong> {comparison_result['entity_name']}</p>
        <p><strong>Type:</strong> {entity['type']} ({'Entity' if entity['type'] == 'E' else 'Person'})</p>
        <p><strong>Test Time:</strong> {comparison_result['test_timestamp']}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
"""
        
        # Calculate totals
        total_common = 0
        total_new = 0
        total_missing = 0
        
        for source, data in comparison_result["sources"].items():
            total_common += data["summary"]["exact_matches"] + data["summary"]["modified_records"]
            total_new += data["summary"]["new_records"]
            total_missing += data["summary"]["missing_records"]
        
        # Add summary cards
        html_content += f"""
        <div class="summary-card">
            <h3>Common Records</h3>
            <div style="font-size: 2em; color: #28a745;">{total_common}</div>
            <div class="summary-names">Records found in both systems</div>
        </div>
        
        <div class="summary-card">
            <h3>Uncommon - New in OpenSearch</h3>
            <div style="font-size: 2em; color: #007bff;">{total_new}</div>
            <div class="summary-names">Records only in current OpenSearch</div>
        </div>
        
        <div class="summary-card">
            <h3>Uncommon - Missing from OpenSearch</h3>
            <div style="font-size: 2em; color: #dc3545;">{total_missing}</div>
            <div class="summary-names">Records only in existing GDC search</div>
        </div>
    </div>
"""
        
        # Add detailed sections for each source
        for source, data in comparison_result["sources"].items():
            if data["baseline_count"] == 0 and data["current_count"] == 0:
                continue
            
            html_content += f"""
    <div class="source-section">
        <div class="source-title">{source.upper()}</div>
        <p>Existing GDC Search: {data['baseline_count']} | Current OpenSearch: {data['current_count']}</p>
        
        <table>
            <thead>
                <tr>
                    <th>Status</th>
                    <th>ID</th>
                    <th>Full Name</th>
                    <th>Other Names</th>
                    <th>Changes</th>
                </tr>
            </thead>
            <tbody>
"""
            
            # Add matches
            for record in data["matches"]:
                status_class = "status-common"
                badge_class = "badge-common"
                status_text = "Common"
                changes_text = "No changes" if record["status"] == "exact_match" else "; ".join([f"{k}: {v['old']} -> {v['new']}" for k, v in record.get("changes", {}).items()])
                
                html_content += f"""
                <tr class="{status_class}">
                    <td><span class="badge {badge_class}">{status_text}</span></td>
                    <td>{record['ID']}</td>
                    <td>{record['Full_Name']}</td>
                    <td>{record['Other_Names']}</td>
                    <td>{changes_text}</td>
                </tr>
"""
            
            # Add new records
            for record in data["new_records"]:
                html_content += f"""
                <tr class="status-new">
                    <td><span class="badge badge-new">Uncommon - New in OpenSearch</span></td>
                    <td>{record['ID']}</td>
                    <td>{record['Full_Name']}</td>
                    <td>{record['Other_Names']}</td>
                    <td>New record in current OpenSearch</td>
                </tr>
"""
            
            # Add missing records
            for record in data["missing_records"]:
                html_content += f"""
                <tr class="status-missing">
                    <td><span class="badge badge-missing">Uncommon - Missing from OpenSearch</span></td>
                    <td>{record['ID']}</td>
                    <td>{record['Full_Name']}</td>
                    <td>{record['Other_Names']}</td>
                    <td>Was in existing GDC search but missing from current OpenSearch</td>
                </tr>
"""
            
            html_content += """
            </tbody>
        </table>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def print_entity_summary(self, entity, comparison_result):
        """Print summary to console for a single entity"""
        
        print(f"\n{'='*80}")
        print(f"{entity['name'].upper()} (TYPE: {entity['type']}) REGRESSION TEST RESULTS")
        print(f"{'='*80}")
        print(f"Entity: {comparison_result['entity_name']}")
        print(f"Type: {entity['type']} ({'Entity' if entity['type'] == 'E' else 'Person'})")
        print(f"Test Time: {comparison_result['test_timestamp']}")
        print(f"{'='*80}")
        
        total_exact = 0
        total_modified = 0
        total_new = 0
        total_missing = 0
        
        for source, data in comparison_result["sources"].items():
            if data["baseline_count"] == 0 and data["current_count"] == 0:
                continue
                
            print(f"\n{source.upper()}:")
            print(f"  Existing GDC Search Count: {data['baseline_count']}")
            print(f"  Current OpenSearch Count: {data['current_count']}")
            print(f"  Common Records: {data['summary']['exact_matches'] + data['summary']['modified_records']}")
            print(f"  Uncommon - New in OpenSearch: {data['summary']['new_records']}")
            print(f"  Uncommon - Missing from OpenSearch: {data['summary']['missing_records']}")
            
            total_exact += data['summary']['exact_matches']
            total_modified += data['summary']['modified_records']
            total_new += data['summary']['new_records']
            total_missing += data['summary']['missing_records']
            
            # Show details for changes
            if data['summary']['new_records'] > 0:
                print(f"  UNCOMMON - NEW IN OPENSEARCH:")
                for record in data['new_records']:
                    name = record['Full_Name'] if record['Full_Name'] else f"{record.get('First_Name', '')} {record.get('Last_Name', '')}".strip()
                    other_names = f" ({record['Other_Names']})" if record.get('Other_Names') else ""
                    print(f"    - {name}{other_names} (ID: {record['ID']})")
            
            if data['summary']['missing_records'] > 0:
                print(f"  UNCOMMON - MISSING FROM OPENSEARCH:")
                for record in data['missing_records']:
                    name = record['Full_Name'] if record['Full_Name'] else f"{record.get('First_Name', '')} {record.get('Last_Name', '')}".strip()
                    other_names = f" ({record['Other_Names']})" if record.get('Other_Names') else ""
                    print(f"    - {name}{other_names} (ID: {record['ID']})")
        
        print(f"\n{'='*80}")
        print(f"OVERALL SUMMARY:")
        print(f"  Total Common Records: {total_exact + total_modified}")
        print(f"  Total Uncommon - New in OpenSearch: {total_new}")
        print(f"  Total Uncommon - Missing from OpenSearch: {total_missing}")
        print(f"{'='*80}")
    
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
            
            # Print summary
            self.print_entity_summary(entity, comparison_result)
        
        # Generate unified comparison report
        print(f"\n{'='*80}")
        print("Generating unified comparison report...")
        excel_file, html_file = self.generate_unified_comparison_report()
        if excel_file and html_file:
            print(f"✅ Reports generated successfully!")
        print("All tests completed!")
    
    def generate_overall_summary(self, all_results, main_folder=None):
        """
        Generate an overall summary of all tests
        """
        print(f"\n{'='*80}")
        print("OVERALL TEST SUMMARY")
        print(f"{'='*80}")
        
        total_entities = len(all_results)
        total_common = 0
        total_new = 0
        total_missing = 0
        
        for result in all_results:
            comparison_result = result["comparison_result"]
            for source, data in comparison_result["sources"].items():
                total_common += data["summary"]["exact_matches"] + data["summary"]["modified_records"]
                total_new += data["summary"]["new_records"]
                total_missing += data["summary"]["missing_records"]
        
        print(f"Total Entities Tested: {total_entities}")
        print(f"Total Common Records: {total_common}")
        print(f"Total Uncommon - New in OpenSearch: {total_new}")
        print(f"Total Uncommon - Missing from OpenSearch: {total_missing}")
        print(f"{'='*80}")
        
        print("\nGenerated Reports:")
        for result in all_results:
            entity_name = result["entity"]["name"]
            print(f"  {entity_name}:")
            print(f"    Excel: {result['excel_file']}")
            print(f"    HTML: {result['html_file']}")

if __name__ == "__main__":
    # Run the Excel-driven regression test framework
    framework = ExcelDrivenRegressionTest()
    framework.run_all_tests()
