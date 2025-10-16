


## 🚀 Current Full Flow
Upload pitch deck as PDF -> Transform to images → passed to OpenAI Vision API for text extraction 
-> AI Analysis → extract structured insights (founders, problem, solution, etc.)
-> Extract founder names from analysis -> Look up in Google Custom Search Engine (LinkedIn only)
-> Retrieve LinkedIn username (e.g., `l-mangallon`) -> Fetch full profile from LinkedIn API via Unipile



#  1 -PDF Pitch Deck Analyzer

**Purpose:** Extract text from PDF pitch decks with tricky fonts and encodings, then analyze them with AI.

**Problem encountered with traditional PDF libraries:**

-   Fail on special fonts and encodings -> unreliable    

**Solution 1:**
-   Use an OCR Library
Problem: this is a fast test I want it deployed on Render without dockerisation, and PyTesselate requires OS-level install 

**Problem with fallback approach:**
You could use a regular Python lib for reading pdf and only IF text is not clear then use encoding
This has to be done carefully cause with our test files some files had both clear text and encoded text, resulting in fallback not happening


**Solution Final:**

-   Convert PDF pages to images.
-   Use **OpenAI Vision** for text extraction.
-   Analyze with AI agent for structured insights.

# 2- Lookup founders on Linkedin

We use Unipile to access Linkedin API
(provide api access to various socials, used by lemlist...)


With Unipile you can retrieve a profile  using the last part of url:
l-mangallon in https://www.linkedin.com/in/l-mangallon/
(however It is not always formatted the same way)

The API can not lookup people, if the linkedin account is "standard" (so I had to find another way)


So the solution without using a business linkedin account is to use Custom Search JSON API from Google:
https://developers.google.com/custom-search/v1/overview
The engine has been setup to look only on linkedin domain (very simple setup and API access)
so it can takes a regular request and return the url part that the unipile API needs to retrieve a profile


## 🛠️ Available Tools

### 1. Google LinkedIn Search Tool (`google_linkedin_search_tool.py`)
n profiles using Google Custom Search API.

**Agno Tools:**
- `google_linkedin_search(query, num_results)` - Returns formatted search results
- `get_linkedin_usernames(query, num_results)` - Returns comma-separated LinkedIn usernames

**Helper Functions:**
- `get_linkedin_usernames_liry, num_results)` - Returns list of usernames
- `google_linkedin_search_raw(query, num_results)` - Returns raw API response

### 2. LinkedIn Search Tool (`linkedin_search_tool.py`)

Fetches detailed LinkedIn profiles using Unipile API.

**Agno Tool:**
- `search_linkedin_people(name_surname, account_id)` - Returns formatted profile info

**Helper Function:**
- `linkedin_search(name_surname, account_id)` - Returns raw profile data

### 3. Pitch Deck Analyzer (`analyze_pitchdeck.py`)

Main analysis function with optional LinkedIn lookup.

```python
analyze_pitchdeck(
    file_path: str,
    verbose: bool = True,
    force_ocr: bool = False,
    lookup_founders: bool = False  # Enable LinkedIn lookup
)
```

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for Vision OCR | Yes |
| `GOOGLE_API_KEY` | Google Custom Search API key | For LinkedIn lookup |
| `GOOGLE_CX` | Google Custom Search Engine ID | For LinkedIn lookup |
| `UNIPILE_API_KEY` | Unipile API key | For LinkedIn lookup |
| `UNIPILE_ACCOUNT_ID` | Your LinkedIn account ID in Unipile | For LinkedIn lookup |


## 📚 API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /analyze?lookup_founders=true` - Analyze pitch deck with optional LinkedIn lookup



Deployed on Render:


<img width="1309" height="697" alt="Screenshot 2025-10-16 at 16 33 56" src="https://github.com/user-attachments/assets/7e6b4ffe-8512-4263-b6ee-a22f70d11669" />

