import os
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from agno.tools import tool

# Load environment variables
load_dotenv()


class LinkedInSearchClient:
    """Client for searching LinkedIn profiles using Unipile API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LinkedIn search client.
        
        Args:
            api_key: Unipile API key. If not provided, will look for UNIPILE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('UNIPILE_API_KEY')
        if not self.api_key:
            raise ValueError("UNIPILE_API_KEY environment variable is required")
        
        self.base_url = "https://api22.unipile.com:15236"
        self.headers = {
            'X-API-KEY': self.api_key,
            'accept': 'application/json'
        }
    
    def search_people(
        self, 
        name_surname: str,
        account_id: str
    ) -> Dict[str, Any]:
        """Search for a person on LinkedIn using the Unipile API.
        
        Args:
            name_surname: The person's name and surname (e.g., "john-doe")
            account_id: Unipile account ID for the LinkedIn account
            
        Returns:
            Dictionary containing search results
        """
        # Build the endpoint URL with the name-surname and account_id as query param
        endpoint = f"{self.base_url}/api/v1/users/{name_surname}"
        
        # Build query parameters - only account_id
        params = {
            "account_id": account_id
        }
        
        try:
            response = requests.get(
                endpoint,
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"LinkedIn search failed: {str(e)}"
            status_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            
            # Add more specific error info if available
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.text
                    error_msg += f" | Response: {error_detail}"
                except:
                    pass
            
            return {
                "error": error_msg,
                "status_code": status_code
            }


def _search_linkedin_people_impl(
    name_surname: str,
    account_id: str
) -> str:
    """Implementation of LinkedIn search - can be called directly."""
    try:
        client = LinkedInSearchClient()
        results = client.search_people(
            name_surname=name_surname,
            account_id=account_id
        )
        
        if "error" in results:
            return f"❌ Error: {results['error']}"
        
        # Format the results for display
        if not results:
            return f"🔍 No LinkedIn profile found for '{name_surname}'"
        
        # Extract profile information from actual API response structure
        first_name = results.get('first_name', '')
        last_name = results.get('last_name', '')
        profile_name = f"{first_name} {last_name}".strip() or 'N/A'
        
        headline = results.get('headline', 'N/A')
        location_info = results.get('location', 'N/A')
        
        # Build LinkedIn profile URL from public_identifier
        public_id = results.get('public_identifier', '')
        profile_url = f"https://www.linkedin.com/in/{public_id}" if public_id else 'N/A'
        
        # Get connection and follower counts
        connections = results.get('connections_count', 'N/A')
        followers = results.get('follower_count', 'N/A')
        
        # Get contact info
        contact_info = results.get('contact_info', {})
        emails = contact_info.get('emails', [])
        email = emails[0] if emails else 'N/A'
        
        # Get websites
        websites = results.get('websites', [])
        
        formatted_result = f"🔍 LinkedIn Profile for '{name_surname}':\n\n"
        formatted_result += f"**{profile_name}**\n"
        formatted_result += f"• Headline: {headline}\n"
        formatted_result += f"• Location: {location_info}\n"
        formatted_result += f"• Profile: {profile_url}\n"
        formatted_result += f"• Connections: {connections} | Followers: {followers}\n"
        formatted_result += f"• Email: {email}\n"
        
        if websites:
            formatted_result += f"• Websites: {', '.join(websites[:3])}\n"
        
        return formatted_result
        
    except Exception as e:
        return f"❌ Error searching LinkedIn: {str(e)}"


@tool
def search_linkedin_people(
    name_surname: str,
    account_id: str
) -> str:
    """Search for a specific person on LinkedIn using their name-surname format.
    
    Args:
        name_surname: The person's name and surname in URL format (e.g., "john-doe")
        account_id: Unipile account ID for the LinkedIn account
        
    Returns:
        Formatted string with search results or error message
    """
    return _search_linkedin_people_impl(name_surname, account_id)


# Example function for direct usage (not as agno tool)
def linkedin_search(name_surname: str, account_id: str) -> Dict[str, Any]:
    """Direct LinkedIn search function that returns raw API response.
    
    Args:
        name_surname: Person's name in URL format (e.g., "john-doe")
        account_id: Unipile account ID
        
    Returns:
        Raw API response dictionary
    """
    client = LinkedInSearchClient()
    return client.search_people(name_surname=name_surname, account_id=account_id)


if __name__ == "__main__":
    print("Use test_linkedin_tool.py to test this module")
    print("Usage: python test_linkedin_tool.py <name-surname> <account_id>")
