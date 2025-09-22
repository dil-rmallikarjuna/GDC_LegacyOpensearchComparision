#!/usr/bin/env python3
"""
OpenSearch Search Relevance Tester
Tests search relevance without baseline comparison - evaluates if OpenSearch results are relevant to search terms.
"""

import requests
import json
import pandas as pd
from datetime import datetime
import os
import html
import re
from difflib import SequenceMatcher

class SearchRelevanceTester:
    def __init__(self, test_data_file="search_relevance_test_data.xlsx"):
        self.test_data_file = test_data_file
        
        # API Configuration
        self.api_config = {
            "url": "https://15krnwu233.execute-api.us-east-1.amazonaws.com/prod/search",
            "api_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJyZWFkLWNsaWVudCIsInJvbGUiOiJyZWFkIiwicGVybWlzc2lvbnMiOlsicmVhZCJdLCJleHAiOjE3NTgwODcyMzIsImlhdCI6MTc1ODA4MzYzMiwiaXNzIjoiZ2RjLXNlYXJjaC1pZGVudGl0eS1zZXJ2aWNlIn0.8-ffozf_8N1AmiWMgyG1y321K94EzKR_vyQ9VdhqcRM",
            "timeout": 30
        }
        
        # Ensure results directory exists
        os.makedirs("results", exist_ok=True)
        
        # Store all test results
        self.test_results = []
    
    def load_test_data(self):
        """Load test data from Excel or text file"""
        try:
            if self.test_data_file.endswith('.xlsx'):
                df = pd.read_excel(self.test_data_file)
            else:
                df = pd.read_csv(self.test_data_file, sep='\t')
            
            # Clean the data
            df = df.dropna(subset=['Search Term', 'Entity Type'])
            
            test_cases = []
            for index, row in df.iterrows():
                test_case = {
                    "search_term": row['Search Term'].strip(),
                    "entity_type": row['Entity Type'].strip(),
                    "expected_result_type": row.get('Expected Result Type', 'exact_match').strip(),
                    "notes": row.get('Notes', '').strip(),
                    "row_index": index
                }
                test_cases.append(test_case)
            
            print(f"Loaded {len(test_cases)} test cases from {self.test_data_file}")
            return test_cases
            
        except Exception as e:
            print(f"Error loading test data: {e}")
            return []
    
    def call_opensearch_api(self, search_term, entity_type):
        """Call OpenSearch API for a search term"""
        api_url = self.api_config["url"]
        api_key = self.api_config["api_key"]
        
        # API payload
        payload = {
            "query": search_term,
            "schemas": ["col", "rights", "mex", "watch", "soe", "pep", "sanction"],
            "limit": 100,
            "search_types": ["keyword", "phonetic", "similarity"]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        try:
            print(f"Calling OpenSearch API for '{search_term}' (Type: {entity_type})...")
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=self.api_config["timeout"])
            response.raise_for_status()
            
            api_result = response.json()
            print(f"API Response received successfully")
            
            # Transform API response
            return self.transform_opensearch_response(api_result)
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling OpenSearch API: {e}")
            return {"results": [], "total_hits": 0, "error": str(e)}
        except Exception as e:
            print(f"Error processing API response: {e}")
            return {"results": [], "total_hits": 0, "error": str(e)}
    
    def transform_opensearch_response(self, api_response):
        """Transform OpenSearch API response to standardized format"""
        try:
            results = []
            total_hits = 0
            
            if "results" in api_response and isinstance(api_response["results"], list):
                for result in api_response["results"]:
                    if "_source" in result:
                        source_data = result["_source"]
                        
                        # Extract name information
                        full_name = source_data.get("Full_Name", "")
                        first_name = source_data.get("First_Name", "")
                        last_name = source_data.get("Last_Name", "")
                        
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
                        total_hits += 1
                
                # Print summary
                schema_counts = {}
                for result in results:
                    schema = result["schema"].upper()
                    schema_counts[schema] = schema_counts.get(schema, 0) + 1
                
                for schema, count in schema_counts.items():
                    print(f"  {schema}: {count} records")
            
            return {
                "results": results,
                "total_hits": total_hits,
                "schema_counts": schema_counts if 'schema_counts' in locals() else {},
                "error": None
            }
            
        except Exception as e:
            print(f"Error transforming API response: {e}")
            return {"results": [], "total_hits": 0, "error": str(e)}
    
    def calculate_relevance_score(self, search_term, result_name):
        """Calculate relevance score between search term and result name with fuzzy matching"""
        if not search_term or not result_name:
            return 0.0
        
        # Normalize both strings
        search_normalized = self.normalize_text(search_term)
        result_normalized = self.normalize_text(result_name)
        
        # Exact match
        if search_normalized == result_normalized:
            return 1.0
        
        # Check if one contains the other (for abbreviations)
        if search_normalized in result_normalized or result_normalized in search_normalized:
            return 0.9
        
        # Sequence similarity
        similarity = SequenceMatcher(None, search_normalized, result_normalized).ratio()
        
        # Enhanced word-based matching
        search_words = set(search_normalized.split())
        result_words = set(result_normalized.split())
        
        if search_words and result_words:
            # Calculate different types of word overlap
            intersection = search_words.intersection(result_words)
            union = search_words.union(result_words)
            
            # Jaccard similarity (intersection over union)
            jaccard_score = len(intersection) / len(union) if union else 0
            
            # Coverage of search terms (how many search words are found in result)
            search_coverage = len(intersection) / len(search_words) if search_words else 0
            
            # Coverage of result terms (how many result words are found in search)
            result_coverage = len(intersection) / len(result_words) if result_words else 0
            
            # Fuzzy word matching for similar words (e.g., "aircraft" vs "air craft")
            fuzzy_matches = 0
            for search_word in search_words:
                for result_word in result_words:
                    # Check for partial matches and similar words
                    if (search_word in result_word or result_word in search_word or
                        SequenceMatcher(None, search_word, result_word).ratio() > 0.8):
                        fuzzy_matches += 1
                        break
            
            fuzzy_coverage = fuzzy_matches / len(search_words) if search_words else 0
            
            # Abbreviation detection (e.g., "NBD" matches "National Bank Dubai")
            abbreviation_score = self.check_abbreviation_match(search_words, result_words)
            
            # Combine all scores with weights
            word_score = (
                jaccard_score * 0.3 +
                search_coverage * 0.3 +
                fuzzy_coverage * 0.2 +
                abbreviation_score * 0.2
            )
            
            # Final combined score
            combined_score = (similarity * 0.4) + (word_score * 0.6)
        else:
            combined_score = similarity
        
        return min(combined_score, 1.0)  # Cap at 1.0
    
    def check_abbreviation_match(self, search_words, result_words):
        """Check if words could be abbreviations of each other"""
        abbreviation_score = 0.0
        
        # Convert to lists for easier processing
        search_list = list(search_words)
        result_list = list(result_words)
        
        # Check if any search word could be an abbreviation of result words
        for search_word in search_list:
            if len(search_word) <= 4:  # Potential abbreviation
                # Try to match with initials of result words
                initials = ''.join([word[0].lower() for word in result_list if word])
                if search_word.lower() == initials:
                    abbreviation_score = 1.0
                    break
                
                # Check partial initials match
                if len(search_word) >= 2 and initials.startswith(search_word.lower()):
                    abbreviation_score = 0.8
        
        # Check if any result word could be an abbreviation of search words  
        for result_word in result_list:
            if len(result_word) <= 4:  # Potential abbreviation
                # Try to match with initials of search words
                initials = ''.join([word[0].lower() for word in search_list if word])
                if result_word.lower() == initials:
                    abbreviation_score = max(abbreviation_score, 1.0)
                    break
                
                # Check partial initials match
                if len(result_word) >= 2 and initials.startswith(result_word.lower()):
                    abbreviation_score = max(abbreviation_score, 0.8)
        
        return abbreviation_score
    
    def normalize_text(self, text):
        """Normalize text for comparison"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra spaces and punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def evaluate_search_relevance(self, search_term, api_response, expected_result_type):
        """Evaluate if search results are relevant to the search term"""
        results = api_response.get("results", [])
        
        if not results:
            return {
                "status": "FAIL",
                "reason": "No results returned",
                "relevant_results": [],
                "irrelevant_results": [],
                "total_results": 0,
                "relevance_score": 0.0
            }
        
        relevant_results = []
        irrelevant_results = []
        relevance_scores = []
        
        # Define relevance thresholds based on expected result type (more lenient for fuzzy matching)
        thresholds = {
            "exact_match": 0.6,  # Lowered for fuzzy matching
            "abbreviation_match": 0.5,  # Lowered for abbreviations
            "full_name_match": 0.5,  # Lowered for name variations
            "name_variation": 0.5,  # Lowered for variations
            "transliteration_match": 0.4,  # Keep low for transliterations
            "specific_match": 0.3,  # Lowered for specific matches
            "broad_but_relevant": 0.25,  # Keep low for broad searches
            "relevant_only": 0.3  # Lowered for relevance checks
        }
        
        threshold = thresholds.get(expected_result_type, 0.5)
        
        for result in results:
            # Calculate relevance for full name
            full_name_score = self.calculate_relevance_score(search_term, result["full_name"])
            
            # Also check other name fields
            other_names_score = 0.0
            if result["other_names"]:
                other_names_score = self.calculate_relevance_score(search_term, result["other_names"])
            
            # Take the best score
            best_score = max(full_name_score, other_names_score)
            relevance_scores.append(best_score)
            
            result_with_score = result.copy()
            result_with_score["relevance_score"] = best_score
            result_with_score["relevance_explanation"] = f"Full name: {full_name_score:.2f}, Other names: {other_names_score:.2f}"
            
            if best_score >= threshold:
                relevant_results.append(result_with_score)
            else:
                irrelevant_results.append(result_with_score)
        
        # Calculate overall relevance
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
        
        # Determine status
        if not relevant_results:
            status = "FAIL"
            reason = f"No relevant results found (threshold: {threshold:.2f})"
        elif len(irrelevant_results) > len(relevant_results):
            status = "WARN"
            reason = f"More irrelevant ({len(irrelevant_results)}) than relevant ({len(relevant_results)}) results"
        else:
            status = "PASS"
            reason = f"Found {len(relevant_results)} relevant results"
        
        return {
            "status": status,
            "reason": reason,
            "relevant_results": relevant_results,
            "irrelevant_results": irrelevant_results,
            "total_results": len(results),
            "relevance_score": avg_relevance,
            "threshold": threshold
        }
    
    def run_relevance_test(self, test_case):
        """Run relevance test for a single test case"""
        search_term = test_case["search_term"]
        entity_type = test_case["entity_type"]
        expected_result_type = test_case["expected_result_type"]
        
        # Call API
        api_response = self.call_opensearch_api(search_term, entity_type)
        
        # Evaluate relevance
        relevance_evaluation = self.evaluate_search_relevance(search_term, api_response, expected_result_type)
        
        # Combine results
        test_result = {
            "test_case": test_case,
            "api_response": api_response,
            "relevance_evaluation": relevance_evaluation,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Print summary
        status = relevance_evaluation["status"]
        status_emoji = "✅" if status == "PASS" else "⚠️" if status == "WARN" else "❌"
        
        print(f"\n[{search_term}] Test completed - {status_emoji} {status}")
        print(f"  Results: {relevance_evaluation['total_results']} total, {len(relevance_evaluation['relevant_results'])} relevant, {len(relevance_evaluation['irrelevant_results'])} irrelevant")
        print(f"  Avg Relevance: {relevance_evaluation['relevance_score']:.2f} (threshold: {relevance_evaluation.get('threshold', 0.5):.2f})")
        print(f"  Reason: {relevance_evaluation['reason']}")
        
        # Show top relevant results
        if relevance_evaluation['relevant_results']:
            print(f"  🎯 Top Relevant Results:")
            for result in relevance_evaluation['relevant_results'][:3]:
                print(f"    • {result['full_name']} (ID: {result['id']}) - {result['relevance_score']:.2f}")
        
        # Show irrelevant results
        if relevance_evaluation['irrelevant_results']:
            print(f"  ❌ Irrelevant Results:")
            for result in relevance_evaluation['irrelevant_results'][:3]:
                print(f"    • {result['full_name']} (ID: {result['id']}) - {result['relevance_score']:.2f}")
        
        return test_result
    
    def generate_reports(self):
        """Generate Excel and HTML reports"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate Excel report
        excel_filename = f"results/search_relevance_report_{timestamp}.xlsx"
        self.generate_excel_report(excel_filename)
        
        # Generate HTML report
        html_filename = f"results/search_relevance_report_{timestamp}.html"
        self.generate_html_report(html_filename)
        
        print(f"\nReports generated:")
        print(f"  Excel: {excel_filename}")
        print(f"  HTML: {html_filename}")
    
    def generate_excel_report(self, filename):
        """Generate Excel report"""
        summary_data = []
        detailed_data = []
        
        for result in self.test_results:
            test_case = result["test_case"]
            evaluation = result["relevance_evaluation"]
            
            # Summary data
            summary_data.append({
                "Search Term": test_case["search_term"],
                "Entity Type": test_case["entity_type"],
                "Expected Type": test_case["expected_result_type"],
                "Status": evaluation["status"],
                "Total Results": evaluation["total_results"],
                "Relevant Results": len(evaluation["relevant_results"]),
                "Irrelevant Results": len(evaluation["irrelevant_results"]),
                "Avg Relevance Score": f"{evaluation['relevance_score']:.3f}",
                "Threshold": f"{evaluation.get('threshold', 0.5):.3f}",
                "Reason": evaluation["reason"],
                "Notes": test_case["notes"]
            })
            
            # Detailed results data
            for res in evaluation["relevant_results"] + evaluation["irrelevant_results"]:
                detailed_data.append({
                    "Search Term": test_case["search_term"],
                    "Result Name": res["full_name"],
                    "Result ID": res["id"],
                    "Schema": res["schema"],
                    "Relevance Score": f"{res['relevance_score']:.3f}",
                    "Status": "Relevant" if res in evaluation["relevant_results"] else "Irrelevant",
                    "Other Names": res["other_names"],
                    "API Score": res["score"]
                })
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Summary sheet
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Test Summary', index=False)
            
            # Detailed results sheet
            if detailed_data:
                detailed_df = pd.DataFrame(detailed_data)
                detailed_df.to_excel(writer, sheet_name='Detailed Results', index=False)
    
    def generate_html_report(self, filename):
        """Generate HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenSearch Relevance Test Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .test-case {{ margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; }}
        .test-header {{ padding: 15px; font-weight: bold; font-size: 1.1em; }}
        .test-pass {{ background-color: #d4edda; color: #155724; }}
        .test-warn {{ background-color: #fff3cd; color: #856404; }}
        .test-fail {{ background-color: #f8d7da; color: #721c24; }}
        .test-content {{ padding: 15px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .relevant {{ background-color: #d4edda; }}
        .irrelevant {{ background-color: #f8d7da; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenSearch Search Relevance Test Results</h1>
        <p><strong>Test Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>Total Test Cases:</strong> {len(self.test_results)}</p>
    </div>
"""
        
        # Overall statistics
        pass_count = sum(1 for r in self.test_results if r["relevance_evaluation"]["status"] == "PASS")
        warn_count = sum(1 for r in self.test_results if r["relevance_evaluation"]["status"] == "WARN")
        fail_count = sum(1 for r in self.test_results if r["relevance_evaluation"]["status"] == "FAIL")
        
        html_content += f"""
    <div class="header">
        <h2>Overall Results</h2>
        <p>✅ Passed: {pass_count} | ⚠️ Warnings: {warn_count} | ❌ Failed: {fail_count}</p>
    </div>
"""
        
        # Individual test cases
        for i, result in enumerate(self.test_results):
            test_case = result["test_case"]
            evaluation = result["relevance_evaluation"]
            
            status_class = f"test-{evaluation['status'].lower()}"
            status_emoji = "✅" if evaluation["status"] == "PASS" else "⚠️" if evaluation["status"] == "WARN" else "❌"
            
            html_content += f"""
    <div class="test-case">
        <div class="test-header {status_class}">
            {html.escape(test_case['search_term'])} ({test_case['entity_type']}) - {status_emoji} {evaluation['status']}
        </div>
        <div class="test-content">
            <p><strong>Expected:</strong> {test_case['expected_result_type']}</p>
            <p><strong>Results:</strong> {evaluation['total_results']} total, {len(evaluation['relevant_results'])} relevant, {len(evaluation['irrelevant_results'])} irrelevant</p>
            <p><strong>Avg Relevance:</strong> {evaluation['relevance_score']:.3f} (threshold: {evaluation.get('threshold', 0.5):.3f})</p>
            <p><strong>Reason:</strong> {html.escape(evaluation['reason'])}</p>
            
            <h4>Results Details:</h4>
            <table>
                <tr><th>Name</th><th>ID</th><th>Schema</th><th>Relevance</th><th>Status</th></tr>
"""
            
            # Show all results
            all_results = evaluation['relevant_results'] + evaluation['irrelevant_results']
            for res in all_results[:10]:  # Limit to first 10
                status_class = "relevant" if res in evaluation['relevant_results'] else "irrelevant"
                status_text = "Relevant" if res in evaluation['relevant_results'] else "Irrelevant"
                
                html_content += f"""
                <tr class="{status_class}">
                    <td>{html.escape(res['full_name'])}</td>
                    <td>{html.escape(res['id'])}</td>
                    <td>{html.escape(res['schema'])}</td>
                    <td>{res['relevance_score']:.3f}</td>
                    <td>{status_text}</td>
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
        """Run all relevance tests"""
        print("OpenSearch Search Relevance Tester")
        print("=" * 80)
        
        # Load test data
        test_cases = self.load_test_data()
        if not test_cases:
            print("No test cases loaded. Exiting.")
            return
        
        # Run tests
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] Testing: {test_case['search_term']}")
            test_result = self.run_relevance_test(test_case)
            self.test_results.append(test_result)
        
        # Generate reports
        print("\n" + "=" * 80)
        print("Generating reports...")
        self.generate_reports()
        
        # Print final summary
        pass_count = sum(1 for r in self.test_results if r["relevance_evaluation"]["status"] == "PASS")
        warn_count = sum(1 for r in self.test_results if r["relevance_evaluation"]["status"] == "WARN")
        fail_count = sum(1 for r in self.test_results if r["relevance_evaluation"]["status"] == "FAIL")
        
        print("\n" + "=" * 80)
        print("FINAL SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {pass_count}")
        print(f"⚠️ Warnings: {warn_count}")
        print(f"❌ Failed: {fail_count}")
        print(f"Success Rate: {(pass_count/len(self.test_results)*100):.1f}%")
        print("=" * 80)

if __name__ == "__main__":
    tester = SearchRelevanceTester()
    tester.run_all_tests()
