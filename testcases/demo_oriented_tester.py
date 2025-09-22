#!/usr/bin/env python3
"""
Demo Oriented Tester
Tests specific scenarios with detailed criteria matching for demonstration purposes
"""

import requests
import json
import pandas as pd
from datetime import datetime
import os
import html
import re
from difflib import SequenceMatcher

class DemoOrientedTester:
    def __init__(self, test_data_file="targeted_test_cases.xlsx"):
        self.test_data_file = test_data_file
        
        # API Configuration
        self.api_config = {
            "url": "https://15krnwu233.execute-api.us-east-1.amazonaws.com/prod/search",
            "api_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJyZWFkLWNsaWVudCIsInJvbGUiOiJyZWFkIiwicGVybWlzc2lvbnMiOlsicmVhZCJdLCJleHAiOjE3NTgwODcyMzIsImlhdCI6MTc1ODA4MzYzMiwiaXNzIjoiZ2RjLXNlYXJjaC1pZGVudGl0eS1zZXJ2aWNlIn0.8-ffozf_8N1AmiWMgyG1y321K94EzKR_vyQ9VdhqcRM",
            "timeout": 30
        }
        
        # Expected GDC data from payloads (only relevant IDs with names)
        self.expected_gdc_data = {
            "mirage aircraft": {
                "sanction": [{"id": "10131047950", "name": "MIRAGE AIR CRAFT SERVICES SOLE PROPRIETORSHIP LLC"}],
                "watch": [
                    {"id": "20201576120", "name": "MIRAGE AIR CRAFT SERVICES SOLE PROPREITORSHIP LLC"},
                    {"id": "20201633423", "name": "MIRAGE AIR CRAFT SERVICES SOLE PROPRIETORSHIP LLC"}
                ]
            },
            "sigma airline": {
                "sanction": [
                    {"id": "10151125404", "name": "Air Sigma"},
                    {"id": "10120043364", "name": "Sigma Airlines"},
                    {"id": "10840000003", "name": "Sigma Airlines"},
                    {"id": "10230004668", "name": "Sigma Airlines"},
                    {"id": "10160013915", "name": "SIGMA AIRLINES"}
                ],
                "watch": [{"id": "20201734127", "name": "SIGMA AIRLINES"}]
            },
            "nbd": {
                "watch": [
                    {"id": "20200126717", "name": "Nbd Bank"},
                    {"id": "20200126718", "name": "Nbd Trust Company of Florida, National Association"},
                    {"id": "20201091071", "name": "Nbd Bank, N.A."},
                    {"id": "20201091095", "name": "Nbd Bank, N.A."},
                    {"id": "20201356443", "name": "emirat-nbd.com"},
                    {"id": "20200902319", "name": "National Bank of Dubai"}
                ],
                "soe": [
                    {"id": "90100059095", "name": "National Bank of Dominica Ltd."},
                    {"id": "90100165219", "name": "NBD - Podtureň, s.r.o."},
                    {"id": "90100182651", "name": "Emirates NBD Capital India Private Limited"},
                    {"id": "90100030829", "name": "Emirates NBD Global Services LLC"},
                    {"id": "90100091610", "name": "Emirates NBD Trust Company (Jersey) Limited"},
                    {"id": "90100030818", "name": "Emirates NBD Bank PJSC"},
                    {"id": "90100030825", "name": "Emirates NBD Capital Limited"},
                    {"id": "90100030964", "name": "Emirates NBD Capital PJSC"},
                    {"id": "90100030966", "name": "Emirates NBD Asset Management Limited"},
                    {"id": "90100030967", "name": "Emirates NBD Securities LLC"},
                    {"id": "90100091611", "name": "Emirates NBD Global Funding Limited"},
                    {"id": "90100091612", "name": "Emirates NBD Capital (KSA) LLC"},
                    {"id": "90100091616", "name": "Emirates NBD Properties LLC"},
                    {"id": "90100091618", "name": "Emirates NBD Egypt S.A.E"}
                ],
                "rights": [
                    {"id": "30710006066", "name": "Emirates NBD"}
                ],
                "icij": [
                    {"id": "80000485109", "name": "Structured Trust Services, S.A., as trustee of Fideicomiso ITS-ASRL/NBD 2010"},
                    {"id": "80000327942", "name": "NATIONAL BANK OF DUBAI"}
                ]
            },
            "thomas nikolaus": {
                "watch": [{"id": "20200088215", "name": "Thomas Nikolaus"}]
            }
        }
        
        # Ensure results directory exists
        os.makedirs("results", exist_ok=True)
        
        # Store all test results
        self.test_results = []
    
    def load_test_data(self):
        """Load demo oriented test data"""
        try:
            df = pd.read_excel(self.test_data_file)
            df = df.dropna(subset=['Search Term', 'Entity Type'])
            
            test_cases = []
            for index, row in df.iterrows():
                test_case = {
                    "search_term": row['Search Term'].strip(),
                    "entity_type": row['Entity Type'].strip(),
                    "expected_result_type": row.get('Expected Result Type', 'exact_match').strip(),
                    "specific_criteria": row.get('Specific Criteria', '').strip(),
                    "notes": row.get('Notes', '').strip(),
                    "row_index": index
                }
                test_cases.append(test_case)
            
            print(f"Loaded {len(test_cases)} targeted test cases")
            return test_cases
            
        except Exception as e:
            print(f"Error loading test data: {e}")
            return []
    
    def call_opensearch_api(self, search_term, entity_type):
        """Call OpenSearch API"""
        payload = {
            "query": search_term,
            "schemas": ["col", "rights", "mex", "watch", "soe", "pep", "sanction", "icij"],
            "limit": 100,
            "search_types": ["keyword", "phonetic", "similarity"]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_config['api_key']}"
        }
        
        try:
            print(f"Calling OpenSearch API for '{search_term}' (Type: {entity_type})...")
            
            response = requests.post(self.api_config["url"], json=payload, headers=headers, timeout=self.api_config["timeout"])
            response.raise_for_status()
            
            api_result = response.json()
            return self.transform_opensearch_response(api_result)
            
        except Exception as e:
            print(f"Error calling OpenSearch API: {e}")
            return {"results": [], "total_hits": 0, "error": str(e)}
    
    def transform_opensearch_response(self, api_response):
        """Transform API response"""
        try:
            results = []
            schema_counts = {}
            
            if "results" in api_response and isinstance(api_response["results"], list):
                for result in api_response["results"]:
                    if "_source" in result:
                        source_data = result["_source"]
                        
                        # Extract name information
                        full_name = source_data.get("Full_Name", "")
                        first_name = source_data.get("First_Name", "")
                        last_name = source_data.get("Last_Name", "")
                        
                        # For ICIJ schema, use name_normalized or name field
                        schema_name = result.get("_index", "").lower()
                        if schema_name == "icij":
                            name_normalized = source_data.get("name_normalized", "")
                            name_field = source_data.get("name", "")
                            if name_normalized:
                                full_name = name_normalized
                            elif name_field:
                                full_name = name_field
                        
                        # Construct full name if not present
                        if not full_name and (first_name or last_name):
                            full_name = f"{first_name} {last_name}".strip()
                        
                        normalized_result = {
                            "id": source_data.get("ID", ""),
                            "full_name": full_name,
                            "first_name": first_name,
                            "last_name": last_name,
                            "other_names": source_data.get("Other_Names", ""),
                            "schema": result.get("_index", ""),
                            "score": result.get("_score", 0),
                            "raw_result": result
                        }
                        results.append(normalized_result)
                        
                        # Count by schema
                        schema = result.get("_index", "").upper()
                        schema_counts[schema] = schema_counts.get(schema, 0) + 1
                
                # Print summary
                for schema, count in schema_counts.items():
                    print(f"  {schema}: {count} records")
            
            return {
                "results": results,
                "total_hits": len(results),
                "schema_counts": schema_counts,
                "error": None
            }
            
        except Exception as e:
            print(f"Error transforming API response: {e}")
            return {"results": [], "total_hits": 0, "error": str(e)}
    
    def check_gdc_payload_match(self, search_term, result):
        """Check if OpenSearch result matches expected GDC payload data"""
        search_key = search_term.lower().strip()
        result_id = result.get("id", "")
        result_schema = result.get("schema", "").lower()
        
        # Check if this search term has expected GDC data
        if search_key in self.expected_gdc_data:
            expected_data = self.expected_gdc_data[search_key]
            
            # Check if this result ID appears in expected GDC data
            for schema, expected_records in expected_data.items():
                for record in expected_records:
                    if result_id == record["id"] and schema == result_schema:
                        return {
                            "is_gdc_match": True,
                            "gdc_schema": schema,
                            "gdc_note": f"Expected from GDC payload ({schema})",
                            "gdc_expected_name": record["name"]
                        }
        
        return {
            "is_gdc_match": False,
            "gdc_schema": None,
            "gdc_note": "Not in expected GDC payload",
            "gdc_expected_name": None
        }

    def evaluate_targeted_relevance(self, search_term, api_response, test_case):
        """Evaluate relevance based on specific criteria"""
        results = api_response.get("results", [])
        specific_criteria = test_case["specific_criteria"]
        expected_type = test_case["expected_result_type"]
        
        if not results:
            # Check if we expected GDC data but got no OpenSearch results
            search_key = search_term.lower().strip()
            expected_gdc = self.expected_gdc_data.get(search_key, {})
            expected_count = sum(len(records) for records in expected_gdc.values())
            
            return {
                "status": "FAIL",
                "reason": f"No OpenSearch results (Expected {expected_count} records from Info4c)" if expected_count > 0 else "No results returned",
                "relevant_results": [],
                "irrelevant_results": [],
                "excluded_results": [],
                "missing_gdc_results": expected_count,
                "total_results": 0,
                "criteria_met": False
            }
        
        relevant_results = []
        irrelevant_results = []
        excluded_results = []
        
        for result in results:
            # Check criteria relevance
            evaluation = self.evaluate_single_result(search_term, result, test_case)
            
            # Check GDC payload match
            gdc_match = self.check_gdc_payload_match(search_term, result)
            
            result_with_evaluation = result.copy()
            result_with_evaluation.update(evaluation)
            result_with_evaluation.update(gdc_match)
            
            # Enhanced classification including GDC context
            if evaluation["is_relevant"]:
                if gdc_match["is_gdc_match"]:
                    result_with_evaluation["classification"] = "Relevant & Expected from GDC"
                else:
                    result_with_evaluation["classification"] = "Relevant (OpenSearch only)"
                relevant_results.append(result_with_evaluation)
            elif evaluation["is_excluded"]:
                result_with_evaluation["classification"] = "Should be Excluded"
                excluded_results.append(result_with_evaluation)
            else:
                result_with_evaluation["classification"] = "Irrelevant"
                irrelevant_results.append(result_with_evaluation)
        
        # Check for missing GDC results
        search_key = search_term.lower().strip()
        expected_gdc = self.expected_gdc_data.get(search_key, {})
        missing_gdc_ids = []
        found_gdc_ids = []
        
        for result in relevant_results:
            if result.get("is_gdc_match", False):
                found_gdc_ids.append(result["id"])
        
        for schema, expected_records in expected_gdc.items():
            for record in expected_records:
                if record["id"] not in found_gdc_ids:
                    missing_gdc_ids.append(f"{record['id']} - {record['name']} ({schema})")
        
        # Determine overall status
        gdc_matches = len([r for r in relevant_results if r.get("is_gdc_match", False)])
        
        # Combine excluded and irrelevant results - they're all "not what we searched for"
        all_irrelevant_results = excluded_results + irrelevant_results
        criteria_met = len(relevant_results) > 0 and len(all_irrelevant_results) == 0
        
        # Calculate failure reasons for irrelevant results
        failure_reasons = []
        if all_irrelevant_results:
            for result in all_irrelevant_results[:5]:  # Show first 5 irrelevant results
                failure_reasons.append(f"Searched for '{search_term}' but got '{result['full_name']}' - not what we searched for")
        
        if not relevant_results:
            status = "FAIL"
            reason = f"No relevant OpenSearch results found"
            if missing_gdc_ids:
                reason += f" (Missing {len(missing_gdc_ids)} expected Info4c records)"
        elif all_irrelevant_results:
            # FAIL if ANY irrelevant results exist, regardless of relevant count
            status = "FAIL"
            reason = f"Search returned irrelevant results: {len(all_irrelevant_results)} irrelevant out of {len(results)} total"
        elif missing_gdc_ids:
            status = "WARN"
            reason = f"Found {len(relevant_results)} relevant results, but missing {len(missing_gdc_ids)} expected Info4c records"
        else:
            status = "PASS"
            reason = f"Found {len(relevant_results)} relevant results"
            if gdc_matches > 0:
                reason += f" ({gdc_matches} match Info4c records)"
        
        return {
            "status": status,
            "reason": reason,
            "relevant_results": relevant_results,
            "irrelevant_results": all_irrelevant_results,  # Combined excluded + irrelevant
            "excluded_results": [],  # No longer used - moved to irrelevant
            "missing_gdc_ids": missing_gdc_ids,
            "found_gdc_matches": gdc_matches,
            "failure_reasons": failure_reasons,
            "total_results": len(results),
            "criteria_met": criteria_met
        }
    
    def evaluate_single_result(self, search_term, result, test_case):
        """Evaluate a single result against specific criteria"""
        search_normalized = search_term.lower().strip()
        result_name = result["full_name"].lower().strip()
        other_names = result["other_names"].lower().strip()
        first_name = result["first_name"].lower().strip()
        last_name = result["last_name"].lower().strip()
        
        # Combine all name fields for evaluation
        all_names = f"{result_name} {other_names} {first_name} {last_name}".strip()
        
        # Apply specific criteria based on test case
        if "Microsoft Corporation" in test_case["search_term"] or test_case["search_term"].lower().strip() == "microsoft":
            return self.evaluate_microsoft_criteria(search_normalized, result_name, other_names)
        elif "Mirage AIRCRAFT" in test_case["search_term"]:
            return self.evaluate_mirage_aircraft_criteria(search_normalized, all_names)
        elif "Sigma airline" in test_case["search_term"]:
            return self.evaluate_sigma_airline_criteria(search_normalized, all_names)
        elif "NBD" in test_case["search_term"]:
            return self.evaluate_nbd_criteria(search_normalized, all_names)
        elif "Thomas Nikolaus" in test_case["search_term"]:
            return self.evaluate_thomas_nikolaus_criteria(search_normalized, first_name, last_name, result_name)
        elif "David Smith" in test_case["search_term"]:
            return self.evaluate_david_smith_criteria(search_normalized, first_name, last_name, result_name)
        elif "Al Hamdani" in test_case["search_term"]:
            return self.evaluate_al_hamdani_criteria(search_normalized, all_names)
        else:
            # Default evaluation
            return self.evaluate_default_criteria(search_normalized, all_names)
    
    def evaluate_microsoft_criteria(self, search_term, result_name, other_names):
        """Microsoft Corporation: exclude subsidiaries like Microsoft AG, Microsoft Ireland"""
        all_text = f"{result_name} {other_names}".lower()
        
        # Should contain "microsoft corporation"
        if "microsoft corporation" in all_text:
            return {"is_relevant": True, "is_excluded": False, "reason": "Exact Microsoft Corporation match"}
        
        # Exclude subsidiaries/regional offices
        exclusion_terms = ["microsoft ag", "microsoft ireland", "microsoft limited", "microsoft ltd", 
                          "microsoft gmbh", "microsoft inc", "microsoft llc"]
        
        for exclusion in exclusion_terms:
            if exclusion in all_text:
                return {"is_relevant": False, "is_excluded": True, "reason": f"Excluded subsidiary: {exclusion}"}
        
        # Allow general Microsoft matches but mark as less relevant
        if "microsoft" in all_text:
            return {"is_relevant": True, "is_excluded": False, "reason": "General Microsoft match"}
        
        return {"is_relevant": False, "is_excluded": False, "reason": "No Microsoft match"}
    
    def evaluate_mirage_aircraft_criteria(self, search_term, all_names):
        """Mirage Aircraft: should find "Mirage Air Craft Services" despite spacing"""
        # Look for mirage and aircraft/air craft combinations
        has_mirage = "mirage" in all_names
        has_aircraft = "aircraft" in all_names or "air craft" in all_names
        
        if has_mirage and has_aircraft:
            return {"is_relevant": True, "is_excluded": False, "reason": "Found Mirage Aircraft/Air Craft match"}
        
        return {"is_relevant": False, "is_excluded": False, "reason": "No Mirage Aircraft match"}
    
    def evaluate_sigma_airline_criteria(self, search_term, all_names):
        """Sigma Airline: should find Sigma Airlines (with 's')"""
        has_sigma = "sigma" in all_names
        has_airline = "airline" in all_names or "airlines" in all_names
        
        if has_sigma and has_airline:
            return {"is_relevant": True, "is_excluded": False, "reason": "Found Sigma Airline/Airlines match"}
        
        return {"is_relevant": False, "is_excluded": False, "reason": "No Sigma Airline match"}
    
    def evaluate_nbd_criteria(self, search_term, all_names):
        """NBD: should find National Bank of Dubai, exclude irrelevant NBD matches"""
        # Highly relevant NBD matches (exact bank names)
        highly_relevant = ["national bank of dubai", "emirates nbd bank", "nbd bank"]
        
        for term in highly_relevant:
            if term in all_names:
                return {"is_relevant": True, "is_excluded": False, "reason": f"Found relevant NBD match: {term}"}
        
        # Moderately relevant (Emirates NBD variations)
        moderately_relevant = ["emirates nbd"]
        for term in moderately_relevant:
            if term in all_names and "bank" in all_names:
                return {"is_relevant": True, "is_excluded": False, "reason": f"Found relevant NBD match: {term}"}
        
        # Exclude clearly irrelevant NBD matches (not bank-related)
        irrelevant_patterns = [
            "nodarovich", "nodarievich", "nodaro", "nodar", 
            "book development", "podturen",
            "nodependenza", "edge ngram"
        ]
        
        for pattern in irrelevant_patterns:
            if pattern in all_names:
                return {"is_relevant": False, "is_excluded": True, "reason": f"Excluded irrelevant match: {pattern}"}
        
        # If contains NBD, check for bank context or NBD-related domains
        if "nbd" in all_names:
            # Check if it's bank-related or NBD domain
            bank_indicators = ["bank", "financial", "dubai", "emirates"]
            nbd_domains = ["emirat-nbd", "nbd.com", "nbd.ae"]
            
            has_bank_context = any(indicator in all_names for indicator in bank_indicators)
            has_nbd_domain = any(domain in all_names for domain in nbd_domains)
            
            if has_bank_context or has_nbd_domain:
                return {"is_relevant": True, "is_excluded": False, "reason": "Found NBD with bank/domain context"}
            else:
                return {"is_relevant": False, "is_excluded": False, "reason": "NBD found but not bank-related"}
        
        return {"is_relevant": False, "is_excluded": False, "reason": "No NBD match"}
    
    def evaluate_thomas_nikolaus_criteria(self, search_term, first_name, last_name, full_name):
        """Thomas Nikolaus: exact person match"""
        # Check for exact first and last name match
        has_thomas = "thomas" in first_name or "thomas" in full_name
        has_nikolaus = "nikolaus" in last_name or "nikolaus" in full_name
        
        if has_thomas and has_nikolaus:
            return {"is_relevant": True, "is_excluded": False, "reason": "Found Thomas Nikolaus exact match"}
        
        return {"is_relevant": False, "is_excluded": False, "reason": "No Thomas Nikolaus match"}
    
    def evaluate_david_smith_criteria(self, search_term, first_name, last_name, full_name):
        """David Smith: only David Smith or David Smithy, exclude David Beckham or John Smith"""
        all_text = f"{first_name} {last_name} {full_name}".lower()
        
        has_david = "david" in all_text
        has_smith = "smith" in all_text
        
        # Must have both David and Smith
        if not (has_david and has_smith):
            return {"is_relevant": False, "is_excluded": False, "reason": "Missing David or Smith"}
        
        # Exclude wrong combinations
        if "david beckham" in all_text or "john smith" in all_text:
            return {"is_relevant": False, "is_excluded": True, "reason": "Excluded: wrong name combination"}
        
        # Accept David Smith or David Smithy
        if "david smith" in all_text:
            return {"is_relevant": True, "is_excluded": False, "reason": "Found David Smith match"}
        
        return {"is_relevant": True, "is_excluded": False, "reason": "Found David + Smith combination"}
    
    def evaluate_al_hamdani_criteria(self, search_term, all_names):
        """Al Hamdani: names containing Al Hamdani variations - exclude Haldane or Hamdaniyah"""
        
        # Exclude clearly unrelated matches (should cause test failure)
        exclusions = ["haldane", "hamdaniyah", "al-hamdaniyah"]
        for exclusion in exclusions:
            if exclusion in all_names:
                return {"is_relevant": False, "is_excluded": True, "reason": f"Excluded unrelated match: {exclusion}"}
        
        # Check for various Al Hamdani patterns (case insensitive)
        al_hamdani_patterns = [
            "al hamdani",      # Standard format: "Saad S. Al-Hamdani"
            "al-hamdani",      # With hyphen: "Bashar Ismail al-Hamdani"
            "alhamdani",       # No space/hyphen
            "ali hamdani",     # Ali variation: "Ali Hamdani bin Md Diah"
            "ali-hamdani",     # Ali with hyphen
            "alihamdani"       # Ali no space/hyphen
        ]
        
        for pattern in al_hamdani_patterns:
            if pattern in all_names:
                return {"is_relevant": True, "is_excluded": False, "reason": "Found Al Hamdani pattern"}
        
        # Mark other non-matches as irrelevant (not excluded, but still wrong)
        return {"is_relevant": False, "is_excluded": False, "reason": "No Al Hamdani match"}
    
    def evaluate_default_criteria(self, search_term, all_names):
        """Default evaluation for other cases"""
        # Simple word overlap
        search_words = set(search_term.split())
        name_words = set(all_names.split())
        
        overlap = search_words.intersection(name_words)
        overlap_ratio = len(overlap) / len(search_words) if search_words else 0
        
        if overlap_ratio >= 0.5:
            return {"is_relevant": True, "is_excluded": False, "reason": f"Word overlap: {overlap_ratio:.2f}"}
        
        return {"is_relevant": False, "is_excluded": False, "reason": f"Low word overlap: {overlap_ratio:.2f}"}
    
    def run_targeted_test(self, test_case):
        """Run a targeted test"""
        search_term = test_case["search_term"]
        entity_type = test_case["entity_type"]
        
        print(f"\n{'='*80}")
        print(f"Testing: {search_term}")
        print(f"Criteria: {test_case['specific_criteria']}")
        print(f"{'='*80}")
        
        # Call API
        api_response = self.call_opensearch_api(search_term, entity_type)
        
        # Evaluate against criteria
        evaluation = self.evaluate_targeted_relevance(search_term, api_response, test_case)
        
        # Print results
        status = evaluation["status"]
        status_emoji = "✅" if status == "PASS" else "⚠️" if status == "WARN" else "❌"
        
        print(f"\n{status_emoji} Test Status: {status}")
        print(f"Reason: {evaluation['reason']}")
        print(f"Total OpenSearch Results: {evaluation['total_results']}")
        print(f"✅ Relevant: {len(evaluation['relevant_results'])}")
        print(f"❌ Irrelevant: {len(evaluation['irrelevant_results'])}")
        
        if evaluation.get('found_gdc_matches', 0) > 0:
            print(f"📋 Info4c Payload Matches: {evaluation['found_gdc_matches']}")
        
        if evaluation.get('missing_gdc_ids'):
            print(f"⚠️ Missing Expected Info4c Records: {len(evaluation['missing_gdc_ids'])}")
        
        # Show failure reasons for irrelevant results
        if evaluation.get('failure_reasons'):
            print(f"\n❌ FAILURE REASONS:")
            for reason in evaluation['failure_reasons']:
                print(f"  • {reason}")
        
        # Show relevant results with Info4c context
        if evaluation['relevant_results']:
            print(f"\n🎯 RELEVANT OPENSEARCH RESULTS:")
            for result in evaluation['relevant_results'][:5]:
                gdc_indicator = "📋 Info4c" if result.get("is_gdc_match", False) else "🔍 OS"
                print(f"  {gdc_indicator} {result['full_name']} (ID: {result['id']}) - {result['reason']}")
                if result.get("is_gdc_match", False):
                    print(f"      └─ {result.get('gdc_note', '')}")
        
        # Show missing Info4c records
        if evaluation.get('missing_gdc_ids'):
            print(f"\n⚠️ MISSING EXPECTED INFO4C RECORDS:")
            for missing_id in evaluation['missing_gdc_ids'][:5]:
                print(f"  • {missing_id} - Not found in OpenSearch")
        
        # Show irrelevant results - all results that are not what we searched for
        if evaluation['irrelevant_results']:
            print(f"\n❌ IRRELEVANT RESULTS (Not what we searched for):")
            for result in evaluation['irrelevant_results'][:10]:  # Show more irrelevant results
                print(f"  • {result['full_name']} (ID: {result['id']}) - {result['reason']}")
        
        return {
            "test_case": test_case,
            "api_response": api_response,
            "evaluation": evaluation,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def generate_reports(self):
        """Generate Excel and HTML reports"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        excel_filename = f"results/demo_oriented_report_{timestamp}.xlsx"
        html_filename = f"results/demo_oriented_report_{timestamp}.html"
        
        self.generate_excel_report(excel_filename)
        self.generate_html_report(html_filename)
        
        print(f"\n📊 Reports generated:")
        print(f"  Excel: {excel_filename}")
        print(f"  HTML: {html_filename}")
    
    def generate_excel_report(self, filename):
        """Generate detailed Excel report"""
        summary_data = []
        relevant_data = []
        irrelevant_data = []
        missing_gdc_data = []
        expected_gdc_data = []
        
        for result in self.test_results:
            test_case = result["test_case"]
            evaluation = result["evaluation"]
            
            # Summary sheet
            summary_data.append({
                "Search Term": test_case["search_term"],
                "Entity Type": test_case["entity_type"],
                "Specific Criteria": test_case["specific_criteria"],
                "Status": evaluation["status"],
                "Total OpenSearch Results": evaluation["total_results"],
                "Relevant": len(evaluation["relevant_results"]),
                "Irrelevant": len(evaluation["irrelevant_results"]),
                "Info4c Payload Matches": evaluation.get("found_gdc_matches", 0),
                "Missing GDC IDs": len(evaluation.get("missing_gdc_ids", [])),
                "Criteria Met": "Yes" if evaluation["criteria_met"] else "No",
                "Reason": evaluation["reason"],
                "Timestamp": result["timestamp"]
            })
            
            # Relevant results sheet
            for res in evaluation["relevant_results"]:
                relevant_data.append({
                    "Search Term": test_case["search_term"],
                    "Result Name": res["full_name"],
                    "ID": res["id"],
                    "Schema": res["schema"],
                    "Other Names": res["other_names"],
                    "Classification": res.get("classification", "Relevant"),
                    "GDC Match": "Yes" if res.get("is_gdc_match", False) else "No",
                    "GDC Note": res.get("gdc_note", ""),
                    "Evaluation Reason": res["reason"],
                    "Status": "Relevant"
                })
            
            # Irrelevant results sheet (not what we searched for)
            for res in evaluation["irrelevant_results"]:
                irrelevant_data.append({
                    "Search Term": test_case["search_term"],
                    "Result Name": res["full_name"],
                    "ID": res["id"],
                    "Schema": res["schema"],
                    "Other Names": res["other_names"],
                    "Reason": res["reason"],
                    "Status": "Not what we searched for"
                })
            
            # Missing GDC IDs sheet
            for missing_id in evaluation.get("missing_gdc_ids", []):
                missing_gdc_data.append({
                    "Search Term": test_case["search_term"],
                    "Missing ID": missing_id,
                    "Status": "Expected from Info4c but not found in OpenSearch",
                    "Impact": "Potential data gap"
                })
            
            # Expected GDC results sheet (show all expected from payload)
            search_key = test_case["search_term"].lower().strip()
            if search_key in self.expected_gdc_data:
                expected_data = self.expected_gdc_data[search_key]
                for schema, records in expected_data.items():
                    for record in records:
                        # Check if this was found in OpenSearch
                        found_in_os = any(
                            r.get("id") == record["id"] and r.get("schema", "").lower() == schema
                            for r in evaluation["relevant_results"]
                        )
                        
                        expected_gdc_data.append({
                            "Search Term": test_case["search_term"],
                            "Expected ID": record["id"],
                            "Expected Name": record["name"],
                            "Schema": schema.upper(),
                            "Found in OpenSearch": "Yes" if found_in_os else "No",
                            "Status": "Match" if found_in_os else "Missing"
                        })
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            if summary_data:
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Test Summary', index=False)
            if expected_gdc_data:
                pd.DataFrame(expected_gdc_data).to_excel(writer, sheet_name='Expected Info4c Records', index=False)
            if relevant_data:
                pd.DataFrame(relevant_data).to_excel(writer, sheet_name='OpenSearch Results', index=False)
            if irrelevant_data:
                pd.DataFrame(irrelevant_data).to_excel(writer, sheet_name='Irrelevant Results', index=False)
            if missing_gdc_data:
                pd.DataFrame(missing_gdc_data).to_excel(writer, sheet_name='Missing Info4c Records', index=False)
    
    def generate_html_report(self, filename):
        """Generate visual HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Targeted OpenSearch Relevance Test Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .test-case {{ margin: 20px 0; border: 1px solid #ddd; border-radius: 10px; background: white; overflow: hidden; }}
        .test-header {{ padding: 15px; font-weight: bold; font-size: 1.1em; }}
        .test-pass {{ background-color: #d4edda; color: #155724; }}
        .test-warn {{ background-color: #fff3cd; color: #856404; }}
        .test-fail {{ background-color: #f8d7da; color: #721c24; }}
        .test-content {{ padding: 15px; }}
        .criteria-box {{ background-color: #e9ecef; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f8f9fa; }}
        .relevant {{ background-color: #d4edda; }}
        .irrelevant {{ background-color: #f8d7da; }}
        .excluded {{ background-color: #f5c6cb; border: 2px solid #dc3545; }}
        .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat-box {{ text-align: center; padding: 15px; border-radius: 8px; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Targeted OpenSearch Relevance Test Results</h1>
        <p><strong>Test Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>Total Test Cases:</strong> {len(self.test_results)}</p>
    </div>
"""
        
        # Overall statistics
        pass_count = sum(1 for r in self.test_results if r["evaluation"]["status"] == "PASS")
        warn_count = sum(1 for r in self.test_results if r["evaluation"]["status"] == "WARN")
        fail_count = sum(1 for r in self.test_results if r["evaluation"]["status"] == "FAIL")
        
        html_content += f"""
    <div class="stats">
        <div class="stat-box" style="border-left: 4px solid #28a745;">
            <h3>✅ PASSED</h3>
            <h2>{pass_count}</h2>
        </div>
        <div class="stat-box" style="border-left: 4px solid #ffc107;">
            <h3>⚠️ WARNINGS</h3>
            <h2>{warn_count}</h2>
        </div>
        <div class="stat-box" style="border-left: 4px solid #dc3545;">
            <h3>❌ FAILED</h3>
            <h2>{fail_count}</h2>
        </div>
    </div>
"""
        
        # Individual test cases
        for result in self.test_results:
            test_case = result["test_case"]
            evaluation = result["evaluation"]
            
            status_class = f"test-{evaluation['status'].lower()}"
            status_emoji = "✅" if evaluation["status"] == "PASS" else "⚠️" if evaluation["status"] == "WARN" else "❌"
            
            html_content += f"""
    <div class="test-case">
        <div class="test-header {status_class}">
            {status_emoji} {html.escape(test_case['search_term'])} ({test_case['entity_type']}) - {evaluation['status']}
        </div>
        <div class="test-content">
            <div class="criteria-box">
                <strong>Specific Criteria:</strong> {html.escape(test_case['specific_criteria'])}
            </div>
            
            <p><strong>Results:</strong> {evaluation['total_results']} total | 
               ✅ {len(evaluation['relevant_results'])} relevant | 
               ❌ {len(evaluation['irrelevant_results'])} irrelevant | 
               🚫 {len(evaluation['excluded_results'])} excluded</p>
            <p><strong>Status:</strong> {html.escape(evaluation['reason'])}</p>"""
            
            # Add expected Info4c records table
            search_key = test_case["search_term"].lower().strip()
            if search_key in self.expected_gdc_data:
                expected_data = self.expected_gdc_data[search_key]
                html_content += f"""
            
            <h4>📋 Expected Info4c Records:</h4>
            <table>
                <tr><th>ID</th><th>Name</th><th>Schema</th><th>Status</th></tr>"""
                
                for schema, records in expected_data.items():
                    for record in records:
                        # Check if found in OpenSearch
                        found_in_os = any(
                            r.get("id") == record["id"] and r.get("schema", "").lower() == schema
                            for r in evaluation["relevant_results"]
                        )
                        status_class = "relevant" if found_in_os else "irrelevant"
                        status_text = "✅ Found" if found_in_os else "❌ Missing"
                        
                        html_content += f"""
                <tr class="{status_class}">
                    <td>{html.escape(record['id'])}</td>
                    <td>{html.escape(record['name'])}</td>
                    <td>{html.escape(schema.upper())}</td>
                    <td>{status_text}</td>
                </tr>"""
                
                html_content += """
            </table>"""
            
            html_content += f"""
            
            <h4>📊 OpenSearch Results:</h4>
            <table>
                <tr><th>Name</th><th>ID</th><th>Schema</th><th>Status</th><th>Reason</th></tr>
"""
            
            # Show all results with proper classification
            all_results = []
            
            for res in evaluation['relevant_results']:
                all_results.append((res, "relevant", "✅ Relevant", res.get('reason', '')))
            
            for res in evaluation['irrelevant_results'][:10]:  # Show more irrelevant results
                all_results.append((res, "irrelevant", "❌ Not what we searched for", res.get('reason', '')))
            
            for res, css_class, status_text, reason in all_results:
                html_content += f"""
                <tr class="{css_class}">
                    <td>{html.escape(res['full_name'])}</td>
                    <td>{html.escape(res['id'])}</td>
                    <td>{html.escape(res['schema'])}</td>
                    <td>{status_text}</td>
                    <td>{html.escape(reason)}</td>
                </tr>
"""
            
            html_content += """
            </table>
        </div>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def run_all_tests(self):
        """Run all demo oriented tests"""
        print("🎯 Demo Oriented Tester")
        print("=" * 80)
        
        test_cases = self.load_test_data()
        if not test_cases:
            print("No test cases loaded. Exiting.")
            return
        
        # Reorder test cases - put NBD at the end since it has too much data
        nbd_tests = [tc for tc in test_cases if tc['search_term'].lower() == 'nbd']
        other_tests = [tc for tc in test_cases if tc['search_term'].lower() != 'nbd']
        reordered_tests = other_tests + nbd_tests
        
        for i, test_case in enumerate(reordered_tests, 1):
            print(f"\n[{i}/{len(reordered_tests)}] Processing: {test_case['search_term']}")
            test_result = self.run_targeted_test(test_case)
            self.test_results.append(test_result)
        
        # Generate reports
        self.generate_reports()
        
        # Final summary
        pass_count = sum(1 for r in self.test_results if r["evaluation"]["status"] == "PASS")
        warn_count = sum(1 for r in self.test_results if r["evaluation"]["status"] == "WARN")
        fail_count = sum(1 for r in self.test_results if r["evaluation"]["status"] == "FAIL")
        
        print(f"\n{'='*80}")
        print("🎯 DEMO ORIENTED TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {pass_count}")
        print(f"⚠️ Warnings: {warn_count}")
        print(f"❌ Failed: {fail_count}")
        print(f"Success Rate: {(pass_count/len(self.test_results)*100):.1f}%")
        print("=" * 80)

if __name__ == "__main__":
    tester = DemoOrientedTester()
    tester.run_all_tests()
