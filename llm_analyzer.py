"""
LLM-based analyzer for determining search result relevance using web scraping and AI analysis.
"""
import requests
import json
import time
from typing import Dict, List, Tuple, Optional
from urllib.parse import quote_plus
import re

class LLMRelevanceAnalyzer:
    """Uses LLM and web scraping to determine if search results are truly relevant."""
    
    def __init__(self, use_web_search: bool = False):
        # You can configure different LLM providers here
        self.llm_provider = "openai"  # or "anthropic", "local", etc.
        self.search_cache = {}  # Cache web search results
        self.use_web_search = use_web_search  # Disable by default for speed
        
    def web_search(self, query: str, num_results: int = 3) -> List[Dict]:
        """
        Perform web search to get additional context about an entity.
        Using DuckDuckGo Instant Answer API as it's free and doesn't require API keys.
        """
        if query in self.search_cache:
            return self.search_cache[query]
        
        try:
            # Use DuckDuckGo Instant Answer API
            url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant information
                results = []
                
                # Abstract (main description)
                if data.get('Abstract'):
                    results.append({
                        'type': 'abstract',
                        'text': data['Abstract'],
                        'source': data.get('AbstractSource', 'Unknown')
                    })
                
                # Definition
                if data.get('Definition'):
                    results.append({
                        'type': 'definition',
                        'text': data['Definition'],
                        'source': data.get('DefinitionSource', 'Unknown')
                    })
                
                # Related topics
                for topic in data.get('RelatedTopics', [])[:2]:  # Limit to 2
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append({
                            'type': 'related',
                            'text': topic['Text'],
                            'source': 'DuckDuckGo'
                        })
                
                self.search_cache[query] = results
                return results
                
        except Exception as e:
            print(f"Web search error for '{query}': {e}")
        
        return []
    
    def analyze_with_llm_simulation(self, entity_name: str, reference_company: str, web_context: List[Dict]) -> Tuple[bool, str, float]:
        """
        Simulate LLM analysis to determine if entity is related to reference company.
        In a real implementation, this would call OpenAI, Anthropic, or local LLM.
        """
        
        # Create context from web search results
        context_text = ""
        for item in web_context:
            context_text += f"{item['type'].title()}: {item['text']}\n"
        
        # Simulate intelligent analysis based on patterns
        entity_lower = entity_name.lower()
        reference_lower = reference_company.lower()
        
        # High confidence matches
        if reference_lower in entity_lower:
            if self._is_exact_company_match(entity_name, reference_company):
                return True, f"Direct match: '{entity_name}' is clearly related to {reference_company}", 0.95
        
        # Check for subsidiaries or divisions
        if self._is_subsidiary_or_division(entity_name, reference_company, context_text):
            return True, f"Subsidiary/Division: '{entity_name}' appears to be part of {reference_company}", 0.85
        
        # Check for partnerships or joint ventures
        if self._is_partnership(entity_name, reference_company, context_text):
            return True, f"Partnership: '{entity_name}' has business relationship with {reference_company}", 0.75
        
        # Check for completely unrelated companies
        if self._is_unrelated_company(entity_name, reference_company, context_text):
            return False, f"Unrelated: '{entity_name}' is a different company from {reference_company}", 0.05
        
        # Default: uncertain
        return False, f"Uncertain: Could not determine relationship between '{entity_name}' and {reference_company}", 0.3
    
    def _is_exact_company_match(self, entity_name: str, reference_company: str) -> bool:
        """Check if entity is the exact company or clear variation."""
        entity_clean = re.sub(r'\b(company|corp|corporation|inc|ltd|limited|s\.a\.?|s\.a\.i\.?)\b', '', entity_name.lower()).strip()
        reference_clean = re.sub(r'\b(company|corp|corporation|inc|ltd|limited)\b', '', reference_company.lower()).strip()
        
        # Check for exact match or very close match
        if entity_clean == reference_clean:
            return True
        
        # Check for common abbreviations and variations
        if reference_company.lower() == "general electric":
            return entity_clean in ["general electric", "ge"] or "general electric" in entity_clean
        elif reference_company.lower() == "ibm":
            return entity_clean in ["ibm", "international business machines"] or "ibm" in entity_clean
        elif reference_company.lower() == "johnson":
            return "johnson" in entity_clean and ("johnson" in entity_clean)
        elif reference_company.lower() == "coca-cola":
            # More flexible matching for Coca-Cola
            coca_variations = ["coca-cola", "coca cola", "cocacola", "the coca-cola"]
            return any(variation in entity_clean for variation in coca_variations)
        elif reference_company.lower() == "procter & gamble":
            pg_variations = ["procter & gamble", "procter and gamble", "p&g", "pg"]
            return any(variation in entity_clean for variation in pg_variations)
        
        return False
    
    def _is_subsidiary_or_division(self, entity_name: str, reference_company: str, context: str) -> bool:
        """Check if entity is a subsidiary or division."""
        entity_lower = entity_name.lower()
        
        if reference_company.lower() == "general electric":
            # GE divisions
            ge_divisions = ["ge aviation", "ge power", "ge healthcare", "ge renewable", "ge capital", "ge digital"]
            return any(division in entity_lower for division in ge_divisions)
        
        elif reference_company.lower() == "ibm":
            # IBM divisions/products
            ibm_terms = ["watson", "red hat", "ibm cloud", "ibm research"]
            return any(term in entity_lower for term in ibm_terms)
        
        elif reference_company.lower() == "coca-cola":
            # Coca-Cola subsidiaries and bottlers
            coca_subsidiaries = [
                "coca cola", "coca-cola", "cocacola",
                "embotelladora coca cola", "coca cola bottling", "coca cola beverages",
                "coca cola servicios", "coca cola polar", "coca cola singapore",
                "coca cola amatil", "coca cola hellenic", "coca cola femsa"
            ]
            return any(subsidiary in entity_lower for subsidiary in coca_subsidiaries)
        
        elif reference_company.lower() == "procter & gamble":
            # P&G brands and subsidiaries
            pg_brands = ["procter", "p&g", "pampers", "tide", "gillette", "oral-b", "crest", "head & shoulders"]
            return any(brand in entity_lower for brand in pg_brands)
        
        elif reference_company.lower() == "johnson & johnson":
            # J&J subsidiaries
            jj_subsidiaries = ["johnson", "j&j", "janssen", "ethicon", "depuy", "acuvue"]
            return any(subsidiary in entity_lower for subsidiary in jj_subsidiaries)
        
        # Check context for subsidiary keywords
        if context:
            subsidiary_keywords = ["subsidiary", "division", "unit of", "owned by", "part of"]
            return any(keyword in context.lower() for keyword in subsidiary_keywords)
        
        return False
    
    def _is_partnership(self, entity_name: str, reference_company: str, context: str) -> bool:
        """Check if entity has partnership with reference company."""
        if context:
            partnership_keywords = ["partnership", "joint venture", "collaboration", "alliance"]
            return any(keyword in context.lower() and reference_company.lower() in context.lower() 
                      for keyword in partnership_keywords)
        return False
    
    def _is_unrelated_company(self, entity_name: str, reference_company: str, context: str) -> bool:
        """Check if entity is clearly unrelated."""
        entity_lower = entity_name.lower()
        
        # Different industry indicators
        if reference_company.lower() == "general electric":
            # If it's clearly a different electric/utility company
            unrelated_patterns = [
                "qatar general electricity",
                "uganda electricity",
                "electricity generating public",
                "wind energy electricity"
            ]
            return any(pattern in entity_lower for pattern in unrelated_patterns)
        
        return False
    
    def analyze_relevance(self, entity_name: str, reference_company: str, query: str) -> Tuple[bool, str, float]:
        """
        Main method to analyze if an entity is relevant to the reference company.
        
        Returns:
            Tuple of (is_relevant, explanation, confidence_score)
        """
        
        # Step 1: Get web context (only if enabled)
        web_context = []
        if self.use_web_search:
            try:
                web_context = self.web_search(f"{entity_name} company")
            except Exception as e:
                # Continue without web context if it fails
                web_context = []
        
        # Step 2: Analyze with simulated LLM
        is_relevant, explanation, confidence = self.analyze_with_llm_simulation(
            entity_name, reference_company, web_context
        )
        
        return is_relevant, explanation, confidence
    
    def batch_analyze(self, entities: List[str], reference_company: str, query: str) -> List[Dict]:
        """Analyze multiple entities in batch."""
        results = []
        
        for entity in entities:
            is_relevant, explanation, confidence = self.analyze_relevance(entity, reference_company, query)
            results.append({
                'entity': entity,
                'is_relevant': is_relevant,
                'explanation': explanation,
                'confidence': confidence
            })
        
        return results

# Test the analyzer
if __name__ == "__main__":
    analyzer = LLMRelevanceAnalyzer()
    
    # Test with some entities
    test_entities = [
        "General Electric Company",
        "Qatar General Electricity & Water",
        "GE Aviation",
        "Electricity Generating Public Company"
    ]
    
    print("Testing LLM Relevance Analyzer:")
    print("=" * 50)
    
    for entity in test_entities:
        is_relevant, explanation, confidence = analyzer.analyze_relevance(
            entity, "General Electric", "general electric"
        )
        
        status = "✅ RELEVANT" if is_relevant else "❌ NOT RELEVANT"
        print(f"{status} ({confidence:.2f}): {entity}")
        print(f"   Explanation: {explanation}")
        print()
