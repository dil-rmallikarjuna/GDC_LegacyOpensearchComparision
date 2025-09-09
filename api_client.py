"""
API client for the new OpenSearch API.
"""
import requests
import json
import time
from typing import Dict, List, Optional
from config import Config

class OpenSearchAPIClient:
    """Client for interacting with the OpenSearch API."""
    
    def __init__(self):
        self.base_url = Config.API_URL
        self.headers = Config.API_HEADERS
        
    def search(self, query: str, schemas: Optional[List[str]] = None, 
               search_types: Optional[List[str]] = None, limit: int = 1000) -> Dict:
        """
        Perform a search using the OpenSearch API.
        
        Args:
            query: Search query string
            schemas: List of schemas to search in
            search_types: List of search types to use
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing the API response
        """
        if schemas is None:
            schemas = Config.DEFAULT_SCHEMAS
        if search_types is None:
            search_types = Config.DEFAULT_SEARCH_TYPES
            
        payload = {
            "query": query,
            "schemas": schemas,
            "limit": limit,
            "search_types": search_types
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return {"error": str(e), "results": []}
    
    def batch_search(self, queries: List[str], **kwargs) -> Dict[str, Dict]:
        """
        Perform multiple searches in batch.
        
        Args:
            queries: List of query strings
            **kwargs: Additional arguments to pass to search method
            
        Returns:
            Dictionary mapping queries to their results
        """
        results = {}
        for query in queries:
            print(f"Searching for: {query}")
            results[query] = self.search(query, **kwargs)
            time.sleep(0.1)  # Small delay to avoid rate limiting
        return results
