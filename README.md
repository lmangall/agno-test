
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

## API Usage

The call took 1mn30 for Airbnb pitch-deck but was succesful

➜  agno-test git:(main) curl -X POST "https://XXXXXXX.onrender.com/analyze" \
  -F "file=@pitch/airbnb-pitch-deck.pdf" \
  -F "force_ocr=true" | jq -r '.analysis'
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

