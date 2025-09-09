#!/usr/bin/env python3
"""
Quick test to verify Coca-Cola matching logic
"""
from llm_analyzer import LLMRelevanceAnalyzer

def test_coca_cola_matching():
    analyzer = LLMRelevanceAnalyzer(use_web_search=False)
    
    # Test entities that should be TRUE MATCHES for Coca-Cola
    test_entities = [
        "The Coca-Cola Company",
        "COCA-COLA SERVICIOS DE PERU S.A",
        "Embotelladora Coca Cola Polar S.A.I",
        "Coca Cola Singapore Beverages",
        "COCAMAR SC",  # This might be false positive
        "Sahra Colaad Cabdi"  # This should be false positive
    ]
    
    print("Testing Coca-Cola Entity Classification:")
    print("=" * 60)
    
    for entity in test_entities:
        is_relevant, explanation, confidence = analyzer.analyze_relevance(
            entity, "Coca-Cola", "coca-cola"
        )
        
        status = "✅ TRUE MATCH" if is_relevant else "❌ FALSE POSITIVE"
        print(f"{status} ({confidence:.2f}): {entity}")
        print(f"   Explanation: {explanation}")
        print()

if __name__ == "__main__":
    test_coca_cola_matching()
