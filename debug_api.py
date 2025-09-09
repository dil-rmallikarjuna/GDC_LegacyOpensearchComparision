"""
Debug script to check the actual API response format.
"""
import json
from api_client import OpenSearchAPIClient

def debug_api_response():
    """Debug the API response to see the actual data structure."""
    client = OpenSearchAPIClient()
    
    print("Testing API with 'google' query...")
    response = client.search("google", limit=10)  # Limit to 10 for easier debugging
    
    print("\n" + "="*60)
    print("RAW API RESPONSE:")
    print("="*60)
    print(json.dumps(response, indent=2, default=str))
    
    if 'results' in response:
        print(f"\n📊 Found {len(response['results'])} results")
        print("\n" + "="*60)
        print("FIRST FEW RESULTS:")
        print("="*60)
        
        for i, result in enumerate(response['results'][:3], 1):
            print(f"\n--- Result {i} ---")
            print(f"Type: {type(result)}")
            print(f"Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            print(f"Raw data: {json.dumps(result, indent=2, default=str)}")
    else:
        print("❌ No 'results' key in response")
        print(f"Available keys: {list(response.keys())}")

if __name__ == "__main__":
    debug_api_response()
