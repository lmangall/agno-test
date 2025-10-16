


## 🚀 Current Full Flow

1. **Upload pitch deck as PDF** 
2. **Transform to images** → passed to OpenAI Vision API for text extraction
3. **AI Analysis** → extract structured insights (founders, problem, solution, etc.)
4. **Founder Lookup** (optional):
   - Extract founder names from analysis
   - Look up in Google Custom Search Engine (LinkedIn only)
   - Retrieve LinkedIn username (e.g., `l-mangallon`)
   - Fetch full profile from LinkedIn API via Unipile



# PDF Pitch Deck Analyzer

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

## 🔧 Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```bash
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CX=your_custom_search_engine_id
UNIPILE_API_KEY=your_unipile_key
UNIPILE_ACCOUNT_ID=your_linkedin_account_id
```

## 🧪 Testing

### Test Google LinkedIn Search
```bash
python test_google_linkedin_tool.py "leonard mangallon"
```

### Test Combined Search (Google → LinkedIn API)
```bash
python test_combined_linkedin_search.py "leonard mangallon"
```

### Test Full Pitch Deck Analysis
```bash
# Without LinkedIn lookup
python test_full_analysis.py ./pitch/airbnb-pitch-deck.pdf false

# With LinkedIn lookup
python test_full_analysis.py ./pitch/airbnb-pitch-deck.pdf true
```

## 🌐 API Usage

### Basic Analysis (without LinkedIn lookup)
```bash
curl -X POST "https://XXXXXXX.onrender.com/analyze" \
  -F "file=@pitch/airbnb-pitch-deck.pdf"
```

### Analysis with LinkedIn Founder Lookup
```bash
curl -X POST "https://XXXXXXX.onrender.com/analyze?lookup_founders=true" \
  -F "file=@pitch/airbnb-pitch-deck.pdf"
```

### Example Response

The call took 1mn30 for Airbnb pitch-deck (14 pages, <1mb)

```bash
curl -X POST "https://XXXXXXX.onrender.com/analyze" \
  -F "file=@pitch/airbnb-pitch-deck.pdf" | jq -r '.analysis'
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  906k    0  1686  100  904k     19  10955  0:01:24  0:01:24 --:--:--   468
```json
{
  "startup_name": "AirBed&Breakfast™",
  "value_proposition": "Book rooms with locals, rather than hotels.",
  "number_of_founders": 4,
  "founders": [
    "Joe Gebbia",
    "Brian Chesky",
    "Nathan Blecharcyk",
    "Michael Seibel"
  ],
  "problem": "Price is a concern for customers booking travel online. Hotels leave you disconnected from the city and its culture. No easy way exists to book a room with a local or become a host.",
  "solution": "A web platform where users can rent out their space to host travelers. It allows customers to save money when traveling, make money when hosting, and share culture.",
  "target_market": "Travelers seeking affordable accommodation and locals wishing to host.",
  "traction": "Projected 80,000 transactions in the first 12 months yielding $2M in revenue.",
  "funding": {
    "amount": 500000,
    "round": "Angel Round"
  },
  "notable_points": [
    "1st to market for transaction-based temporary housing site",
    "Host incentive to make money over competitors like Couchsurfing",
    "Ease of use with streamlined booking process",
    "Positive press and user testimonials highlighting success"
  ],
  "summary": "AirBed&Breakfast offers a unique platform enabling travelers to connect with local hosts, providing affordable and culturally immersive options. With a strong founding team and a business model based on service fees, the startup aims to tap into a significant portion of the travel market.",
  "investor_remark": "A promising concept that addresses real pain points in travel accommodation."
}
```
➜  agno-test git:(main) 



We use Unipile to access Linkedin API
(provide api access to various socials, used by lemlist...)


With Unipile you can retrieve a profile  using the last part of url:
l-mangallon in 
https://www.linkedin.com/in/l-mangallon/
(It is not always formatted the same way)

The API can not lookup people, if the linkedin account is "standard"


So the solution without using a business linkedin account is to use Custom Search JSON API
The engine has been setup to look only on linkedin domain
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

## 🚀 Running the API

```bash
# Development
python api.py

# Production (Render)
uvicorn api:app --host 0.0.0.0 --port $PORT
```

The API will be available at `http://localhost:8000`

## 📚 API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /analyze?lookup_founders=true` - Analyze pitch deck with optional LinkedIn lookup
