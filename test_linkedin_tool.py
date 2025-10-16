#!/usr/bin/env python3
"""
Simple test script for the LinkedIn search tool.
Usage: python test_linkedin_tool.py <name-surname> <account_id>

Example: python test_linkedin_tool.py john-doe qAXOJ2qHQyKTjjsN-rX_Ug
"""

import sys
from linkedin_search_tool import _search_linkedin_people_impl, LinkedInSearchClient

def main():
    # Check command line arguments
    if len(sys.argv) != 3:
        print("❌ Usage: python test_linkedin_tool.py <name-surname> <account_id>")
        print("\nExample:")
        print("  python test_linkedin_tool.py john-doe qAXOJ2qHQyKTjjsN-rX_Ug")
        print("\nNote: Make sure UNIPILE_API_KEY is set in your environment!")
        sys.exit(1)
    
    name_surname = sys.argv[1]
    account_id = sys.argv[2]
    
    print(f"🔍 Testing LinkedIn Search Tool")
    print(f"Name-surname: {name_surname}")
    print(f"Account ID: {account_id}")
    print("-" * 50)
    
    # Test 1: Using the implementation function
    print("📍 Test 1: Using implementation function")
    try:
        result = _search_linkedin_people_impl(
            name_surname=name_surname,
            account_id=account_id
        )
        print(result)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "-" * 50)
    
    # Test 2: Using the client directly for raw response
    print("📍 Test 2: Using client directly (raw response)")
    try:
        client = LinkedInSearchClient()
        raw_result = client.search_people(
            name_surname=name_surname,
            account_id=account_id
        )
        print("Raw API Response:")
        import json
        print(json.dumps(raw_result, indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()