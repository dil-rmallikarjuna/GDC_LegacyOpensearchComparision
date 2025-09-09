"""
Reference loader for search term definitions.
"""
import os
from typing import Dict, List

class SearchReferenceLoader:
    """Loads and manages search reference definitions."""
    
    def __init__(self, reference_file: str = "search_reference.txt"):
        self.reference_file = reference_file
        self.references = {}
        self.load_references()
    
    def load_references(self):
        """Load search references from the text file."""
        if not os.path.exists(self.reference_file):
            print(f"Warning: Reference file {self.reference_file} not found")
            return
        
        try:
            with open(self.reference_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse line format: QUERY_TERM: description
                    if ':' not in line:
                        print(f"Warning: Invalid format on line {line_num}: {line}")
                        continue
                    
                    query_term, description = line.split(':', 1)
                    query_term = query_term.strip().upper()
                    description = description.strip()
                    
                    # Split description into keywords
                    keywords = [keyword.strip().lower() for keyword in description.split(',')]
                    keywords = [k for k in keywords if k]  # Remove empty strings
                    
                    self.references[query_term] = {
                        'description': description,
                        'keywords': keywords
                    }
            
            print(f"Loaded {len(self.references)} search references")
            
        except Exception as e:
            print(f"Error loading reference file: {e}")
    
    def get_reference_keywords(self, query: str) -> List[str]:
        """Get reference keywords for a query term."""
        query_upper = query.strip().upper()
        if query_upper in self.references:
            return self.references[query_upper]['keywords']
        return []
    
    def has_reference(self, query: str) -> bool:
        """Check if a query has a reference definition."""
        return query.strip().upper() in self.references
    
    def get_all_queries(self) -> List[str]:
        """Get all defined query terms."""
        return list(self.references.keys())
    
    def print_references(self):
        """Print all loaded references for debugging."""
        print("\nLoaded Search References:")
        print("=" * 50)
        for query, ref in self.references.items():
            print(f"{query}:")
            print(f"  Description: {ref['description']}")
            print(f"  Keywords: {ref['keywords'][:5]}...")  # Show first 5 keywords
            print()

if __name__ == "__main__":
    # Test the reference loader
    loader = SearchReferenceLoader()
    loader.print_references()
    
    # Test keyword lookup
    test_query = "apple"
    keywords = loader.get_reference_keywords(test_query)
    print(f"\nKeywords for '{test_query}': {keywords[:10]}...")  # Show first 10
