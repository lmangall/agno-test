import json
from textwrap import dedent
from pathlib import Path
import base64
import fitz  # PyMuPDF
from dotenv import load_dotenv
try:
    from PIL import Image
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

import openai
from agno.agent import Agent
from agno.models.openai.responses import OpenAIResponses

# Load environment variables
load_dotenv()


# ==========
# OCR HELPER FUNCTION (OpenAI Vision API)
# ==========
def ocr_with_vision_sdk(image_base64: str) -> str:
    """Extract text from an image using OpenAI Vision API (GPT-4o-mini)."""
    image_data = f"data:image/png;base64,{image_base64}"
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extract all text from this image. Return only text, "
                            "preserve layout and structure as much as possible."
                        )
                    },
                    {"type": "image_url", "image_url": {"url": image_data}}
                ]
            }
        ],
        max_tokens=2000
    )
    return response.choices[0].message.content


# ==========
# PDF TEXT EXTRACTOR
# ==========
def extract_pdf_text(file_path: str, verbose: bool = True, force_ocr: bool = False) -> str:
    """Extract text from PDF page by page with optional OCR fallback."""
    pdf_path = Path(file_path)
    if not pdf_path.exists():
        return json.dumps({"error": f"File not found: {file_path}"})

    pages = []
    try:
        doc = fitz.open(str(pdf_path))
        print(f"📄 Found {len(doc)} pages in PDF\n")

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()

            needs_better_extraction = not text.strip() or "(cid:" in text \
                                      or len([c for c in text if ord(c) > 127]) > len(text) * 0.3

            if needs_better_extraction or force_ocr:
                if force_ocr:
                    print(f"🔍 Using enhanced extraction for page {page_num + 1} (forced mode)")
                else:
                    print(f"⚠️ Page {page_num + 1} has encoding issues, trying enhanced extraction...")

                methods_tried = []

                # If force_ocr is True, skip other methods and go straight to Vision OCR
                if not force_ocr:
                    # Method 1: dict reconstruction
                    try:
                        blocks = page.get_text("dict")["blocks"]
                        parts = []
                        for block in blocks:
                            if "lines" in block:
                                for line in block["lines"]:
                                    for span in line["spans"]:
                                        t = span.get("text", "")
                                        if t.strip():
                                            parts.append(t)
                        reconstructed = " ".join(parts)
                        if reconstructed and len(reconstructed) > len(text):
                            text = reconstructed
                            methods_tried.append("dict_reconstruction")
                    except:
                        pass

                    # Method 2: HTML extraction
                    try:
                        html_text = page.get_text("html")
                        import re
                        clean_text = re.sub(r"<[^>]+>", " ", html_text)
                        clean_text = re.sub(r"\s+", " ", clean_text).strip()
                        if clean_text and len(clean_text) > len(text):
                            text = clean_text
                            methods_tried.append("html_extraction")
                    except:
                        pass

                # Method 3: Vision OCR
                has_artifacts = '&#x' in text or len([c for c in text if ord(c) > 127]) > len(text) * 0.1
                if PIL_AVAILABLE and (force_ocr or has_artifacts or not methods_tried):
                    try:
                        pix = page.get_pixmap(dpi=300)
                        img_data = pix.tobytes("png")
                        img_base64 = base64.b64encode(img_data).decode("utf-8")
                        ocr_text = ocr_with_vision_sdk(img_base64)
                        if ocr_text and len(ocr_text.strip()) > 50:
                            text = ocr_text
                            methods_tried.append("vision_ocr")
                    except Exception as e:
                        print(f"Vision OCR failed: {str(e)[:100]}...")

                if methods_tried:
                    print(f"✅ Enhanced extraction successful using: {', '.join(methods_tried)}")

            pages.append({"page": page_num + 1, "content": text.strip()})

            if verbose:
                print(f"{'='*70}")
                print(f"📖 PAGE {page_num + 1}/{len(doc)}")
                print(f"{'='*70}")
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
# AGENT DEFINITION (OpenAIResponses)
# ==========
pitchdeck_agent = Agent(
    model=OpenAIResponses(id="gpt-4o-mini"),
    instructions=dedent("""\
        You are a startup analyst and venture scout who reviews pitch decks 🦄.
        Extract structured startup insights from PDF text.

        **Goals:**
        - startup_name, value_proposition
        - number_of_founders, founders
        - problem, solution, target_market
        - traction, funding, notable_points
        - summary

        Return a clean JSON block only.
        Set missing fields to null.
        End with a one-line investor remark.
    """),
    markdown=True
)


# ==========
# PITCH DECK ANALYZER
# ==========
def analyze_pitchdeck(file_path: str, verbose: bool = True, force_ocr: bool = False) -> str:
    """Extract text from PDF and analyze with LLM via Agno."""
    print("🔍 Extracting text from PDF...\n")
    extracted_text = extract_pdf_text(file_path, verbose=verbose, force_ocr=force_ocr)
    data = json.loads(extracted_text)

    if "error" in data:
        return extracted_text

    full_text = "\n\n".join([f"Page {p['page']}:\n{p['content']}" for p in data])

    print(f"\n✅ Extracted {len(data)} pages, {len(full_text)} characters")
    print("🤖 Sending to LLM for analysis...\n")

    response = pitchdeck_agent.run(
        f"Analyze this startup pitch deck content and extract structured insights:\n\n{full_text}"
    )
    return response.content


# ==========
# EXAMPLE USAGE
# ==========
if __name__ == "__main__":
    pdf_path = "./pitch/airbnb-pitch-deck.pdf"

    print("\n" + "="*70)
    print("🚀 PITCH DECK ANALYZER")
    print("="*70 + "\n")

    output = analyze_pitchdeck(pdf_path, verbose=True, force_ocr=True)

    print("\n" + "="*70)
    print("📊 ANALYSIS RESULTS")
    print("="*70 + "\n")
    print(output)

    print("\n" + "="*70)
    print("✅ DONE!")
    print("="*70 + "\n")
