#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to demonstrate interactive validation
"""

from scanning_summarizer import ScanningRequestSummarizer

def test_interactive_validation():
    """Test the interactive validation with sample research text"""
    
    research_text = """We have 4 groups (healthy, injured+vehicle control, treatment 1(Rmim), treatment 2 (Wmim).Lung stem cells (AT2-TRITC) and total cells (DAPI) are stained. N=9-10 per group were stained and need imaging and quantification. I am interested in imaging of AT2 (TRITC) stem cells and DAPI and quantification of: 1. # of AT2 cells per lung section 2. # of AT2 cells normalized by total area of lung section 3. # of AT2 cells normalized by # of DAPI cells per lung section. This is a scanning request for pathology analysis."""
    
    print("Interactive Validation Test")
    print("=" * 50)
    print("Research Text: " + research_text[:100] + "...")
    print()
    
    summarizer = ScanningRequestSummarizer()
    
    # Extract scanning requests (this will trigger validation)
    extracted_data = summarizer.extract_scanning_requests(research_text)
    
    print("\nEXTRACTED DATA:")
    print("=" * 50)
    
    for entry in extracted_data:
        print("Request ID: " + entry['Pathology Request No.'])
        print("Status: " + entry['Status'])
        print("Therapeutic Area: " + entry['Therapeutic Area'])
        print("Procedure: " + entry['Procedure'])
        print("Assay Type: " + entry['Assay Type/Staining Type'])
        print("PI: " + entry['PI'])
        print("Pathologist: " + entry['Pathologist'])
        print("Project Title: " + entry['Project Title'])
        print("Request Purpose: " + entry['Request Purpose'])
        print()

if __name__ == "__main__":
    test_interactive_validation() 