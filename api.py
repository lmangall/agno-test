from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from pydantic import BaseModel
from typing import Optional
import os
import tempfile
from pathlib import Path
from analyze_pitchdeck import analyze_pitchdeck

app = FastAPI(
    title="Pitch Deck Analyzer API",
    description="AI-powered pitch deck analysis with LinkedIn founder lookup",
    version="2.0.0"
)

# Response model
class AnalysisResponse(BaseModel):
    analysis: str

@app.get("/")
async def root():
    return {
        "message": "Pitch Deck Analyzer API with LinkedIn Lookup",
        "version": "2.0.0",
        "endpoints": {
            "/analyze": "POST - Analyze a pitch deck PDF (add ?lookup_founders=true for LinkedIn lookup)",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_deck(
    file: UploadFile = File(...),
    lookup_founders: bool = Query(False, description="Look up founders on LinkedIn after analysis")
):
    """
    Upload a PDF pitch deck and get AI-powered analysis.
    Uses OpenAI Vision OCR for all pages.
    
    - **file**: PDF file to analyze
    - **lookup_founders**: If true, automatically looks up founders on LinkedIn (requires UNIPILE_ACCOUNT_ID in env)
    
    Example with LinkedIn lookup:
    ```
    curl -X POST "http://localhost:8000/analyze?lookup_founders=true" -F "file=@pitch.pdf"
    ```
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        if lookup_founders:
            print(f"🚀 Analyzing pitch deck with OpenAI Vision OCR + LinkedIn founder lookup")
        else:
            print(f"🚀 Analyzing pitch deck with OpenAI Vision OCR")
            
        # Analyze the pitch deck with optional LinkedIn lookup
        analysis = analyze_pitchdeck(
            tmp_path, 
            verbose=False, 
            force_ocr=True,
            lookup_founders=lookup_founders
        )
        
        # Clean up the temporary file
        Path(tmp_path).unlink()
        
        return AnalysisResponse(analysis=analysis)
    
    except Exception as e:
        # Clean up on error
        if 'tmp_path' in locals():
            try:
                Path(tmp_path).unlink()
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
