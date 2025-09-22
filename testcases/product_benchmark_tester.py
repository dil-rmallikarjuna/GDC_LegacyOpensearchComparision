#!/usr/bin/env python3
"""
Product Benchmark Tester
Tests how well OpenSearch handles spelling variations, misspellings, and name variations
by comparing results between original names and their variations for product benchmarking.
"""

import pandas as pd
import requests
import json
import os
from datetime import datetime
import time

class ProductBenchmarkTester:
    def __init__(self, test_data_file="variation_test_cases.xlsx"):
        self.test_data_file = test_data_file
        
        # API Configuration
        self.api_config = {
            "url": "https://15krnwu233.execute-api.us-east-1.amazonaws.com/prod/search",
            "api_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJyZWFkLWNsaWVudCIsInJvbGUiOiJyZWFkIiwicGVybWlzc2lvbnMiOlsicmVhZCJdLCJleHAiOjE3NTgwODcyMzIsImlhdCI6MTc1ODA4MzYzMiwiaXNzIjoiZ2RjLXNlYXJjaC1pZGVudGl0eS1zZXJ2aWNlIn0.8-ffozf_8N1AmiWMgyG1y321K94EzKR_vyQ9VdhqcRM",
            "timeout": 30
        }
        
        self.test_results = []
        
        # Create results directory
        os.makedirs("results", exist_ok=True)
        
    def load_test_data(self):
        """Load product benchmark test data"""
        try:
            df = pd.read_excel(self.test_data_file)
            df = df.dropna(subset=['Search Term Original', 'Search Term Variation', 'Entity Type'])
            
            test_cases = []
            for index, row in df.iterrows():
                test_case = {
                    "original_term": row['Search Term Original'].strip(),
                    "variation_term": row['Search Term Variation'].strip(),
                    "entity_type": row['Entity Type'].strip(),
                    "test_category": row['Test Category'].strip(),
                    "expected_behavior": row['Expected Behavior'].strip()
                }
                test_cases.append(test_case)
            
            print(f"Loaded {len(test_cases)} product benchmark test cases")
            return test_cases
            
        except Exception as e:
            print(f"Error loading test data: {e}")
            return []
    
    def call_opensearch_api(self, search_term, entity_type):
        """Call OpenSearch API for a given search term"""
        try:
            payload = {
                "query": search_term,
                "schemas": ["col", "rights", "mex", "watch", "soe", "pep", "sanction"],
                "limit": 100,
                "search_types": ["keyword", "phonetic", "similarity"]
            }
            
            # Adjust for entity type
            if entity_type.upper() == 'P':  # Person
                payload["schemas"] = ["watch", "pep", "sanction", "mex"]
            elif entity_type.upper() == 'E':  # Entity
                payload["schemas"] = ["watch", "sanction", "soe", "icij", "rights"]
            
            print(f"  Calling API for '{search_term}' (Type: {entity_type})...")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_config['api_key']}"
            }
            
            response = requests.post(
                self.api_config["url"],
                headers=headers,
                json=payload,
                timeout=self.api_config["timeout"]
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                # Group by schema
                schema_counts = {}
                processed_results = []
                
                for result in results:
                    schema = result.get("_index", "unknown")
                    if schema not in schema_counts:
                        schema_counts[schema] = 0
                    schema_counts[schema] += 1
                    
                    source = result.get("_source", {})
                    
                    # Extract name information with correct field names
                    full_name = source.get("Full_Name", "")
                    first_name = source.get("First_Name", "")
                    last_name = source.get("Last_Name", "")
                    
                    # For ICIJ schema, prioritize name normalized field
                    name_normalized = source.get("name_normalized", "") or source.get("name normalized", "")
                    if schema.lower() == "icij" and name_normalized:
                        full_name = name_normalized
                    
                    # Construct full name if not present
                    if not full_name and (first_name or last_name):
                        full_name = f"{first_name} {last_name}".strip()
                    
                    processed_result = {
                        "id": source.get("ID", ""),
                        "schema": schema,
                        "full_name": full_name,
                        "first_name": first_name,
                        "last_name": last_name,
                        "other_names": source.get("Other_Names", ""),
                        "name_normalized": name_normalized,
                        "score": result.get("_score", 0)
                    }
                    processed_results.append(processed_result)
                
                # Print schema summary
                for schema, count in schema_counts.items():
                    print(f"    {schema.upper()}: {count} records")
                
                return {
                    "success": True,
                    "total_hits": len(results),
                    "results": processed_results,
                    "schema_counts": schema_counts
                }
            else:
                print(f"    API Error: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}", "results": [], "total_hits": 0}
                
        except Exception as e:
            print(f"    API Exception: {e}")
            return {"success": False, "error": str(e), "results": [], "total_hits": 0}
    
    def validate_icij_results(self, original_results, variation_results):
        """Validate ICIJ results using name normalized field for name matching"""
        icij_original = [r for r in original_results["results"] if r["schema"].lower() == "icij"]
        icij_variation = [r for r in variation_results["results"] if r["schema"].lower() == "icij"]
        
        if not icij_original and not icij_variation:
            return {
                "icij_score": 1.0,  # No ICIJ results to validate
                "icij_original_count": 0,
                "icij_variation_count": 0,
                "icij_common_count": 0,
                "icij_name_matches": 0,
                "icij_validation_details": "No ICIJ results found"
            }
        
        # Extract name normalized fields for comparison
        original_names = {r["id"]: r["name_normalized"] for r in icij_original if r["name_normalized"]}
        variation_names = {r["id"]: r["name_normalized"] for r in icij_variation if r["name_normalized"]}
        
        # Find common IDs
        original_ids = set(r["id"] for r in icij_original)
        variation_ids = set(r["id"] for r in icij_variation)
        common_ids = original_ids.intersection(variation_ids)
        
        # Count name matches in common results
        name_matches = 0
        for hit_id in common_ids:
            if hit_id in original_names and hit_id in variation_names:
                # Compare normalized names (case-insensitive)
                if original_names[hit_id].lower().strip() == variation_names[hit_id].lower().strip():
                    name_matches += 1
        
        # Calculate ICIJ validation score
        total_icij_results = len(original_ids.union(variation_ids))
        if total_icij_results == 0:
            icij_score = 1.0
        else:
            # Score based on name consistency in common results
            if len(common_ids) == 0:
                icij_score = 0.0  # No common ICIJ results
            else:
                icij_score = name_matches / len(common_ids) if len(common_ids) > 0 else 0.0
        
        return {
            "icij_score": icij_score,
            "icij_original_count": len(icij_original),
            "icij_variation_count": len(icij_variation),
            "icij_common_count": len(common_ids),
            "icij_name_matches": name_matches,
            "icij_validation_details": f"ICIJ: {len(common_ids)} common, {name_matches} name matches"
        }
    
    def compare_results(self, original_results, variation_results, test_case):
        """Compare results between original and variation searches"""
        original_ids = set(r["id"] for r in original_results["results"])
        variation_ids = set(r["id"] for r in variation_results["results"])
        
        # Find overlapping results
        common_ids = original_ids.intersection(variation_ids)
        original_only = original_ids - variation_ids
        variation_only = variation_ids - original_ids
        
        # Calculate similarity metrics
        total_unique_ids = len(original_ids.union(variation_ids))
        overlap_ratio = len(common_ids) / total_unique_ids if total_unique_ids > 0 else 0
        
        # ICIJ-specific validation
        icij_validation = self.validate_icij_results(original_results, variation_results)
        
        # Determine test result with ICIJ validation consideration
        if overlap_ratio >= 0.8 and icij_validation["icij_score"] >= 0.8:  # 80% or more overlap + good ICIJ validation
            test_result = "PASS"
            result_reason = f"High overlap: {overlap_ratio:.1%} common results, ICIJ validation: {icij_validation['icij_score']:.1%}"
        elif overlap_ratio >= 0.5 and icij_validation["icij_score"] >= 0.5:  # 50-79% overlap + moderate ICIJ validation
            test_result = "WARN"
            result_reason = f"Moderate overlap: {overlap_ratio:.1%} common results, ICIJ validation: {icij_validation['icij_score']:.1%}"
        else:  # Low overlap or poor ICIJ validation
            test_result = "FAIL"
            result_reason = f"Low overlap: {overlap_ratio:.1%} common results, ICIJ validation: {icij_validation['icij_score']:.1%}"
        
        return {
            "test_result": test_result,
            "result_reason": result_reason,
            "overlap_ratio": overlap_ratio,
            "common_count": len(common_ids),
            "original_only_count": len(original_only),
            "variation_only_count": len(variation_only),
            "common_ids": list(common_ids),
            "original_only_ids": list(original_only),
            "variation_only_ids": list(variation_only),
            "icij_validation": icij_validation
        }
    
    def run_benchmark_test(self, test_case):
        """Run a single benchmark test"""
        print(f"\n{'='*80}")
        print(f"Testing: {test_case['original_term']} vs {test_case['variation_term']}")
        print(f"Category: {test_case['test_category']}")
        print(f"Expected: {test_case['expected_behavior']}")
        print(f"{'='*80}")
        
        # Call API for original term
        original_results = self.call_opensearch_api(test_case['original_term'], test_case['entity_type'])
        time.sleep(0.5)  # Rate limiting
        
        # Call API for variation term
        variation_results = self.call_opensearch_api(test_case['variation_term'], test_case['entity_type'])
        time.sleep(0.5)  # Rate limiting
        
        # Compare results
        comparison = self.compare_results(original_results, variation_results, test_case)
        
        # Print summary
        status_emoji = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}
        print(f"\n{status_emoji.get(comparison['test_result'], '❓')} Test Result: {comparison['test_result']}")
        print(f"Reason: {comparison['result_reason']}")
        print(f"Original hits: {original_results['total_hits']}")
        print(f"Variation hits: {variation_results['total_hits']}")
        print(f"Common results: {comparison['common_count']}")
        print(f"Original only: {comparison['original_only_count']}")
        print(f"Variation only: {comparison['variation_only_count']}")
        
        # Print ICIJ validation details
        icij_val = comparison.get('icij_validation', {})
        if icij_val.get('icij_original_count', 0) > 0 or icij_val.get('icij_variation_count', 0) > 0:
            print(f"\n🔍 ICIJ Validation:")
            print(f"  ICIJ Original: {icij_val.get('icij_original_count', 0)}")
            print(f"  ICIJ Variation: {icij_val.get('icij_variation_count', 0)}")
            print(f"  ICIJ Common: {icij_val.get('icij_common_count', 0)}")
            print(f"  Name Matches: {icij_val.get('icij_name_matches', 0)}")
            print(f"  ICIJ Score: {icij_val.get('icij_score', 0):.1%}")
            print(f"  Details: {icij_val.get('icij_validation_details', 'N/A')}")
        
        return {
            "test_case": test_case,
            "original_results": original_results,
            "variation_results": variation_results,
            "comparison": comparison,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def generate_excel_report(self):
        """Generate Excel report with benchmark results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/product_benchmark_report_{timestamp}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = []
            detailed_data = []
            
            for result in self.test_results:
                test_case = result["test_case"]
                comparison = result["comparison"]
                original = result["original_results"]
                variation = result["variation_results"]
                
                # Get ICIJ validation data
                icij_val = comparison.get('icij_validation', {})
                
                summary_data.append({
                    "Original Term": test_case["original_term"],
                    "Variation Term": test_case["variation_term"],
                    "Entity Type": test_case["entity_type"],
                    "Test Category": test_case["test_category"],
                    "Test Result": comparison["test_result"],
                    "Overlap Ratio": f"{comparison['overlap_ratio']:.1%}",
                    "Original Hits": original["total_hits"],
                    "Variation Hits": variation["total_hits"],
                    "Common Results": comparison["common_count"],
                    "Original Only": comparison["original_only_count"],
                    "Variation Only": comparison["variation_only_count"],
                    "ICIJ Original Count": icij_val.get('icij_original_count', 0),
                    "ICIJ Variation Count": icij_val.get('icij_variation_count', 0),
                    "ICIJ Common Count": icij_val.get('icij_common_count', 0),
                    "ICIJ Name Matches": icij_val.get('icij_name_matches', 0),
                    "ICIJ Score": f"{icij_val.get('icij_score', 0):.1%}",
                    "Reason": comparison["result_reason"]
                })
                
                # Create detailed hit comparison with names
                original_hits = {r["id"]: r for r in original["results"]}
                variation_hits = {r["id"]: r for r in variation["results"]}
                all_ids = set(original_hits.keys()) | set(variation_hits.keys())
                
                for hit_id in all_ids:
                    original_result = original_hits.get(hit_id, {})
                    variation_result = variation_hits.get(hit_id, {})
                    
                    original_name = original_result.get("full_name", "")
                    variation_name = variation_result.get("full_name", "")
                    original_schema = original_result.get("schema", "")
                    variation_schema = variation_result.get("schema", "")
                    original_name_norm = original_result.get("name_normalized", "")
                    variation_name_norm = variation_result.get("name_normalized", "")
                    
                    if hit_id in comparison["common_ids"]:
                        status = "Common"
                    elif hit_id in comparison["original_only_ids"]:
                        status = "Original Only"
                    else:
                        status = "Variation Only"
                    
                    # ICIJ-specific validation status
                    icij_status = ""
                    if original_schema.lower() == "icij" or variation_schema.lower() == "icij":
                        if original_name_norm and variation_name_norm:
                            if original_name_norm.lower().strip() == variation_name_norm.lower().strip():
                                icij_status = "✅ Name Match"
                            else:
                                icij_status = "❌ Name Mismatch"
                        else:
                            icij_status = "⚠️ Missing Name Normalized"
                    
                    detailed_data.append({
                        "Original Term": test_case["original_term"],
                        "Variation Term": test_case["variation_term"],
                        "Hit ID": hit_id,
                        "Original Name": original_name,
                        "Variation Name": variation_name,
                        "Original Schema": original_schema,
                        "Variation Schema": variation_schema,
                        "Original Name Normalized": original_name_norm,
                        "Variation Name Normalized": variation_name_norm,
                        "Status": status,
                        "ICIJ Validation": icij_status
                    })
            
            # Write summary sheet
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            
            # Write detailed sheet
            detailed_df = pd.DataFrame(detailed_data)
            detailed_df.to_excel(writer, sheet_name="Detailed Comparison", index=False)
            
            # Write category analysis
            category_analysis = summary_df.groupby('Test Category').agg({
                'Test Result': lambda x: (x == 'PASS').sum(),
                'Original Term': 'count',
                'Overlap Ratio': lambda x: pd.Series([float(val.strip('%'))/100 for val in x]).mean()
            }).rename(columns={
                'Test Result': 'Passed Tests',
                'Original Term': 'Total Tests',
                'Overlap Ratio': 'Average Overlap'
            })
            category_analysis['Pass Rate'] = category_analysis['Passed Tests'] / category_analysis['Total Tests']
            category_analysis['Average Overlap'] = category_analysis['Average Overlap'].apply(lambda x: f"{x:.1%}")
            category_analysis['Pass Rate'] = category_analysis['Pass Rate'].apply(lambda x: f"{x:.1%}")
            
            category_analysis.to_excel(writer, sheet_name="Category Analysis")
        
        print(f"\n📊 Excel report generated: {filename}")
        return filename
    
    def generate_html_report(self):
        """Generate HTML report with benchmark results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/product_benchmark_report_{timestamp}.html"
        
        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["comparison"]["test_result"] == "PASS")
        warned_tests = sum(1 for r in self.test_results if r["comparison"]["test_result"] == "WARN")
        failed_tests = sum(1 for r in self.test_results if r["comparison"]["test_result"] == "FAIL")
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Product Benchmark Test Report</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .summary {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .test-case {{ background: white; margin: 20px 0; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .test-pass {{ border-left: 5px solid #28a745; }}
        .test-warn {{ border-left: 5px solid #ffc107; }}
        .test-fail {{ border-left: 5px solid #dc3545; }}
        .comparison-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        .comparison-table th, .comparison-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        .comparison-table th {{ background-color: #f8f9fa; font-weight: bold; }}
        .status-pass {{ color: #28a745; font-weight: bold; }}
        .status-warn {{ color: #ffc107; font-weight: bold; }}
        .status-fail {{ color: #dc3545; font-weight: bold; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
        .metric-label {{ font-size: 14px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔄 Product Benchmark Test Report</h1>
        <p>Testing OpenSearch handling of spelling variations, misspellings, and name variations for product benchmarking</p>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Test Summary</h2>
        <div class="metric">
            <div class="metric-value">{total_tests}</div>
            <div class="metric-label">Total Tests</div>
        </div>
        <div class="metric">
            <div class="metric-value" style="color: #28a745;">{passed_tests}</div>
            <div class="metric-label">Passed</div>
        </div>
        <div class="metric">
            <div class="metric-value" style="color: #ffc107;">{warned_tests}</div>
            <div class="metric-label">Warnings</div>
        </div>
        <div class="metric">
            <div class="metric-value" style="color: #dc3545;">{failed_tests}</div>
            <div class="metric-label">Failed</div>
        </div>
        <div class="metric">
            <div class="metric-value">{(passed_tests/total_tests*100):.1f}%</div>
            <div class="metric-label">Success Rate</div>
        </div>
    </div>
"""
        
        # Add individual test results
        for result in self.test_results:
            test_case = result["test_case"]
            comparison = result["comparison"]
            original = result["original_results"]
            variation = result["variation_results"]
            
            status_class = f"test-{comparison['test_result'].lower()}"
            status_emoji = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}
            
            html_content += f"""
    <div class="test-case {status_class}">
        <h3>{status_emoji.get(comparison['test_result'], '❓')} {test_case['original_term']} vs {test_case['variation_term']}</h3>
        <p><strong>Category:</strong> {test_case['test_category']}</p>
        <p><strong>Expected:</strong> {test_case['expected_behavior']}</p>
        <p><strong>Result:</strong> <span class="status-{comparison['test_result'].lower()}">{comparison['test_result']}</span> - {comparison['result_reason']}</p>
        
        <table class="comparison-table">
            <tr>
                <th>Metric</th>
                <th>Original Term</th>
                <th>Variation Term</th>
                <th>Comparison</th>
            </tr>
            <tr>
                <td><strong>Search Term</strong></td>
                <td>{test_case['original_term']}</td>
                <td>{test_case['variation_term']}</td>
                <td>-</td>
            </tr>
            <tr>
                <td><strong>Total Hits</strong></td>
                <td>{original['total_hits']}</td>
                <td>{variation['total_hits']}</td>
                <td>{comparison['common_count']} common</td>
            </tr>
            <tr>
                <td><strong>Overlap Ratio</strong></td>
                <td colspan="2">{comparison['overlap_ratio']:.1%}</td>
                <td>{comparison['common_count']} / {comparison['common_count'] + comparison['original_only_count'] + comparison['variation_only_count']} total unique</td>
            </tr>
            <tr>
                <td><strong>Unique Results</strong></td>
                <td>{comparison['original_only_count']} original only</td>
                <td>{comparison['variation_only_count']} variation only</td>
                <td>{comparison['common_count']} in both</td>
            </tr>"""
            
            # Add ICIJ validation row if applicable
            icij_val = comparison.get('icij_validation', {})
            if icij_val.get('icij_original_count', 0) > 0 or icij_val.get('icij_variation_count', 0) > 0:
                html_content += f"""
            <tr style="background-color: #e8f4fd;">
                <td><strong>ICIJ Validation</strong></td>
                <td>{icij_val.get('icij_original_count', 0)} ICIJ results</td>
                <td>{icij_val.get('icij_variation_count', 0)} ICIJ results</td>
                <td>{icij_val.get('icij_common_count', 0)} common, {icij_val.get('icij_name_matches', 0)} name matches ({icij_val.get('icij_score', 0):.1%})</td>
            </tr>"""
            
            html_content += """
        </table>
        
        <h4>📋 Detailed Hit Comparison</h4>
        <table class="comparison-table">
            <tr>
                <th>Hit ID</th>
                <th>Original Search Name</th>
                <th>Variation Search Name</th>
                <th>Original Schema</th>
                <th>Variation Schema</th>
                <th>Original Name Normalized</th>
                <th>Variation Name Normalized</th>
                <th>Status</th>
                <th>ICIJ Validation</th>
            </tr>"""
            
            # Add detailed hit comparison
            original_hits = {r["id"]: r for r in original["results"]}
            variation_hits = {r["id"]: r for r in variation["results"]}
            all_ids = set(original_hits.keys()) | set(variation_hits.keys())
            
            for hit_id in sorted(all_ids):
                original_result = original_hits.get(hit_id, {})
                variation_result = variation_hits.get(hit_id, {})
                
                original_name = original_result.get("full_name", "")
                variation_name = variation_result.get("full_name", "")
                original_schema = original_result.get("schema", "")
                variation_schema = variation_result.get("schema", "")
                original_name_norm = original_result.get("name_normalized", "")
                variation_name_norm = variation_result.get("name_normalized", "")
                
                if hit_id in comparison["common_ids"]:
                    status = "✅ Common"
                    row_class = "style='background-color: #d4edda;'"
                elif hit_id in comparison["original_only_ids"]:
                    status = "🔵 Original Only"
                    row_class = "style='background-color: #cce5ff;'"
                else:
                    status = "🟡 Variation Only"
                    row_class = "style='background-color: #fff3cd;'"
                
                # ICIJ-specific validation status
                icij_status = ""
                if original_schema.lower() == "icij" or variation_schema.lower() == "icij":
                    if original_name_norm and variation_name_norm:
                        if original_name_norm.lower().strip() == variation_name_norm.lower().strip():
                            icij_status = "✅ Name Match"
                        else:
                            icij_status = "❌ Name Mismatch"
                    else:
                        icij_status = "⚠️ Missing Name Normalized"
                
                html_content += f"""
            <tr {row_class}>
                <td>{hit_id}</td>
                <td>{original_name if original_name else '<em>Not found</em>'}</td>
                <td>{variation_name if variation_name else '<em>Not found</em>'}</td>
                <td>{original_schema}</td>
                <td>{variation_schema}</td>
                <td>{original_name_norm if original_name_norm else '<em>N/A</em>'}</td>
                <td>{variation_name_norm if variation_name_norm else '<em>N/A</em>'}</td>
                <td>{status}</td>
                <td>{icij_status if icij_status else '<em>N/A</em>'}</td>
            </tr>"""
            
            html_content += """
        </table>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📄 HTML report generated: {filename}")
        return filename
    
    def run_icij_validation_test(self, search_term):
        """Run a specific ICIJ validation test"""
        print(f"\n🔍 ICIJ Validation Test for: '{search_term}'")
        print("="*60)
        
        # Call API with ICIJ schema specifically
        payload = {
            "query": search_term,
            "schemas": ["icij"],
            "limit": 100,
            "search_types": ["keyword", "phonetic", "similarity"]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_config['api_key']}"
        }
        
        try:
            response = requests.post(
                self.api_config["url"],
                headers=headers,
                json=payload,
                timeout=self.api_config["timeout"]
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                print(f"Found {len(results)} ICIJ results")
                
                for i, result in enumerate(results, 1):
                    source = result.get("_source", {})
                    name_normalized = source.get("name_normalized", "") or source.get("name normalized", "")
                    full_name = source.get("Full_Name", "") or source.get("name", "")
                    other_names = source.get("Other_Names", "") or source.get("otherNames", "")
                    
                    print(f"\n{i}. ID: {source.get('ID', 'N/A')}")
                    print(f"   Name Normalized: {name_normalized}")
                    print(f"   Full Name: {full_name}")
                    print(f"   Other Names: {other_names}")
                    print(f"   Score: {result.get('_score', 0):.2f}")
                
                return results
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"API Exception: {e}")
            return []
    
    def run_all_tests(self):
        """Run all product benchmark tests"""
        print("🔄 Product Benchmark Tester")
        print("="*80)
        
        test_cases = self.load_test_data()
        if not test_cases:
            print("No test cases loaded. Exiting.")
            return
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] Processing: {test_case['original_term']} vs {test_case['variation_term']}")
            test_result = self.run_benchmark_test(test_case)
            self.test_results.append(test_result)
        
        # Generate reports
        self.generate_excel_report()
        self.generate_html_report()
        
        # Final summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["comparison"]["test_result"] == "PASS")
        warned_tests = sum(1 for r in self.test_results if r["comparison"]["test_result"] == "WARN")
        failed_tests = sum(1 for r in self.test_results if r["comparison"]["test_result"] == "FAIL")
        
        # ICIJ validation summary
        icij_tests = [r for r in self.test_results if r["comparison"].get("icij_validation", {}).get("icij_original_count", 0) > 0 or r["comparison"].get("icij_validation", {}).get("icij_variation_count", 0) > 0]
        icij_passed = sum(1 for r in icij_tests if r["comparison"].get("icij_validation", {}).get("icij_score", 0) >= 0.8)
        
        print(f"\n{'='*80}")
        print(f"🔄 PRODUCT BENCHMARK TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"⚠️ Warnings: {warned_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if icij_tests:
            print(f"\n🔍 ICIJ VALIDATION SUMMARY")
            print(f"ICIJ Tests: {len(icij_tests)}")
            print(f"ICIJ Passed: {icij_passed}")
            print(f"ICIJ Success Rate: {(icij_passed/len(icij_tests)*100):.1f}%")
        
        print(f"{'='*80}")

if __name__ == "__main__":
    tester = ProductBenchmarkTester()
    tester.run_all_tests()
