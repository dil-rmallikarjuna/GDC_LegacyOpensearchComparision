#!/usr/bin/env python3
"""
Extract search terms from Excel file for K6 performance testing
"""

import sys
import os
import json

def extract_search_terms_from_excel():
    """Extract search terms from the Excel file"""
    try:
        # Try to import required modules
        try:
            import pandas as pd
            use_pandas = True
        except ImportError:
            use_pandas = False
            
        if use_pandas:
            # Use pandas to read Excel
            excel_file = "/Users/rmallikarjuna/Documents/GDC automation excel driven/Test terms copy.xlsx"
            df = pd.read_excel(excel_file)
            
            # Get search terms from the first column or 'Search Term' column
            if 'Search Term' in df.columns:
                terms = df['Search Term'].dropna().unique().tolist()
            else:
                # Use first column
                terms = df.iloc[:, 0].dropna().unique().tolist()
                
            print(f"Extracted {len(terms)} search terms using pandas")
            return terms
        else:
            # Fallback: return some sample terms
            print("Pandas not available, using sample terms")
            return [
                "Narendra Modi",
                "Industrial & Commercial Bank of China",
                "Credit Suisse Group AG",
                "David Thomas Smith",
                "Apple Inc",
                "Microsoft Corporation",
                "Google LLC",
                "Amazon.com Inc",
                "Tesla Inc",
                "Meta Platforms Inc"
            ]
            
    except Exception as e:
        print(f"Error extracting terms: {e}")
        # Return sample terms as fallback
        return [
            "Narendra Modi",
            "Industrial & Commercial Bank of China", 
            "Credit Suisse Group AG",
            "David Thomas Smith",
            "Apple Inc"
        ]

def save_search_terms_to_js(terms):
    """Save search terms to JavaScript file for K6"""
    js_content = f"""
// Search terms extracted from Excel file
// Generated automatically - do not edit manually

export const searchTerms = {json.dumps(terms, indent=2)};

export const getRandomSearchTerm = () => {{
    const randomIndex = Math.floor(Math.random() * searchTerms.length);
    return searchTerms[randomIndex];
}};

export const getSearchTermByIndex = (index) => {{
    return searchTerms[index % searchTerms.length];
}};

export const getTotalSearchTerms = () => {{
    return searchTerms.length;
}};
"""
    
    output_file = "/Users/rmallikarjuna/Documents/GDC automation excel driven/k6-tests/data/search-terms.js"
    with open(output_file, 'w') as f:
        f.write(js_content)
    
    print(f"Saved {len(terms)} search terms to {output_file}")
    return output_file

if __name__ == "__main__":
    print("Extracting search terms from Excel file...")
    terms = extract_search_terms_from_excel()
    
    if terms:
        print(f"Found {len(terms)} search terms:")
        for i, term in enumerate(terms[:10]):  # Show first 10
            print(f"  {i+1}. {term}")
        if len(terms) > 10:
            print(f"  ... and {len(terms)-10} more terms")
        
        # Save to JavaScript file
        output_file = save_search_terms_to_js(terms)
        print(f"✅ Search terms saved to: {output_file}")
    else:
        print("❌ No search terms found")
        sys.exit(1)
