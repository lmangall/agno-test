#!/usr/bin/env python3
"""Test script for full pitch deck analysis with LinkedIn lookup."""

import sys
from analyze_pitchdeck import analyze_pitchdeck
import json


def test_full_analysis(pdf_path: str, lookup_founders: bool = True):
    """Test the full pitch deck analysis with optional LinkedIn lookup.
    
    Args:
        pdf_path: Path to the PDF file
        lookup_founders: Whether to look up founders on LinkedIn
    """
    print("\n" + "="*70)
    print("🚀 PITCH DECK ANALYZER WITH LINKEDIN LOOKUP")
    print("="*70 + "\n")
    
    print(f"📄 PDF: {pdf_path}")
    print(f"🔍 LinkedIn Lookup: {'Enabled' if lookup_founders else 'Disabled'}")
    print()
    
    # Run the analysis
    result = analyze_pitchdeck(
        pdf_path, 
        verbose=True, 
        force_ocr=True,
        lookup_founders=lookup_founders
    )
    
    print("\n" + "="*70)
    print("📊 ANALYSIS RESULTS")
    print("="*70 + "\n")
    
    # Try to pretty print if it's JSON
    try:
        parsed = json.loads(result)
        print(json.dumps(parsed, indent=2))
    except:
        print(result)
    
    print("\n" + "="*70)
    print("✅ DONE!")
    print("="*70 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_full_analysis.py <pdf_path> [lookup_founders]")
        print("\nExamples:")
        print('  python test_full_analysis.py ./pitch/airbnb-pitch-deck.pdf')
        print('  python test_full_analysis.py ./pitch/airbnb-pitch-deck.pdf true')
        print('  python test_full_analysis.py ./pitch/airbnb-pitch-deck.pdf false')
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Parse lookup_founders argument
    lookup_founders = True  # Default
    if len(sys.argv) > 2:
        lookup_arg = sys.argv[2].lower()
        lookup_founders = lookup_arg in ['true', '1', 'yes', 'y']
    
    test_full_analysis(pdf_path, lookup_founders)
