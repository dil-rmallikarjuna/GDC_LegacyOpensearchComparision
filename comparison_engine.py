"""
Comparison engine to analyze search results and identify true matches vs false positives.
"""
from typing import Dict, List, Tuple
import difflib
from dataclasses import dataclass
from reference_loader import SearchReferenceLoader
from llm_analyzer import LLMRelevanceAnalyzer

@dataclass
class ComparisonResult:
    """Data class for storing comparison results."""
    query: str
    old_results_count: int
    new_results_count: int
    common_matches: List[Dict]
    only_in_old: List[Dict]
    only_in_new: List[Dict]
    similarity_score: float
    true_positives: int
    false_positives: int
    false_negatives: int

class ComparisonEngine:
    """Engine for comparing old and new search results."""
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.reference_loader = SearchReferenceLoader()
        self.llm_analyzer = LLMRelevanceAnalyzer()
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings."""
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def extract_key_fields(self, result: Dict) -> Dict:
        """
        Extract key fields from an OpenSearch result.
        
        Args:
            result: Search result dictionary from OpenSearch API
            
        Returns:
            Dictionary with standardized key fields
        """
        # OpenSearch returns results with _source containing the actual data
        source_data = result.get("_source", result)
        
        # Extract name from available fields
        name = (source_data.get("Full_Name") or 
                f"{source_data.get('First_Name', '')} {source_data.get('Last_Name', '')}".strip() or
                "Unknown Entity")
        
        return {
            "id": source_data.get("ID", result.get("_id", "")),
            "name": name,
            "type": source_data.get("Entity_Type", "Unknown"),
            "score": result.get("_score", source_data.get("score", 0)),
            "raw_data": result
        }
    
    
    def analyze_opensearch_relevance(self, query: str, results: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Analyze OpenSearch results for relevance using LLM and web scraping.
        
        Args:
            query: The search query
            results: OpenSearch results
            
        Returns:
            Tuple of (relevant_results, irrelevant_results)
        """
        print(f"🤖 Using LLM analysis for {len(results)} results...")
        
        relevant_results = []
        irrelevant_results = []
        
        # Map query to company name for LLM analysis
        company_mapping = {
            'general electric': 'General Electric',
            'ibm': 'IBM',
            'johnson': 'Johnson & Johnson',
            'coca-cola': 'Coca-Cola',
            'procter': 'Procter & Gamble',
            'microsoft': 'Microsoft',
            'apple': 'Apple',
            'google': 'Google',
            'tesla': 'Tesla',
            'amazon': 'Amazon'
        }
        
        reference_company = company_mapping.get(query.lower().strip(), query.title())
        
        # Analyze each result with LLM
        for i, result in enumerate(results):
            entity_name = result.get('name', 'Unknown Entity')
            
            # Show progress for long lists
            if i % 50 == 0 and i > 0:
                print(f"   Analyzed {i}/{len(results)} results...")
            
            try:
                is_relevant, explanation, confidence = self.llm_analyzer.analyze_relevance(
                    entity_name, reference_company, query
                )
                
                # Add analysis metadata to result
                result['llm_analysis'] = {
                    'is_relevant': is_relevant,
                    'explanation': explanation,
                    'confidence': confidence
                }
                
                if is_relevant and confidence >= 0.7:  # High confidence threshold
                    relevant_results.append(result)
                else:
                    irrelevant_results.append(result)
                    
            except Exception as e:
                print(f"   Error analyzing '{entity_name}': {e}")
                # Default to irrelevant if analysis fails
                irrelevant_results.append(result)
        
        print(f"   ✅ LLM Analysis complete: {len(relevant_results)} relevant, {len(irrelevant_results)} irrelevant")
        return relevant_results, irrelevant_results
    
    def analyze_results(self, query: str, old_results: List[Dict], new_results: List[Dict]) -> ComparisonResult:
        """
        Analyze OpenSearch results for relevance (ignoring old database results).
        
        Args:
            query: The search query
            old_results: Ignored - not used in this analysis
            new_results: Results from OpenSearch API
            
        Returns:
            ComparisonResult object with relevance analysis
        """
        # Extract standardized results from OpenSearch
        standardized_results = [self.extract_key_fields(r) for r in new_results]
        
        # Analyze relevance
        relevant_results, irrelevant_results = self.analyze_opensearch_relevance(query, standardized_results)
        
        # Calculate metrics based on relevance
        true_positives = len(relevant_results)  # Relevant results
        false_positives = len(irrelevant_results)  # Irrelevant results
        false_negatives = 0  # Not applicable for single-source analysis
        
        # Calculate relevance score
        total_results = len(standardized_results)
        if total_results == 0:
            similarity_score = 0.0
        else:
            similarity_score = true_positives / total_results
        
        # Create mock matches for display purposes
        relevant_matches = [{"new": result, "old": {}, "similarity": 1.0} for result in relevant_results]
        
        return ComparisonResult(
            query=query,
            old_results_count=0,  # Not used
            new_results_count=total_results,
            common_matches=relevant_matches,  # Relevant results
            only_in_old=[],  # Not applicable
            only_in_new=irrelevant_results,  # These are false positives
            similarity_score=similarity_score,
            true_positives=true_positives,
            false_positives=false_positives,
            false_negatives=false_negatives
        )
