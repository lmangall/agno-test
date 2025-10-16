import json
import os
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
from google_linkedin_search_tool import get_linkedin_usernames_list
from linkedin_search_tool import linkedin_search

# Load environment variables
load_dotenv()


# ==========
# OCR HELPER FUNCTION (OpenAI Vision API)
# ==========
def ocr_with_vision_sdk(image_base64: str) -> str:
    """Extract text from an image using OpenAI Vision API (GPT-4o-mini)."""
    print("🔥 CALLING OPENAI VISION API FOR OCR...")
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
    print("✅ OPENAI VISION API CALL COMPLETED")
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
            
            # If force_ocr is True, skip normal text extraction and go straight to OCR
            if force_ocr:
                print(f"⚡ Page {page_num + 1}: force_ocr=True, skipping normal extraction")
                text = ""
                needs_better_extraction = True
            else:
                text = page.get_text()
                needs_better_extraction = not text.strip() or "(cid:" in text \
                                          or len([c for c in text if ord(c) > 127]) > len(text) * 0.3
                print(f"📄 Page {page_num + 1}: Normal extraction got {len(text)} chars, needs_better: {needs_better_extraction}")

            if needs_better_extraction or force_ocr:
                if force_ocr:
                    print(f"🔍 Using enhanced extraction for page {page_num + 1} (forced mode)")
                else:
                    print(f"⚠️ Page {page_num + 1} has encoding issues, trying enhanced extraction...")

                methods_tried = []

                # If force_ocr is True, go DIRECTLY to Vision OCR
                if force_ocr and PIL_AVAILABLE:
                    try:
                        print(f"📸 Converting page {page_num + 1} to image for Vision OCR (forced)...")
                        pix = page.get_pixmap(dpi=300)
                        img_data = pix.tobytes("png")
                        img_base64 = base64.b64encode(img_data).decode("utf-8")
                        print(f"📤 Image size: {len(img_base64)} bytes (base64)")
                        ocr_text = ocr_with_vision_sdk(img_base64)
                        if ocr_text and len(ocr_text.strip()) > 50:
                            text = ocr_text
                            methods_tried.append("vision_ocr_forced")
                            print(f"✅ Vision OCR extracted {len(ocr_text)} characters")
                        else:
                            print(f"⚠️ Vision OCR returned insufficient text: {len(ocr_text.strip()) if ocr_text else 0} chars")
                    except Exception as e:
                        print(f"❌ Vision OCR failed: {str(e)[:100]}...")
                
                # Only try other methods if force_ocr is False
                elif not force_ocr:
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

                    # Method 3: Vision OCR (fallback for non-forced mode)
                    has_artifacts = '&#x' in text or len([c for c in text if ord(c) > 127]) > len(text) * 0.1
                    print(f"🔍 Vision OCR check - PIL_AVAILABLE: {PIL_AVAILABLE}, has_artifacts: {has_artifacts}, methods_tried: {methods_tried}")
                    if PIL_AVAILABLE and (has_artifacts or not methods_tried):
                        try:
                            print(f"📸 Converting page {page_num + 1} to image for Vision OCR...")
                            pix = page.get_pixmap(dpi=300)
                            img_data = pix.tobytes("png")
                            img_base64 = base64.b64encode(img_data).decode("utf-8")
                            print(f"📤 Image size: {len(img_base64)} bytes (base64)")
                            ocr_text = ocr_with_vision_sdk(img_base64)
                            if ocr_text and len(ocr_text.strip()) > 50:
                                text = ocr_text
                                methods_tried.append("vision_ocr")
                                print(f"✅ Vision OCR extracted {len(ocr_text)} characters")
                            else:
                                print(f"⚠️ Vision OCR returned insufficient text: {len(ocr_text.strip()) if ocr_text else 0} chars")
                        except Exception as e:
                            print(f"❌ Vision OCR failed: {str(e)[:100]}...")

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
# LINKEDIN FOUNDER LOOKUP
# ==========
def lookup_founders_on_linkedin(founders_list: list, account_id: str = None) -> dict:
    """Look up founders on LinkedIn using Google search + LinkedIn API.
    
    Args:
        founders_list: List of founder names
        account_id: Unipile account ID (optional, reads from env)
        
    Returns:
        Dictionary with founder LinkedIn profiles
    """
    if not account_id:
        account_id = os.getenv('UNIPILE_ACCOUNT_ID')
    
    if not account_id:
        return {"error": "UNIPILE_ACCOUNT_ID not found in environment"}
    
    founder_profiles = {}
    
    for founder_name in founders_list:
        print(f"\n🔍 Looking up {founder_name} on LinkedIn...")
        
        try:
            # Step 1: Search Google for LinkedIn profiles
            usernames = get_linkedin_usernames_list(founder_name, num_results=3)
            
            if not usernames:
                print(f"   ⚠️  No LinkedIn profiles found for {founder_name}")
                founder_profiles[founder_name] = {"error": "No LinkedIn profile found"}
                continue
            
            print(f"   ✅ Found {len(usernames)} potential profile(s): {', '.join(usernames)}")
            
            # Step 2: Get detailed profile for the first match
            first_username = usernames[0]
            print(f"   📊 Fetching detailed profile for {first_username}...")
            
            profile_data = linkedin_search(
                name_surname=first_username,
                account_id=account_id
            )
            
            if "error" in profile_data:
                print(f"   ⚠️  Error fetching profile: {profile_data.get('error')}")
                founder_profiles[founder_name] = {
                    "username": first_username,
                    "error": profile_data.get('error'),
                    "alternatives": usernames[1:] if len(usernames) > 1 else []
                }
            else:
                print(f"   ✅ Profile retrieved successfully")
                founder_profiles[founder_name] = {
                    "username": first_username,
                    "profile": profile_data,
                    "alternatives": usernames[1:] if len(usernames) > 1 else []
                }
                
        except Exception as e:
            print(f"   ❌ Error looking up {founder_name}: {str(e)}")
            founder_profiles[founder_name] = {"error": str(e)}
    
    return founder_profiles


# ==========
# PITCH DECK ANALYZER
# ==========
def analyze_pitchdeck(file_path: str, verbose: bool = True, force_ocr: bool = False, lookup_founders: bool = False) -> str:
    """Extract text from PDF and analyze with LLM via Agno.
    
    Args:
        file_path: Path to PDF file
        verbose: Print detailed extraction info
        force_ocr: Force OCR for all pages
        lookup_founders: If True, look up founders on LinkedIn after analysis
        
    Returns:
        JSON string with analysis results and optional founder LinkedIn profiles
    """
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
    
    analysis_content = response.content
    
    # If lookup_founders is enabled, extract founder names and look them up
    if lookup_founders:
        print("\n" + "="*70)
        print("🔎 LOOKING UP FOUNDERS ON LINKEDIN")
        print("="*70)
        
        try:
            # Try to parse the analysis to extract founder names
            # Look for founder names in the response
            import re
            
            # Try to find founders in JSON format
            founders_match = re.search(r'"founders":\s*\[(.*?)\]', analysis_content, re.DOTALL)
            if founders_match:
                founders_str = founders_match.group(1)
                # Extract names from JSON array
                founder_names = re.findall(r'"([^"]+)"', founders_str)
                
                if founder_names:
                    print(f"📋 Found {len(founder_names)} founder(s): {', '.join(founder_names)}")
                    
                    # Look up each founder
                    linkedin_profiles = lookup_founders_on_linkedin(founder_names)
                    
                    # Append LinkedIn data to the analysis
                    result = {
                        "analysis": analysis_content,
                        "linkedin_profiles": linkedin_profiles
                    }
                    
                    return json.dumps(result, indent=2)
                else:
                    print("⚠️  No founder names found in analysis")
            else:
                print("⚠️  Could not parse founders from analysis")
                
        except Exception as e:
            print(f"❌ Error during LinkedIn lookup: {str(e)}")
    
    return analysis_content


# ==========
# EXAMPLE USAGE
# ==========
if __name__ == "__main__":
    pdf_path = "./pitch/airbnb-pitch-deck.pdf"

    print("\n" + "="*70)
    print("🚀 PITCH DECK ANALYZER WITH LINKEDIN LOOKUP")
    print("="*70 + "\n")

    # Set lookup_founders=True to enable LinkedIn lookup
    output = analyze_pitchdeck(pdf_path, verbose=True, force_ocr=True, lookup_founders=True)

    print("\n" + "="*70)
    print("📊 ANALYSIS RESULTS")
    print("="*70 + "\n")
    print(output)

    print("\n" + "="*70)
    print("✅ DONE!")
    print("="*70 + "\n")
