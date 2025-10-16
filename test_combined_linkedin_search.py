#!/usr/bin/env python3
"""Test script showing how to combine Google search with LinkedIn profile lookup."""

import os
import sys
from dotenv import load_dotenv
from google_linkedin_search_tool import get_linkedin_usernames_list
from linkedin_search_tool import _search_linkedin_people_impl

# Load environment variables
load_dotenv()


def test_combined_search(query: str, account_id: str = None):
    """Test the combined Google + LinkedIn search workflow.
    
    Args:
        query: Person's name to search for
        account_id: Unipile account ID for LinkedIn API (optional, reads from env)
    """
    # Get account_id from env if not provided
    if not account_id:
        account_id = os.getenv('UNIPILE_ACCOUNT_ID')
        if not account_id:
            print("❌ Error: UNIPILE_ACCOUNT_ID not found in environment variables")
            print("   Please add it to your .env file or pass as argument")
            return
    print(f"\n{'='*70}")
    print(f"Combined LinkedIn Search Test")
    print(f"{'='*70}\n")
    
    print(f"Step 1: Searching Google for LinkedIn profiles matching '{query}'...\n")
    
    # Get LinkedIn usernames from Google search
    usernames = get_linkedin_usernames_list(query, num_results=3)
    
    if not usernames:
        print("❌ No LinkedIn usernames found")
        return
    
    print(f"✅ Found {len(usernames)} LinkedIn username(s):")
    for idx, username in enumerate(usernames, 1):
        print(f"  {idx}. {username}")
    
    # Use the first username to get detailed profile info
    first_username = usernames[0]
    
    print(f"\n{'='*70}")
    print(f"Step 2: Getting detailed profile for '{first_username}'...\n")
    
    profile_result = _search_linkedin_people_impl(
        name_surname=first_username,
        account_id=account_id
    )
    
    print(profile_result)
    
    # Show other usernames that could be checked
    if len(usernames) > 1:
        print(f"\n{'='*70}")
        print(f"Other profiles you could check:")
        for username in usernames[1:]:
            print(f"  • {username}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_combined_linkedin_search.py <name> [account_id]")
        print("\nExample:")
        print('  python test_combined_linkedin_search.py "leonard mangallon"')
        print('  python test_combined_linkedin_search.py "leonard mangallon" custom_account_id')
        sys.exit(1)
    
    query = sys.argv[1]
    
    # Account ID is optional - if not provided, will use env var
    account_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    test_combined_search(query, account_id)
