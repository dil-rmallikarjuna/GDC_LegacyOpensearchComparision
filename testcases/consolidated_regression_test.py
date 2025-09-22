#!/usr/bin/env python3
"""
Consolidated Regression Testing Framework
Generates a single Excel and HTML report with different sheets/sections for each entity.
"""

import requests
import json
import pandas as pd
from datetime import datetime
import os
import hashlib
import html

class ConsolidatedRegressionTest:
    def __init__(self, excel_path="/Users/rmallikarjuna/Documents/GDC automation test/GDC Old System Result.xlsx"):
        self.excel_path = excel_path
        
        # API Configuration - Your actual AWS API Gateway endpoint
        self.api_config = {
            "url": "https://15krnwu233.execute-api.us-east-1.amazonaws.com/prod/search",
            "api_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJyZWFkLWNsaWVudCIsInJvbGUiOiJyZWFkIiwicGVybWlzc2lvbnMiOlsicmVhZCJdLCJleHAiOjE3NTgwODcyMzIsImlhdCI6MTc1ODA4MzYzMiwiaXNzIjoiZ2RjLXNlYXJjaC1pZGVudGl0eS1zZXJ2aWNlIn0.8-ffozf_8N1AmiWMgyG1y321K94EzKR_vyQ9VdhqcRM",
            "timeout": 30
        }
        
        # Ensure results directory exists
        os.makedirs("results", exist_ok=True)
        
        # Store all results for consolidated reporting
        self.all_results = []
    
    def html_escape(self, text):
        """
        Properly escape text for HTML to handle Unicode characters
        """
        if not text:
            return ""
        return html.escape(str(text))
    
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
        
        # Payload for OpenSearch API call
        payload = {
            "query": entity_name,
            "schemas": ["col", "rights", "mex", "watch", "soe", "pep", "sanction"],
            "limit": 100,
            "search_types": ["keyword", "phonetic", "similarity"]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add authorization header if API key is provided
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        try:
            print(f"Calling OpenSearch API for {entity_name} (Type: {entity_type})...")
            
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
        Compare baseline data with current API data and determine test pass/fail
        """
        comparison_result = {
            "entity_name": entity_name,
            "test_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "test_status": "PASS",  # Will be set to FAIL if conditions are met
            "failure_reasons": [],
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
        
        # Check for test failure conditions with refined logic
        total_baseline = sum(source_data["baseline_count"] for source_data in comparison_result["sources"].values())
        
        # Failure Condition 1: Missing RELEVANT records (OpenSearch doesn't have entries from GDC that match the searched entity)
        relevant_missing_records = self.validate_missing_record_relevance(entity_name, baseline_data, comparison_result)
        if relevant_missing_records:
            comparison_result["test_status"] = "FAIL"
            comparison_result["failure_reasons"].append(f"Missing {len(relevant_missing_records)} relevant records in OpenSearch that exist in GDC")
            comparison_result["relevant_missing_records"] = relevant_missing_records
        
        # Failure Condition 2: Check if returned entities match searched entity (irrelevant results)
        incorrect_entities = self.validate_entity_relevance(entity_name, current_data)
        if incorrect_entities:
            comparison_result["test_status"] = "FAIL"
            comparison_result["failure_reasons"].append(f"OpenSearch returned {len(incorrect_entities)} irrelevant entities")
            comparison_result["incorrect_entities"] = incorrect_entities
        
        # Add overall test summary
        total_missing = sum(len(source_data["missing_records"]) for source_data in comparison_result["sources"].values())
        comparison_result["test_summary"] = {
            "total_baseline_records": total_baseline,
            "total_missing_records": total_missing,
            "total_relevant_missing_records": len(relevant_missing_records) if relevant_missing_records else 0,
            "total_common_records": sum(len(source_data["matches"]) for source_data in comparison_result["sources"].values()),
            "total_new_records": sum(len(source_data["new_records"]) for source_data in comparison_result["sources"].values())
        }
        
        return comparison_result
    
    def validate_missing_record_relevance(self, entity_name, baseline_data, comparison_result):
        """
        Validate if missing records from GDC are actually relevant to the searched entity
        Returns list of relevant missing records
        """
        relevant_missing = []
        entity_name_lower = entity_name.lower()
        
        # Split entity name into key words for matching
        entity_words = set(word.strip().lower() for word in entity_name_lower.replace(",", " ").split() if len(word.strip()) > 2)
        
        # Define common location/generic words that shouldn't count as strong matches
        generic_words = {'national', 'international', 'global', 'company', 'ltd', 'llc', 'inc', 'corp', 
                        'limited', 'corporation', 'group', 'holdings', 'the', 'and', 'of', 'for',
                        'dubai', 'emirates', 'saudi', 'china', 'russia', 'america', 'united', 'states'}
        
        for source, source_data in comparison_result["sources"].items():
            missing_records = source_data.get("missing_records", [])
            
            for record in missing_records:
                full_name = record.get("Full_Name", "").lower()
                first_name = record.get("First_Name", "").lower()
                last_name = record.get("Last_Name", "").lower()
                other_names = record.get("Other_Names", "").lower()
                
                # Combine all name fields for checking
                all_names = f"{full_name} {first_name} {last_name} {other_names}".strip()
                record_words = set(word.strip().lower() for word in all_names.replace(",", " ").split() if len(word.strip()) > 2)
                
                # Check if there's significant overlap between searched entity and missing record
                if entity_words and record_words:
                    # Calculate overlap excluding generic words
                    entity_specific_words = entity_words - generic_words
                    record_specific_words = record_words - generic_words
                    
                    # If no specific words remain, fall back to all words
                    if not entity_specific_words:
                        entity_specific_words = entity_words
                    if not record_specific_words:
                        record_specific_words = record_words
                    
                    specific_overlap = len(entity_specific_words.intersection(record_specific_words))
                    generic_overlap = len(entity_words.intersection(record_words)) - specific_overlap
                    
                    # Calculate weighted overlap (specific words count more)
                    if entity_specific_words:
                        specific_ratio = specific_overlap / len(entity_specific_words)
                    else:
                        specific_ratio = 0
                    
                    # For relevance, we need either:
                    # 1. High specific word overlap (≥50%), OR  
                    # 2. Perfect match of ALL entity words (100% including generic)
                    total_overlap_ratio = len(entity_words.intersection(record_words)) / len(entity_words)
                    
                    is_relevant = (specific_ratio >= 0.5) or (total_overlap_ratio >= 0.99)
                    
                    if is_relevant:
                        relevant_missing.append({
                            "source": source,
                            "record_id": record.get("ID", ""),
                            "full_name": record.get("Full_Name", ""),
                            "first_name": record.get("First_Name", ""),
                            "last_name": record.get("Last_Name", ""),
                            "other_names": record.get("Other_Names", ""),
                            "overlap_ratio": total_overlap_ratio,
                            "specific_overlap_ratio": specific_ratio,
                            "searched_entity": entity_name
                        })
        
        return relevant_missing
    
    def validate_entity_relevance(self, entity_name, current_data):
        """
        Validate if returned entities are relevant to the searched entity
        Returns list of irrelevant entities
        """
        irrelevant_entities = []
        entity_name_lower = entity_name.lower()
        
        # Split entity name into key words for matching
        entity_words = set(word.strip().lower() for word in entity_name_lower.replace(",", " ").split() if len(word.strip()) > 2)
        
        for source, records in current_data.items():
            for record in records:
                full_name = record.get("Full_Name", "").lower()
                first_name = record.get("First_Name", "").lower()
                last_name = record.get("Last_Name", "").lower()
                other_names = record.get("Other_Names", "").lower()
                
                # Combine all name fields for checking
                all_names = f"{full_name} {first_name} {last_name} {other_names}".strip()
                record_words = set(word.strip().lower() for word in all_names.replace(",", " ").split() if len(word.strip()) > 2)
                
                # Check if there's significant overlap between searched entity and returned entity
                if entity_words and record_words:
                    overlap = len(entity_words.intersection(record_words))
                    overlap_ratio = overlap / len(entity_words)
                    
                    # More sophisticated matching:
                    # - For single word searches (like "RBI"), be more lenient (20% threshold)
                    # - For multi-word searches, require higher overlap (40% threshold)
                    threshold = 0.2 if len(entity_words) == 1 else 0.4
                    
                    # Also check reverse overlap (what percentage of record words match entity words)
                    reverse_overlap_ratio = overlap / len(record_words) if record_words else 0
                    
                    # Consider it relevant if either direction has good overlap
                    is_relevant = (overlap_ratio >= threshold) or (reverse_overlap_ratio >= threshold)
                    
                    if not is_relevant:
                        irrelevant_entities.append({
                            "source": source,
                            "record_id": record.get("ID", ""),
                            "full_name": record.get("Full_Name", ""),
                            "first_name": record.get("First_Name", ""),
                            "last_name": record.get("Last_Name", ""),
                            "other_names": record.get("Other_Names", ""),
                            "overlap_ratio": overlap_ratio,
                            "reverse_overlap_ratio": reverse_overlap_ratio,
                            "searched_entity": entity_name
                        })
        
        return irrelevant_entities
    
    def generate_consolidated_reports(self):
        """
        Generate consolidated Excel and HTML reports for all entities
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate consolidated Excel report
        excel_filename = f"results/consolidated_regression_report_{timestamp}.xlsx"
        self.generate_consolidated_excel_report(excel_filename)
        
        # Generate consolidated HTML report
        html_filename = f"results/consolidated_regression_report_{timestamp}.html"
        self.generate_consolidated_html_report(html_filename)
        
        return excel_filename, html_filename
    
    def generate_consolidated_excel_report(self, filename):
        """
        Generate consolidated Excel report with sheets for each entity
        """
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Create overall summary sheet
            self.create_overall_summary_sheet(writer)
            
            # Create comprehensive "All Hits" sheet with every record from GDC + OpenSearch
            self.create_all_hits_consolidated_sheet(writer)
            
            # Create entity summary sheet
            self.create_entity_summary_sheet(writer)
            
            # Create individual sheets for each entity
            for result in self.all_results:
                entity = result["entity"]
                comparison_result = result["comparison_result"]
                
                # Create safe sheet name
                safe_name = "".join(c for c in entity["name"] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_name = safe_name.replace(' ', '_')[:31]  # Excel sheet name limit
                
                self.create_entity_sheet(writer, entity, comparison_result, safe_name)
    
    def create_overall_summary_sheet(self, writer):
        """
        Create overall summary sheet with totals across all entities
        """
        summary_data = []
        
        # Calculate totals by entity type
        entity_totals = {"E": {"entities": 0, "passed": 0, "failed": 0, "common": 0, "new": 0, "missing": 0}, 
                        "P": {"entities": 0, "passed": 0, "failed": 0, "common": 0, "new": 0, "missing": 0}}
        
        for result in self.all_results:
            entity = result["entity"]
            comparison_result = result["comparison_result"]
            entity_type = entity["type"]
            
            entity_totals[entity_type]["entities"] += 1
            
            # Track test status
            test_status = comparison_result.get("test_status", "UNKNOWN")
            if test_status == "PASS":
                entity_totals[entity_type]["passed"] += 1
            elif test_status == "FAIL":
                entity_totals[entity_type]["failed"] += 1
            
            for source, data in comparison_result["sources"].items():
                entity_totals[entity_type]["common"] += data["summary"]["exact_matches"] + data["summary"]["modified_records"]
                entity_totals[entity_type]["new"] += data["summary"]["new_records"]
                entity_totals[entity_type]["missing"] += data["summary"]["missing_records"]
        
        # Create summary rows
        for entity_type, totals in entity_totals.items():
            if totals["entities"] > 0:
                summary_data.append({
                    "Entity_Type": "Entities" if entity_type == "E" else "Persons",
                    "Total_Entities_Tested": totals["entities"],
                    "Tests_Passed": totals["passed"],
                    "Tests_Failed": totals["failed"],
                    "Pass_Rate": f"{(totals['passed']/totals['entities']*100):.1f}%" if totals["entities"] > 0 else "0%",
                    "Total_Common_Records": totals["common"],
                    "Total_New_in_OpenSearch": totals["new"],
                    "Total_Missing_from_OpenSearch": totals["missing"],
                    "Total_Records": totals["common"] + totals["new"] + totals["missing"]
                })
        
        # Add grand total
        total_entities = sum(t["entities"] for t in entity_totals.values())
        total_passed = sum(t["passed"] for t in entity_totals.values())
        total_failed = sum(t["failed"] for t in entity_totals.values())
        
        grand_total = {
            "Entity_Type": "GRAND TOTAL",
            "Total_Entities_Tested": total_entities,
            "Tests_Passed": total_passed,
            "Tests_Failed": total_failed,
            "Pass_Rate": f"{(total_passed/total_entities*100):.1f}%" if total_entities > 0 else "0%",
            "Total_Common_Records": sum(t["common"] for t in entity_totals.values()),
            "Total_New_in_OpenSearch": sum(t["new"] for t in entity_totals.values()),
            "Total_Missing_from_OpenSearch": sum(t["missing"] for t in entity_totals.values()),
            "Total_Records": sum(t["common"] + t["new"] + t["missing"] for t in entity_totals.values())
        }
        summary_data.append(grand_total)
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Overall Summary', index=False)
    
    def create_all_hits_consolidated_sheet(self, writer):
        """
        Create comprehensive "All Hits" sheet with every record from GDC + OpenSearch
        """
        all_hits_data = []
        
        for result in self.all_results:
            entity = result["entity"]
            comparison_result = result["comparison_result"]
            
            for source, data in comparison_result["sources"].items():
                if data["baseline_count"] == 0 and data["current_count"] == 0:
                    continue
                
                # Add common records (found in both GDC and OpenSearch)
                for record in data["matches"]:
                    status_text = "Common - Found in Both Systems"
                    all_hits_data.append({
                        "Entity_Name": entity["name"],
                        "Entity_Type": "Entity" if entity["type"] == "E" else "Person",
                        "Source": source.upper(),
                        "Status": status_text,
                        "Status_Order": 1,  # For sorting - Common first
                        "ID": record["ID"],
                        "Full_Name": record["Full_Name"],
                        "Other_Names": record["Other_Names"],
                        "In_Existing_GDC": "✓ Yes",
                        "In_Current_OpenSearch": "✓ Yes",
                        "Changes": "; ".join([f"{k}: {v['old']} -> {v['new']}" for k, v in record.get("changes", {}).items()]) or "No changes"
                    })
                
                # Add records missing from OpenSearch (only in existing GDC)
                for record in data["missing_records"]:
                    all_hits_data.append({
                        "Entity_Name": entity["name"],
                        "Entity_Type": "Entity" if entity["type"] == "E" else "Person",
                        "Source": source.upper(),
                        "Status": "Missing from OpenSearch",
                        "Status_Order": 2,  # For sorting
                        "ID": record["ID"],
                        "Full_Name": record["Full_Name"],
                        "Other_Names": record["Other_Names"],
                        "In_Existing_GDC": "✓ Yes",
                        "In_Current_OpenSearch": "✗ No",
                        "Changes": "Was in existing GDC search but missing from current OpenSearch"
                    })
                
                # Add records missing from existing GDC (only in OpenSearch)
                for record in data["new_records"]:
                    all_hits_data.append({
                        "Entity_Name": entity["name"],
                        "Entity_Type": "Entity" if entity["type"] == "E" else "Person",
                        "Source": source.upper(),
                        "Status": "Missing from Existing GDC",
                        "Status_Order": 3,  # For sorting
                        "ID": record["ID"],
                        "Full_Name": record["Full_Name"],
                        "Other_Names": record["Other_Names"],
                        "In_Existing_GDC": "✗ No",
                        "In_Current_OpenSearch": "✓ Yes",
                        "Changes": "New record in current OpenSearch, not found in existing GDC"
                    })
        
        # Create comprehensive All Hits sheet
        if all_hits_data:
            all_hits_df = pd.DataFrame(all_hits_data)
            # Sort by Status (Common first), then Entity Type, then Entity Name, then Source, then ID
            all_hits_df = all_hits_df.sort_values(['Status_Order', 'Entity_Type', 'Entity_Name', 'Source', 'ID'])
            # Remove sorting column before saving
            all_hits_df = all_hits_df.drop('Status_Order', axis=1)
            all_hits_df.to_excel(writer, sheet_name='All Hits - Comprehensive', index=False)
        else:
            # Create empty sheet if no data
            empty_df = pd.DataFrame({
                "Entity_Name": ["No Data"],
                "Entity_Type": [""],
                "Source": [""],
                "Status": ["No records found"],
                "ID": [""],
                "Full_Name": [""],
                "Other_Names": [""],
                "In_Existing_GDC": [""],
                "In_Current_OpenSearch": [""],
                "Changes": ["No data available"]
            })
            empty_df.to_excel(writer, sheet_name='All Hits - Comprehensive', index=False)
    
    def create_entity_summary_sheet(self, writer):
        """
        Create entity summary sheet with one row per entity
        """
        entity_summary_data = []
        
        for result in self.all_results:
            entity = result["entity"]
            comparison_result = result["comparison_result"]
            
            # Calculate totals for this entity
            total_common = 0
            total_new = 0
            total_missing = 0
            
            for source, data in comparison_result["sources"].items():
                total_common += data["summary"]["exact_matches"] + data["summary"]["modified_records"]
                total_new += data["summary"]["new_records"]
                total_missing += data["summary"]["missing_records"]
            
            test_status = comparison_result.get("test_status", "UNKNOWN")
            status_emoji = "✅ PASS" if test_status == "PASS" else "❌ FAIL" if test_status == "FAIL" else "❓ UNKNOWN"
            
            # Get failure reasons if any
            failure_reasons = "; ".join(comparison_result.get("failure_reasons", [])) if test_status == "FAIL" else ""
            
            entity_summary_data.append({
                "Entity_Name": entity["name"],
                "Entity_Type": "Entity" if entity["type"] == "E" else "Person",
                "Test_Status": status_emoji,
                "Failure_Reasons": failure_reasons,
                "Common_Records": total_common,
                "New_in_OpenSearch": total_new,
                "Missing_from_OpenSearch": total_missing,
                "Total_Records": total_common + total_new + total_missing
            })
        
        if entity_summary_data:
            entity_df = pd.DataFrame(entity_summary_data)
            entity_df = entity_df.sort_values(['Entity_Type', 'Entity_Name'])
            entity_df.to_excel(writer, sheet_name='Entity Summary', index=False)
    
    def create_entity_sheet(self, writer, entity, comparison_result, sheet_name):
        """
        Create individual sheet for each entity
        """
        all_records_data = []
        
        for source, data in comparison_result["sources"].items():
            if data["baseline_count"] == 0 and data["current_count"] == 0:
                continue
            
            # Add matches (Common Records)
            for record in data["matches"]:
                status_text = "Common (Exact Match)" if record["status"] == "exact_match" else "Common (Modified)"
                all_records_data.append({
                    "Source": source.upper(),
                    "Status": status_text,
                    "Status_Order": 1,  # For sorting
                    "ID": record["ID"],
                    "Full_Name": record["Full_Name"],
                    "Other_Names": record["Other_Names"],
                    "Changes": "; ".join([f"{k}: {v['old']} -> {v['new']}" for k, v in record.get("changes", {}).items()]) or "No changes"
                })
            
            # Add new records
            for record in data["new_records"]:
                all_records_data.append({
                    "Source": source.upper(),
                    "Status": "Uncommon - New in OpenSearch",
                    "Status_Order": 2,
                    "ID": record["ID"],
                    "Full_Name": record["Full_Name"],
                    "Other_Names": record["Other_Names"],
                    "Changes": "New record in current OpenSearch"
                })
            
            # Add missing records
            for record in data["missing_records"]:
                all_records_data.append({
                    "Source": source.upper(),
                    "Status": "Uncommon - Missing from OpenSearch",
                    "Status_Order": 2,
                    "ID": record["ID"],
                    "Full_Name": record["Full_Name"],
                    "Other_Names": record["Other_Names"],
                    "Changes": "Was in existing GDC search but missing from current OpenSearch"
                })
        
        # Create sheet with data or placeholder
        if all_records_data:
            entity_df = pd.DataFrame(all_records_data)
            entity_df = entity_df.sort_values(['Status_Order', 'Source', 'ID'])
            entity_df = entity_df.drop('Status_Order', axis=1)
        else:
            entity_df = pd.DataFrame({
                "Source": ["No Data"],
                "Status": ["No Results"],
                "ID": [""],
                "Full_Name": [""],
                "Other_Names": [""],
                "Changes": ["No data available for this entity"]
            })
        
        entity_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    def generate_consolidated_html_report(self, filename):
        """
        Generate consolidated HTML report with sections for each entity
        """
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consolidated Regression Test Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .overall-summary {{ margin: 20px 0; }}
        .summary-card {{ display: inline-block; margin: 10px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; min-width: 200px; }}
        .entity-section {{ margin: 30px 0; border: 1px solid #ddd; border-radius: 5px; }}
        .entity-header {{ background-color: #e0e0e0; padding: 15px; font-weight: bold; font-size: 1.2em; }}
        .entity-content {{ padding: 15px; }}
        .source-section {{ margin: 20px 0; }}
        .source-title {{ background-color: #f5f5f5; padding: 10px; font-weight: bold; }}
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
        .test-pass {{ background-color: #d4edda; color: #155724; }}
        .test-fail {{ background-color: #f8d7da; color: #721c24; }}
        .failure-reasons {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 10px 0; }}
        .irrelevant-entities {{ background-color: #e2e3e5; border-left: 4px solid #6c757d; padding: 10px; margin: 10px 0; }}
        .toc {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .toc ul {{ list-style-type: none; padding-left: 0; }}
        .toc li {{ margin: 5px 0; }}
        .toc a {{ text-decoration: none; color: #007bff; }}
        .toc a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Consolidated Regression Test Results</h1>
        <p><strong>Test Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>Total Entities Tested:</strong> {len(self.all_results)}</p>
    </div>
"""
        
        # Calculate overall totals
        total_common = 0
        total_new = 0
        total_missing = 0
        
        for result in self.all_results:
            comparison_result = result["comparison_result"]
            for source, data in comparison_result["sources"].items():
                total_common += data["summary"]["exact_matches"] + data["summary"]["modified_records"]
                total_new += data["summary"]["new_records"]
                total_missing += data["summary"]["missing_records"]
        
        # Add overall summary
        html_content += f"""
    <div class="overall-summary">
        <h2>Overall Summary</h2>
        <div class="summary-card">
            <h3>Common Records</h3>
            <div style="font-size: 2em; color: #28a745;">{total_common}</div>
            <div>Records found in both systems</div>
        </div>
        
        <div class="summary-card">
            <h3>New in OpenSearch</h3>
            <div style="font-size: 2em; color: #007bff;">{total_new}</div>
            <div>Records only in current OpenSearch</div>
        </div>
        
        <div class="summary-card">
            <h3>Missing from OpenSearch</h3>
            <div style="font-size: 2em; color: #dc3545;">{total_missing}</div>
            <div>Records only in existing GDC search</div>
        </div>
    </div>
"""
        
        # Add table of contents
        html_content += """
    <div class="toc">
        <h2>Table of Contents</h2>
        <ul>
"""
        
        for i, result in enumerate(self.all_results):
            entity = result["entity"]
            entity_type = "Entity" if entity["type"] == "E" else "Person"
            html_content += f'            <li><a href="#entity_{i}">{self.html_escape(entity["name"])} ({entity_type})</a></li>\n'
        
        html_content += """
        </ul>
    </div>
"""
        
        # Add individual entity sections
        for i, result in enumerate(self.all_results):
            entity = result["entity"]
            comparison_result = result["comparison_result"]
            entity_type = "Entity" if entity["type"] == "E" else "Person"
            
            # Calculate entity totals
            entity_common = 0
            entity_new = 0
            entity_missing = 0
            
            for source, data in comparison_result["sources"].items():
                entity_common += data["summary"]["exact_matches"] + data["summary"]["modified_records"]
                entity_new += data["summary"]["new_records"]
                entity_missing += data["summary"]["missing_records"]
            
            test_status = comparison_result.get("test_status", "UNKNOWN")
            status_class = "test-pass" if test_status == "PASS" else "test-fail"
            status_emoji = "✅" if test_status == "PASS" else "❌"
            
            html_content += f"""
    <div class="entity-section" id="entity_{i}">
        <div class="entity-header {status_class}">
            {self.html_escape(entity["name"])} ({entity_type}) - {status_emoji} {test_status}
        </div>
        <div class="entity-content">
            <p><strong>Summary:</strong> {entity_common} Common, {entity_new} New in OpenSearch, {entity_missing} Missing from OpenSearch</p>
"""
            
            # Add failure reasons if test failed
            if test_status == "FAIL" and comparison_result.get("failure_reasons"):
                html_content += """
            <div class="failure-reasons">
                <h4>❌ Test Failure Reasons:</h4>
                <ul>
"""
                for reason in comparison_result["failure_reasons"]:
                    html_content += f"                    <li>{self.html_escape(reason)}</li>\n"
                html_content += """
                </ul>
            </div>
"""
            
            # Add relevant missing records if any
            if comparison_result.get("relevant_missing_records"):
                html_content += """
            <div class="irrelevant-entities">
                <h4>🔍 Relevant Missing Records:</h4>
                <table>
                    <tr><th>Source</th><th>ID</th><th>Name</th><th>Match %</th></tr>
"""
                for missing_info in comparison_result["relevant_missing_records"][:10]:  # Show first 10
                    html_content += f"""
                    <tr>
                        <td>{self.html_escape(missing_info['source'])}</td>
                        <td>{self.html_escape(missing_info['record_id'])}</td>
                        <td>{self.html_escape(missing_info['full_name'])}</td>
                        <td>{missing_info['overlap_ratio']:.1%}</td>
                    </tr>
"""
                html_content += """
                </table>
            </div>
"""

            # Add irrelevant entities if any
            if comparison_result.get("incorrect_entities"):
                html_content += """
            <div class="irrelevant-entities">
                <h4>⚠️ Irrelevant Entities Found:</h4>
                <table>
                    <tr><th>Source</th><th>ID</th><th>Name</th><th>Forward Match %</th><th>Reverse Match %</th></tr>
"""
                for entity_info in comparison_result["incorrect_entities"][:10]:  # Show first 10
                    html_content += f"""
                    <tr>
                        <td>{self.html_escape(entity_info['source'])}</td>
                        <td>{self.html_escape(entity_info['record_id'])}</td>
                        <td>{self.html_escape(entity_info['full_name'])}</td>
                        <td>{entity_info['overlap_ratio']:.1%}</td>
                        <td>{entity_info.get('reverse_overlap_ratio', 0):.1%}</td>
                    </tr>
"""
                html_content += """
                </table>
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
                            <td>{self.html_escape(record['ID'])}</td>
                            <td>{self.html_escape(record['Full_Name'])}</td>
                            <td>{self.html_escape(record['Other_Names'])}</td>
                            <td>{self.html_escape(changes_text)}</td>
                        </tr>
"""
                
                # Add new records
                for record in data["new_records"]:
                    html_content += f"""
                        <tr class="status-new">
                            <td><span class="badge badge-new">New in OpenSearch</span></td>
                            <td>{self.html_escape(record['ID'])}</td>
                            <td>{self.html_escape(record['Full_Name'])}</td>
                            <td>{self.html_escape(record['Other_Names'])}</td>
                            <td>New record in current OpenSearch</td>
                        </tr>
"""
                
                # Add missing records
                for record in data["missing_records"]:
                    html_content += f"""
                        <tr class="status-missing">
                            <td><span class="badge badge-missing">Missing from OpenSearch</span></td>
                            <td>{self.html_escape(record['ID'])}</td>
                            <td>{self.html_escape(record['Full_Name'])}</td>
                            <td>{self.html_escape(record['Other_Names'])}</td>
                            <td>Was in existing GDC search but missing from current OpenSearch</td>
                        </tr>
"""
                
                html_content += """
                    </tbody>
                </table>
            </div>
"""
            
            html_content += """
        </div>
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
        
        test_status = comparison_result.get("test_status", "UNKNOWN")
        status_emoji = "✅" if test_status == "PASS" else "❌"
        
        print(f"\n[{entity['name']}] Processing completed - {status_emoji} {test_status}")
        
        total_common = 0
        total_new = 0
        total_missing = 0
        
        for source, data in comparison_result["sources"].items():
            if data["baseline_count"] > 0 or data["current_count"] > 0:
                total_common += data["summary"]["exact_matches"] + data["summary"]["modified_records"]
                total_new += data["summary"]["new_records"]
                total_missing += data["summary"]["missing_records"]
        
        print(f"  Summary: {total_common} Common, {total_new} New, {total_missing} Missing")
        
        # Print failure reasons if test failed
        if test_status == "FAIL" and comparison_result.get("failure_reasons"):
            print(f"  ❌ Failure Reasons:")
            for reason in comparison_result["failure_reasons"]:
                print(f"    • {reason}")
        
        # Print relevant missing records if any
        if comparison_result.get("relevant_missing_records"):
            print(f"  🔍 Relevant Missing Records:")
            for missing_info in comparison_result["relevant_missing_records"][:3]:  # Show first 3
                print(f"    • {missing_info['full_name']} (ID: {missing_info['record_id']}) - {missing_info['overlap_ratio']:.1%} match")
        
        # Print incorrect entities if any
        if comparison_result.get("incorrect_entities"):
            print(f"  ⚠️  Irrelevant Entities Found:")
            for entity_info in comparison_result["incorrect_entities"][:3]:  # Show first 3
                match_info = f"{entity_info['overlap_ratio']:.1%}↔{entity_info.get('reverse_overlap_ratio', 0):.1%}"
                print(f"    • {entity_info['full_name']} (ID: {entity_info['record_id']}) - {match_info} match")
    
    def run_all_tests(self):
        """
        Run regression tests for all entities and generate consolidated reports
        """
        print("Consolidated Regression Testing Framework")
        print("=" * 80)
        
        # Load entities from Excel
        entities = self.load_entities_from_excel()
        
        if not entities:
            print("No entities found in Excel file. Exiting.")
            return
        
        # Process each entity
        for i, entity in enumerate(entities, 1):
            print(f"\n[{i}/{len(entities)}] Processing: {entity['name']} (Type: {entity['type']})")
            
            # Fetch current data from API
            current_data = self.fetch_current_data(entity['name'], entity['type'])
            
            if current_data is None:
                print(f"Failed to fetch current data for {entity['name']}. Skipping.")
                continue
            
            # Compare data
            comparison_result = self.compare_data(entity['name'], entity['baseline_data'], current_data)
            
            # Store results for consolidated reporting
            self.all_results.append({
                "entity": entity,
                "comparison_result": comparison_result
            })
            
            # Print brief summary
            self.print_entity_summary(entity, comparison_result)
        
        # Generate consolidated reports
        print(f"\n{'='*80}")
        print("Generating consolidated reports...")
        excel_file, html_file = self.generate_consolidated_reports()
        
        # Print overall summary
        self.print_overall_summary()
        
        print(f"\nConsolidated reports generated:")
        print(f"  Excel: {excel_file}")
        print(f"  HTML: {html_file}")
    
    def print_overall_summary(self):
        """
        Print overall summary of all tests
        """
        print(f"\n{'='*80}")
        print("OVERALL TEST SUMMARY")
        print(f"{'='*80}")
        
        total_entities = len(self.all_results)
        total_common = 0
        total_new = 0
        total_missing = 0
        
        # Calculate totals by type
        entity_counts = {"E": 0, "P": 0}
        
        for result in self.all_results:
            entity = result["entity"]
            comparison_result = result["comparison_result"]
            
            entity_counts[entity["type"]] += 1
            
            for source, data in comparison_result["sources"].items():
                total_common += data["summary"]["exact_matches"] + data["summary"]["modified_records"]
                total_new += data["summary"]["new_records"]
                total_missing += data["summary"]["missing_records"]
        
        print(f"Total Entities Tested: {total_entities}")
        print(f"  - Entities (Organizations): {entity_counts['E']}")
        print(f"  - Persons: {entity_counts['P']}")
        print(f"Total Common Records: {total_common}")
        print(f"Total New in OpenSearch: {total_new}")
        print(f"Total Missing from OpenSearch: {total_missing}")
        print(f"{'='*80}")

if __name__ == "__main__":
    # Run the consolidated regression test framework
    framework = ConsolidatedRegressionTest()
    framework.run_all_tests()
