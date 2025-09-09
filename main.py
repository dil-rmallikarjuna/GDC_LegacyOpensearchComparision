"""
Main automation script for comparing search results.
"""
import os
import sys
from typing import List
from tqdm import tqdm
from colorama import init, Fore, Style

from api_client import OpenSearchAPIClient
from comparison_engine import ComparisonEngine
from report_generator import ReportGenerator
from reference_loader import SearchReferenceLoader

# Initialize colorama for colored output
init()

class OpenSearchRelevanceAnalyzer:
    """Main automation class for OpenSearch relevance analysis."""
    
    def __init__(self):
        self.api_client = OpenSearchAPIClient()
        self.comparison_engine = ComparisonEngine()
        self.report_generator = ReportGenerator()
        self.reference_loader = SearchReferenceLoader()
    
    def analyze_relevance(self, queries: List[str] = None):
        """
        Run OpenSearch relevance analysis.
        
        Args:
            queries: List of queries to test. If None, will use default test queries.
        """
        print(f"{Fore.CYAN}Starting OpenSearch Relevance Analysis{Style.RESET_ALL}")
        print("=" * 60)
        
        try:
            # Get queries to test
            if queries is None:
                print(f"{Fore.YELLOW}Loading queries from reference file...{Style.RESET_ALL}")
                # Use all queries from the reference file
                reference_queries = self.reference_loader.get_all_queries()
                if reference_queries:
                    queries = [q.lower() for q in reference_queries]  # Convert to lowercase for API
                    print(f"Using {len(queries)} queries from reference file: {', '.join(queries)}")
                else:
                    # Fallback to default queries
                    queries = ["microsoft", "apple", "google"]
                    print(f"No reference file found, using {len(queries)} default queries")
            
            if not queries:
                print(f"{Fore.RED}❌ No queries found to test{Style.RESET_ALL}")
                return
            
            # Run relevance analysis
            print(f"{Fore.YELLOW}Running relevance analysis for {len(queries)} queries...{Style.RESET_ALL}")
            analysis_results = []
            
            for query in tqdm(queries, desc="Processing queries"):
                try:
                    # Get results from OpenSearch API only
                    api_response = self.api_client.search(query)
                    new_results = api_response.get('results', []) if 'error' not in api_response else []
                    
                    # Analyze relevance
                    analysis = self.comparison_engine.analyze_results(query, [], new_results)
                    analysis_results.append(analysis)
                    
                    # Print quick summary
                    status = "✅" if analysis.similarity_score >= 0.8 else "⚠️"
                    relevant_count = analysis.true_positives
                    total_count = analysis.new_results_count
                    print(f"  {status} {query}: {relevant_count}/{total_count} relevant results ({analysis.similarity_score:.1%})")
                    
                except Exception as e:
                    print(f"{Fore.RED}❌ Error processing query '{query}': {e}{Style.RESET_ALL}")
                    continue
            
            # Generate reports
            print(f"{Fore.YELLOW}Generating reports...{Style.RESET_ALL}")
            
            excel_path = self.report_generator.generate_excel_report(analysis_results)
            html_path = self.report_generator.generate_html_report(analysis_results)
            
            # Print summary
            self.print_summary(analysis_results, excel_path, html_path)
            
        except Exception as e:
            print(f"{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
            raise
    
    def print_summary(self, results, excel_path, html_path):
        """Print a summary of the relevance analysis results."""
        print("\n" + "=" * 60)
        print(f"{Fore.GREEN}OpenSearch Relevance Analysis Complete!{Style.RESET_ALL}")
        print("=" * 60)
        
        total_queries = len(results)
        good_relevance = sum(1 for r in results if r.similarity_score >= 0.8)
        avg_relevance = sum(r.similarity_score for r in results) / total_queries if total_queries > 0 else 0
        total_relevant = sum(r.true_positives for r in results)
        total_irrelevant = sum(r.false_positives for r in results)
        
        print(f"Total Queries Processed: {total_queries}")
        print(f"Good Relevance (≥80%): {good_relevance}")
        print(f"Needs Review: {total_queries - good_relevance}")
        print(f"Average Relevance: {avg_relevance:.1%}")
        print(f"Total Relevant Results: {total_relevant}")
        print(f"Total Irrelevant Results: {total_irrelevant}")
        
        print(f"\nReports Generated:")
        print(f"  Excel: {excel_path}")
        print(f"  HTML: {html_path}")
        
        if good_relevance / total_queries >= 0.8:
            print(f"\n{Fore.GREEN}Overall Assessment: EXCELLENT - Most queries show high relevance{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}Overall Assessment: NEEDS REVIEW - Search relevance could be improved{Style.RESET_ALL}")

def main():
    """Main function."""
    analyzer = OpenSearchRelevanceAnalyzer()
    
    # Run relevance analysis with queries from reference file
    # This will automatically use all queries defined in search_reference.txt
    analyzer.analyze_relevance()

if __name__ == "__main__":
    main()
