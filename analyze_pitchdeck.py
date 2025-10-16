import json
from textwrap import dedent
from pathlib import Path

from agno.agent import Agent
from agno.models.openai import OpenAIChat
import fitz  # PyMuPDF
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ==========
# 1️⃣ PDF TEXT EXTRACTOR (PYMUPDF)
# ==========

def extract_pdf_text(file_path: str, verbose: bool = True) -> str:
    """Extract text from a PDF file page by page and return as JSON.

    Args:
        file_path (str): Path to the PDF file.
        verbose (bool): If True, prints extracted text for each page.

    Returns:
        str: JSON string with text extracted from each page.
    """
    pdf_path = Path(file_path)
    if not pdf_path.exists():
        return json.dumps({"error": f"File not found: {file_path}"})

    pages = []
    
    try:
        # Open PDF with PyMuPDF
        doc = fitz.open(str(pdf_path))
        
        print(f"📄 Found {len(doc)} pages in PDF\n")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # If text extraction fails, try OCR on the page image
            if not text.strip() or "(cid:" in text:
                print(f"⚠️  Page {page_num + 1} needs OCR, extracting from image...")
                # Get page as image and extract text
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                
                # Use pytesseract if available
                try:
                    from PIL import Image
                    import pytesseract
                    import io
                    
                    img = Image.open(io.BytesIO(img_bytes))
                    text = pytesseract.image_to_string(img)
                except ImportError:
                    print("⚠️  pytesseract not available, using raw extraction")
                    text = page.get_text()
            
            pages.append({"page": page_num + 1, "content": text.strip()})
            
            # Print progress
            if verbose:
                print(f"{'='*70}")
                print(f"📖 PAGE {page_num + 1}/{len(doc)}")
                print(f"{'='*70}")
                # Print first 500 characters of the page
                preview = text.strip()[:500]
                print(preview)
                if len(text.strip()) > 500:
                    print(f"\n... ({len(text.strip())} total characters)")
                print(f"{'='*70}\n")
        
        doc.close()
        
    except Exception as e:
        return json.dumps({"error": f"Failed to extract PDF: {str(e)}"})
    
    return json.dumps(pages)


# ==========
# 2️⃣ PITCH DECK ANALYZER TOOL
# ==========

def analyze_pitchdeck(file_path: str, verbose: bool = True) -> str:
    """Full pipeline: extract text from a PDF and analyze it using an LLM.

    Args:
        file_path (str): Path to the pitch deck PDF.
        verbose (bool): If True, prints extraction progress.

    Returns:
        str: Structured JSON-style summary with startup insights.
    """
    # Extract text first
    print("🔍 Extracting text from PDF...\n")
    extracted_text = extract_pdf_text(file_path, verbose=verbose)
    data = json.loads(extracted_text)

    if "error" in data:
        return extracted_text

    # Combine all text into one document for LLM analysis
    full_text = "\n\n".join([f"Page {p['page']}:\n{p['content']}" for p in data])

    print(f"\n✅ Successfully extracted {len(data)} pages of text")
    print(f"📊 Total characters: {len(full_text)}\n")
    print("🤖 Sending to LLM for analysis...\n")

    # Call the analyzer agent
    response = pitchdeck_agent.run(
        f"Analyze this startup pitch deck content and extract structured insights:\n\n{full_text}"
    )

    return response.content


# ==========
# 3️⃣ AGENT DEFINITION
# ==========

pitchdeck_agent = Agent(
    model=OpenAIChat(id="gpt-5-mini"),
    instructions=dedent("""\
        You are a startup analyst and venture scout who reviews pitch decks 🦄.
        Your job is to extract and structure startup insights from PDF content.

        **Analysis goals:**
        - Identify: Startup name, tagline, and value proposition
        - Founders: Number of founders, names, short bios if mentioned
        - Product: Problem being solved, solution, target market
        - Metrics: Traction, funding, or growth indicators
        - Additional: Notable partnerships, technology, or GTM strategy

        **Formatting:**
        Return the output as a clean JSON-like Markdown block:
```json
        {
          "startup_name": "...",
          "value_proposition": "...",
          "number_of_founders": ...,
          "founders": ["...", "..."],
          "problem": "...",
          "solution": "...",
          "target_market": "...",
          "traction": "...",
          "funding": "...",
          "notable_points": "...",
          "summary": "..."
        }
```

        - Be concise and factual.
        - If a field is missing, set it to null.
        - End with a one-line investor remark, e.g.:
          "🚀 Strong early-stage potential in a growing market."
    """),
    markdown=True,
)


# ==========
# 4️⃣ EXAMPLE USAGE
# ==========

if __name__ == "__main__":
    # Example pitch deck to analyze
    pdf_path = "./pitch/airbnb-pitch-deck.pdf"

    print("\n" + "="*70)
    print("🚀 PITCH DECK ANALYZER")
    print("="*70 + "\n")

    output = analyze_pitchdeck(pdf_path, verbose=True)
    
    print("\n" + "="*70)
    print("📊 ANALYSIS RESULTS")
    print("="*70 + "\n")
    print(output)
    
    print("\n" + "="*70)
    print("✅ DONE!")
    print("="*70 + "\n")