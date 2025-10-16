#!/usr/bin/env python3
"""Test script for Google LinkedIn Search Tool."""

import sys
from google_linkedin_search_tool import _google_linkedin_search_impl, google_linkedin_search_raw


def test_search(query: str, num_results: int = 5):
    """Test the Google LinkedIn search tool."""
    print(f"\n{'='*60}")
    print(f"Testing Google LinkedIn Search")
    print(f"{'='*60}\n")
    
    print(f"Query: {query}")
    print(f"Number of results: {num_results}\n")
    
    # Test the formatted tool output
    print("--- Formatted Output (Agno Tool) ---\n")
    result = _google_linkedin_search_impl(query, num_results)
    print(result)
    
    # Test the raw API response
    print("\n--- Raw API Response ---\n")
    raw_result = google_linkedin_search_raw(query, num_results)
    
    if "error" in raw_result:
        print(f"Error: {raw_result['error']}")
    else:
        print(f"Total Results: {raw_result.get('searchInformation', {}).get('totalResults', 'N/A')}")
        print(f"Search Time: {raw_result.get('searchInformation', {}).get('searchTime', 'N/A')} seconds")
        print(f"Items returned: {len(raw_result.get('items', []))}")


if __name__ == "__main__":
    # Default query
    query = "leonard mangallon"
    num_results = 5
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    
    test_search(query, num_results)
