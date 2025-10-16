import os
import re
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from agno.tools import tool

# Load environment variables
load_dotenv()


class GoogleLinkedInSearchClient:
    """Client for searching LinkedIn profiles using Google Custom Search API."""
    
    def __init__(self, api_key: Optional[str] = None, cx: Optional[str] = None):
        """Initialize the Google LinkedIn search client.
        
        Args:
            api_key: Google API key. If not provided, will look for GOOGLE_API_KEY env var.
            cx: Google Custom Search Engine ID. If not provided, will look for GOOGLE_CX env var.
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.cx = cx or os.getenv('GOOGLE_CX')
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        if not self.cx:
            raise ValueError("GOOGLE_CX environment variable is required")
        
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """Search for LinkedIn profiles using Google Custom Search.
        
        Args:
            query: Search query (e.g., person's name)
            num_results: Number of results to return (1-10, default 10)
            
        Returns:
            Dictionary containing search results
        """
        params = {
            "q": query,
            "key": self.api_key,
            "cx": self.cx,
            "num": min(num_results, 10)  # Google CSE max is 10 per request
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Google search failed: {str(e)}"
            status_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f" | Details: {error_detail}"
                except:
                    error_msg += f" | Response: {e.response.text}"
            
            return {
                "error": error_msg,
                "status_code": status_code
            }


def extract_linkedin_username(url: str) -> Optional[str]:
    """Extract LinkedIn username from a LinkedIn profile URL.
    
    Args:
        url: LinkedIn profile URL (e.g., https://fr.linkedin.com/in/l-mangallon)
        
    Returns:
        Username string (e.g., 'l-mangallon') or None if not found
    """
    # Pattern to match LinkedIn profile URLs
    pattern = r'linkedin\.com/in/([^/?]+)'
    match = re.search(pattern, url)
    return match.group(1) if match else None


def _google_linkedin_search_impl(query: str, num_results: int = 10) -> str:
    """Implementation of Google LinkedIn search - can be called directly."""
    try:
        client = GoogleLinkedInSearchClient()
        results = client.search(query=query, num_results=num_results)
        
        if "error" in results:
            return f"❌ Error: {results['error']}"
        
        # Check if we have items in the response
        items = results.get('items', [])
        if not items:
            return f"🔍 No LinkedIn profiles found for '{query}'"
        
        # Format the results
        formatted_result = f"🔍 LinkedIn Search Results for '{query}':\n\n"
        formatted_result += f"Found {len(items)} result(s)\n\n"
        
        for idx, item in enumerate(items, 1):
            title = item.get('title', 'N/A')
            link = item.get('link', 'N/A')
            snippet = item.get('snippet', 'N/A')
            
            # Extract username from URL
            username = extract_linkedin_username(link)
            
            formatted_result += f"{idx}. **{title}**\n"
            formatted_result += f"   URL: {link}\n"
            if username:
                formatted_result += f"   Username: {username}\n"
            formatted_result += f"   {snippet}\n\n"
        
        return formatted_result
        
    except Exception as e:
        return f"❌ Error searching LinkedIn via Google: {str(e)}"


def _get_linkedin_usernames_impl(query: str, num_results: int = 10) -> str:
    """Get LinkedIn usernames from search results."""
    try:
        client = GoogleLinkedInSearchClient()
        results = client.search(query=query, num_results=num_results)
        
        if "error" in results:
            return f"❌ Error: {results['error']}"
        
        items = results.get('items', [])
        if not items:
            return f"🔍 No LinkedIn profiles found for '{query}'"
        
        # Extract usernames
        usernames = []
        for item in items:
            link = item.get('link', '')
            username = extract_linkedin_username(link)
            if username:
                usernames.append(username)
        
        if not usernames:
            return f"🔍 No LinkedIn usernames found for '{query}'"
        
        # Return as comma-separated list
        return ", ".join(usernames)
        
    except Exception as e:
        return f"❌ Error extracting LinkedIn usernames: {str(e)}"


@tool
def google_linkedin_search(query: str, num_results: int = 10) -> str:
    """Search for LinkedIn profiles using Google Custom Search API.
    
    This tool uses Google's Custom Search Engine configured specifically for LinkedIn
    to find profiles and information about people.
    
    Args:
        query: Search query - typically a person's name (e.g., "leonard mangallon")
        num_results: Number of results to return (1-10, default 10)
        
    Returns:
        Formatted string with search results including titles, URLs, and snippets
    """
    return _google_linkedin_search_impl(query, num_results)


@tool
def get_linkedin_usernames(query: str, num_results: int = 10) -> str:
    """Get LinkedIn usernames from Google search results.
    
    This tool searches for LinkedIn profiles and extracts just the usernames
    (e.g., 'l-mangallon') which can be used with other LinkedIn tools.
    
    Args:
        query: Search query - typically a person's name (e.g., "leonard mangallon")
        num_results: Number of results to return (1-10, default 10)
        
    Returns:
        Comma-separated list of LinkedIn usernames
    """
    return _get_linkedin_usernames_impl(query, num_results)


# Direct usage functions (not as agno tools)
def google_linkedin_search_raw(query: str, num_results: int = 10) -> Dict[str, Any]:
    """Direct Google LinkedIn search function that returns raw API response.
    
    Args:
        query: Search query
        num_results: Number of results (1-10)
        
    Returns:
        Raw API response dictionary
    """
    client = GoogleLinkedInSearchClient()
    return client.search(query=query, num_results=num_results)


def get_linkedin_usernames_list(query: str, num_results: int = 10) -> List[str]:
    """Get LinkedIn usernames as a Python list.
    
    Args:
        query: Search query
        num_results: Number of results (1-10)
        
    Returns:
        List of LinkedIn usernames
    """
    client = GoogleLinkedInSearchClient()
    results = client.search(query=query, num_results=num_results)
    
    if "error" in results:
        return []
    
    items = results.get('items', [])
    usernames = []
    
    for item in items:
        link = item.get('link', '')
        username = extract_linkedin_username(link)
        if username:
            usernames.append(username)
    
    return usernames


if __name__ == "__main__":
    print("Google LinkedIn Search Tool")
    print("Usage example:")
    print('  from google_linkedin_search_tool import google_linkedin_search')
    print('  result = google_linkedin_search("leonard mangallon")')
    print('  print(result)')
