#!/usr/bin/env python3
"""
API Security Tester for OpenSearch Endpoint
Tests various input patterns to identify potential vulnerabilities
"""

import requests
import json
import time
from datetime import datetime
from security_test_queries import get_injection_test_queries, get_edge_case_queries

class APISecurityTester:
    def __init__(self):
        self.api_config = {
            "url": "https://15krnwu233.execute-api.us-east-1.amazonaws.com/prod/search",
            "api_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJyZWFkLWNsaWVudCIsInJvbGUiOiJyZWFkIiwicGVybWlzc2lvbnMiOlsicmVhZCJdLCJleHAiOjE3NTgwODcyMzIsImlhdCI6MTc1ODA4MzYzMiwiaXNzIjoiZ2RjLXNlYXJjaC1pZGVudGl0eS1zZXJ2aWNlIn0.8-ffozf_8N1AmiWMgyG1y321K94EzKR_vyQ9VdhqcRM",
            "timeout": 10
        }
        self.test_results = []
        
    def test_query(self, test_query, test_type="injection"):
        """Test a single query against the API"""
        payload = {
            "query": test_query,
            "schemas": ["col", "rights", "mex", "watch", "soe", "pep", "sanction"],
            "limit": 10,  # Reduced limit for security testing
            "search_types": ["keyword", "phonetic", "similarity"]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_config['api_key']}"
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                self.api_config["url"], 
                json=payload, 
                headers=headers, 
                timeout=self.api_config["timeout"]
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            result = {
                "query": test_query,
                "test_type": test_type,
                "status_code": response.status_code,
                "response_time": response_time,
                "success": response.status_code == 200,
                "timestamp": datetime.now().isoformat()
            }
            
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    result["result_count"] = len(json_response.get("results", []))
                    result["response_size"] = len(response.text)
                except:
                    result["result_count"] = 0
                    result["response_size"] = len(response.text)
            else:
                result["error_message"] = response.text[:200]  # First 200 chars of error
                result["result_count"] = 0
                result["response_size"] = len(response.text)
            
            return result
            
        except requests.exceptions.Timeout:
            return {
                "query": test_query,
                "test_type": test_type,
                "status_code": "TIMEOUT",
                "response_time": self.api_config["timeout"],
                "success": False,
                "error_message": "Request timed out",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "query": test_query,
                "test_type": test_type,
                "status_code": "ERROR",
                "response_time": time.time() - start_time,
                "success": False,
                "error_message": str(e)[:200],
                "timestamp": datetime.now().isoformat()
            }
    
    def run_injection_tests(self, limit=10):
        """Run injection attack tests"""
        print("🚨 Running Injection Tests...")
        print("=" * 60)
        
        injection_queries = get_injection_test_queries()[:limit]  # Limit for safety
        
        for i, query in enumerate(injection_queries, 1):
            print(f"[{i}/{len(injection_queries)}] Testing: {repr(query[:50])}")
            
            result = self.test_query(query, "injection")
            self.test_results.append(result)
            
            # Print immediate result
            if result["success"]:
                print(f"  ✅ Status: {result['status_code']} | Results: {result.get('result_count', 0)} | Time: {result['response_time']:.2f}s")
            else:
                print(f"  ❌ Status: {result['status_code']} | Error: {result.get('error_message', 'Unknown')}")
            
            # Rate limiting - be respectful
            time.sleep(0.5)
    
    def run_edge_case_tests(self, limit=15):
        """Run edge case tests"""
        print("\n✅ Running Edge Case Tests...")
        print("=" * 60)
        
        edge_queries = get_edge_case_queries()[:limit]
        
        for i, query in enumerate(edge_queries, 1):
            print(f"[{i}/{len(edge_queries)}] Testing: {repr(query)}")
            
            result = self.test_query(query, "edge_case")
            self.test_results.append(result)
            
            # Print immediate result
            if result["success"]:
                print(f"  ✅ Status: {result['status_code']} | Results: {result.get('result_count', 0)} | Time: {result['response_time']:.2f}s")
            else:
                print(f"  ❌ Status: {result['status_code']} | Error: {result.get('error_message', 'Unknown')}")
            
            # Rate limiting
            time.sleep(0.3)
    
    def analyze_results(self):
        """Analyze test results for security issues"""
        print("\n📊 SECURITY ANALYSIS")
        print("=" * 60)
        
        # Categorize results
        successful_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        injection_tests = [r for r in self.test_results if r["test_type"] == "injection"]
        edge_tests = [r for r in self.test_results if r["test_type"] == "edge_case"]
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Successful: {len(successful_tests)}")
        print(f"❌ Failed: {len(failed_tests)}")
        print(f"🚨 Injection Tests: {len(injection_tests)}")
        print(f"✅ Edge Case Tests: {len(edge_tests)}")
        
        # Look for anomalies
        print(f"\n🔍 ANOMALY DETECTION:")
        
        # Check for different status codes
        status_codes = {}
        for result in self.test_results:
            code = result["status_code"]
            status_codes[code] = status_codes.get(code, 0) + 1
        
        print(f"Status Code Distribution:")
        for code, count in status_codes.items():
            print(f"  {code}: {count} requests")
        
        # Check for unusually long response times
        response_times = [r["response_time"] for r in successful_tests]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            print(f"\nResponse Times:")
            print(f"  Average: {avg_time:.2f}s")
            print(f"  Maximum: {max_time:.2f}s")
            
            # Flag slow responses
            slow_responses = [r for r in successful_tests if r["response_time"] > avg_time * 3]
            if slow_responses:
                print(f"  ⚠️ Unusually slow responses: {len(slow_responses)}")
        
        # Check for error patterns
        error_messages = {}
        for result in failed_tests:
            error = result.get("error_message", "Unknown")[:50]
            error_messages[error] = error_messages.get(error, 0) + 1
        
        if error_messages:
            print(f"\nError Patterns:")
            for error, count in error_messages.items():
                print(f"  {count}x: {error}")
        
        # Security recommendations
        print(f"\n🛡️ SECURITY RECOMMENDATIONS:")
        if len(failed_tests) > len(successful_tests) * 0.1:  # More than 10% failures
            print("  ⚠️ High failure rate - API may be rejecting malicious input (GOOD)")
        else:
            print("  ✅ Low failure rate - API appears stable")
        
        if any(r["status_code"] == 500 for r in failed_tests):
            print("  🚨 Server errors detected - may reveal system information")
        
        if max(response_times) > 5.0 if response_times else False:
            print("  ⚠️ Some queries cause slow responses - potential DoS vector")
    
    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/security_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")

def main():
    print("🔒 API Security Tester")
    print("=" * 60)
    print("⚠️  WARNING: Only test APIs you own or have permission to test!")
    print("=" * 60)
    
    tester = APISecurityTester()
    
    # Run limited tests to be respectful
    tester.run_injection_tests(limit=5)  # Only first 5 injection tests
    tester.run_edge_case_tests(limit=10)  # Only first 10 edge cases
    
    # Analyze results
    tester.analyze_results()
    
    # Save results
    tester.save_results()

if __name__ == "__main__":
    main()

