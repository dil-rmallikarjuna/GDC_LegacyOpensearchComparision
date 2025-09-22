#!/usr/bin/env python3
"""
Excel-Driven Regression Testing Framework
Reads entity data from Excel file and performs regression testing for each entity.
"""

import requests
import json
import pandas as pd
from datetime import datetime
import os
import hashlib

class ExcelDrivenRegressionTest:
    def __init__(self, excel_path="/Users/rmallikarjuna/Documents/GDC automation test/GDC Old System Result.xlsx"):
        self.excel_path = excel_path
        
        # API Configuration - Your actual AWS API Gateway endpoint
        self.api_config = {
            "url": "https://15krnwu233.execute-api.us-east-1.amazonaws.com/prod/search",
            "api_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJyZWFkLWNsaWVudCIsInJvbGUiOiJyZWFkIiwicGVybWlzc2lvbnMiOlsicmVhZCJdLCJleHAiOjE3NTc2NTYwMjAsImlhdCI6MTc1NzY1MjQyMCwiaXNzIjoiZ2RjLXNlYXJjaC1pZGVudGl0eS1zZXJ2aWNlIn0.71UeA_p0PQZBZymTAWshk9nJV0afSt_jM5fwW3QgtUo",
            "timeout": 30
        }
        
        # Ensure results directory exists
        os.makedirs("results", exist_ok=True)
    
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
                            gdc_data = json.loads(entity["current_gdc_response"])
                            entity["baseline_data"] = self.parse_gdc_response(gdc_data)
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
    
    def parse_gdc_response(self, gdc_data):
        """
        Parse GDC response JSON to extract baseline data
        """
        baseline_data = {
            "watch": [],
            "icij": [],
            "mex": [],
            "rights": [],
            "pep": [],
            "sanction": [],
            "soe": [],
            "col": [],
            "media": [],
            "ofac": []
        }
        
        try:
            # Navigate through the GDC response structure
            if "Args" in gdc_data and len(gdc_data["Args"]) > 0:
                args = gdc_data["Args"][0]
                if "nameSearch" in args and "Preview" in args["nameSearch"]:
                    preview = args["nameSearch"]["Preview"]
                    
                    # Extract data from each source
                    for source, records in preview.items():
                        if source.lower() in baseline_data and isinstance(records, list):
                            for record in records:
                                # Normalize the record structure
                                normalized_record = {
                                    "recid": record.get("recid", 0),
                                    "ID": record.get("ID", ""),
                                    "First_Name": record.get("First_Name", ""),
                                    "Last_Name": record.get("Last_Name", ""),
                                    "Full_Name": record.get("Full_Name", ""),
                                    "Other_Names": record.get("Other_Names", ""),
                                    "AltScript": record.get("AltScript", ""),
                                    "RecType": record.get("RecType", "")
                                }
                                baseline_data[source.lower()].append(normalized_record)
            
        except Exception as e:
            print(f"Error parsing GDC response structure: {e}")
        
        return baseline_data
    
    def fetch_current_data(self, entity_name, entity_type):
        """
        Fetch current data from OpenSearch API
        """
        
        # Use configured API settings
        api_url = self.api_config["url"]
        api_key = self.api_config["api_key"]
        
        # Determine RecType based on entity type
        rec_type = "E" if entity_type == "E" else "P"
        
        # Payload for OpenSearch API call
        payload = {
            "query": entity_name,
            "schemas": ["col", "rights", "mex", "watch", "soe", "pep", "sanctions"],
            "limit": 100,
            "search_types": ["keyword", "phonetic", "similarity"]
        }
        
        # Note: RecType filtering will be handled in post-processing if needed
        # The API doesn't seem to support RecType parameter directly
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add authorization header if API key is provided
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        try:
            print(f"Calling OpenSearch API for {entity_name} (Type: {entity_type})...")
            print(f"Payload: {payload}")
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=self.api_config["timeout"])
            response.raise_for_status()
            
            api_result = response.json()
            print(f"API Response received successfully")
            
            # Transform API response to match our expected format
            return self.transform_opensearch_response(api_result)
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling OpenSearch API: {e}")
            print("Returning empty data...")
            
            # Return empty data structure if API call fails
            return {
                "watch": [],
                "icij": [],
                "mex": [],
                "rights": [],
                "pep": [],
                "sanction": [],
                "soe": [],
                "col": [],
                "media": [],
                "ofac": []
            }
        
        except Exception as e:
            print(f"Error processing API response: {e}")
            return None
    
    def transform_opensearch_response(self, api_response):
        """
        Transform OpenSearch API response to match our expected format
        """
        
        try:
            print(f"Raw API response keys: {list(api_response.keys()) if isinstance(api_response, dict) else type(api_response)}")
            
            # Initialize transformed data structure
            transformed_data = {
                "watch": [],
                "icij": [],
                "mex": [],
                "rights": [],
                "pep": [],
                "sanction": [],
                "soe": [],
                "col": [],
                "media": [],
                "ofac": []
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
        self.generate_html_report(entity, comparison_result, html_filename)
        
        return excel_filename, html_filename
    
    def generate_html_report(self, entity, comparison_result, filename):
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
        print("Excel-Driven Regression Testing Framework")
        print("=" * 80)
        
        # Create main test run folder with timestamp
        run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        main_folder = f"results/regression_test_run_{run_timestamp}"
        os.makedirs(main_folder, exist_ok=True)
        print(f"Results will be saved to: {main_folder}")
        print()
        
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
            
            # Generate individual reports
            excel_file, html_file = self.generate_individual_reports(entity, comparison_result, main_folder)
            
            # Print summary
            self.print_entity_summary(entity, comparison_result)
            
            print(f"\nReports generated for {entity['name']}:")
            print(f"  Excel: {excel_file}")
            print(f"  HTML: {html_file}")
            
            # Store results for summary
            all_results.append({
                "entity": entity,
                "comparison_result": comparison_result,
                "excel_file": excel_file,
                "html_file": html_file
            })
        
        # Generate overall summary
        self.generate_overall_summary(all_results, main_folder)
    
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
