
# PDF Pitch Deck Analyzer

**Purpose:** Extract text from PDF pitch decks with tricky fonts and encodings, then analyze them with AI.

**Problem encountered with traditional PDF libraries:**

-   Fail on special fonts and encodings -> unreliable    

**Solution 1:**
-   Use an OCR Library
Problem: this is a fast test I want it deployed on Render without dockerisation, and PyTesselate requires OS-level install  

**Solution Final:**

-   Convert PDF pages to images.
-   Use **OpenAI Vision** for text extraction.
-   Analyze with AI agent for structured insights.

## API Usage

### Start the server
```bash
python api.py
```

### Analyze a pitch deck
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@pitch/airbnb-pitch-deck.pdf" \
  -F "force_ocr=false"
```

### With forced OCR
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@pitch/airbnb-pitch-deck.pdf" \
  -F "force_ocr=true"
```

### Health check
```bash
curl http://localhost:8000/health
```
        
    
