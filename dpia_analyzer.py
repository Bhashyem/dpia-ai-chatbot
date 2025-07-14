#!/usr/bin/env python3
"""
Combined DPIA Analyzer and Case Creator
Analyzes text for scanning requests and creates DPIA cases in Pega with the results.
"""

import requests
import json
import base64
import sys
import os
import re
from datetime import datetime
from typing import List, Dict, Any

# Import the scanning summarizer functionality
from scanning_summarizer import ScanningRequestSummarizer

# Pega Configuration
PEGA_BASE_URL = "https://roche-gtech-dt1.pegacloud.net/prweb/api/v1"
PEGA_USERNAME = ""
PEGA_PASSWORD = ""

# Basic auth header
BASIC_AUTH = base64.b64encode(f"{PEGA_USERNAME}:{PEGA_PASSWORD}".encode()).decode()

class DPIAAnalyzer:
    def __init__(self):
        self.summarizer = ScanningRequestSummarizer()
    
    def analyze_and_create_case(self, text: str, custom_title: str = None) -> Dict[str, Any]:
        """Analyze text and create DPIA case with results"""
        
        print("🔍 DPIA Analyzer & Case Creator")
        print("=" * 50)
        
        # Step 1: Analyze the text
        print("📝 Step 1: Analyzing text for scanning requests...")
        extracted_data = self.summarizer.extract_scanning_requests(text)
        
        print(f"   ✅ Found {len(extracted_data)} scanning request entries")
        
        # Step 2: Generate summary for case description
        summary = self._generate_case_summary(extracted_data, text)
        
        # Step 3: Create DPIA case
        print("\n🏢 Step 2: Creating DPIA case in Pega...")
        
        # Generate title
        if custom_title:
            title = custom_title
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            if len(extracted_data) > 1:
                title = f"Scanning request - {len(extracted_data)} items found - {timestamp}"
            else:
                title = f"Scanning request - Analysis - {timestamp}"
        
        # Create case
        case_result = self._create_pega_case(title, summary)
        
        # Step 4: Return combined results
        result = {
            "analysis": {
                "text_length": len(text),
                "entries_found": len(extracted_data),
                "scanning_data": extracted_data
            },
            "case": case_result,
            "summary": summary
        }
        
        return result
    
    def _generate_case_summary(self, extracted_data: List[Dict], original_text: str) -> str:
        """Generate a summary for the DPIA case description"""
        
        summary_parts = []
        summary_parts.append("DPIA Scanning Request - Automated Analysis Results")
        summary_parts.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary_parts.append(f"Text Length: {len(original_text)} characters")
        summary_parts.append(f"Scanning Requests Found: {len(extracted_data)}")
        
        if extracted_data and extracted_data[0].get("Status") != "No Match":
            summary_parts.append("\nKey Findings:")
            
            # Extract unique biospecimens
            biospecimens = set()
            assays = set()
            blocks = set()
            
            for entry in extracted_data:
                if entry.get("Biospecimen") and entry.get("Biospecimen") != "N/A":
                    biospecimens.add(entry.get("Biospecimen"))
                if entry.get("Assay Instructions") and entry.get("Assay Instructions") != "N/A":
                    assays.add(entry.get("Assay Instructions")[:30])
                if entry.get("Block id") and entry.get("Block id") != "N/A":
                    blocks.add(entry.get("Block id"))
            
            if biospecimens:
                summary_parts.append(f"- Biospecimens: {', '.join(list(biospecimens)[:3])}")
            if assays:
                summary_parts.append(f"- Assays: {', '.join(list(assays)[:3])}")
            if blocks:
                summary_parts.append(f"- Block IDs: {', '.join(list(blocks)[:3])}")
            
            # Add sample labels
            labels = [entry.get("label", "")[:50] for entry in extracted_data[:3]]
            if labels:
                summary_parts.append(f"\nSample Entries:")
                for i, label in enumerate(labels, 1):
                    summary_parts.append(f"{i}. {label}")
        else:
            summary_parts.append("\nNo specific scanning requests found in text.")
            summary_parts.append("General DPIA assessment recommended.")
        
        return "\n".join(summary_parts)
    
    def _create_pega_case(self, title: str, description: str) -> Dict[str, Any]:
        """Create a DPIA case in Pega"""
        
        headers = {
            "Authorization": f"Basic {BASIC_AUTH}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "caseTypeID": "Roche-Pathworks-Work-DPIA",
            "processID": "pyStartCase",
            "content": {
                "pyLabel": title,
                "pyDescription": description,
                "pxCreatedFromChannel": "API-Analyzer"
            }
        }
        
        url = f"{PEGA_BASE_URL}/cases"
        
        print(f"   Title: {title}")
        print(f"   Description: {description[:100]}...")
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            print(f"\n   ✅ DPIA case created successfully!")
            print(f"   Case ID: {result.get('ID', 'N/A')}")
            
            return {
                "success": True,
                "case_id": result.get('ID', 'N/A'),
                "response": result
            }
            
        except requests.exceptions.RequestException as e:
            print(f"\n   ❌ Failed to create DPIA case: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

def main():
    """Main function to handle command line usage"""
    
    analyzer = DPIAAnalyzer()
    
    # Check for input methods
    custom_title = None
    text = ""
    
    # Parse command line arguments
    if "--title" in sys.argv:
        title_index = sys.argv.index("--title")
        if title_index + 1 < len(sys.argv):
            custom_title = sys.argv[title_index + 1]
    
    # Get text input
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        # Read from file
        filename = sys.argv[1]
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"📄 Reading from file: {filename}")
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            sys.exit(1)
    else:
        # Read from stdin
        print("📝 Enter text to analyze (Ctrl+D to finish):")
        text = sys.stdin.read()
    
    if not text.strip():
        print("❌ No text provided for analysis")
        sys.exit(1)
    
    # Process the text
    result = analyzer.analyze_and_create_case(text, custom_title)
    
    # Display results
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)
    
    print(f"📈 Analysis: {result['analysis']['entries_found']} scanning requests found")
    
    if result['case']['success']:
        print(f"✅ Case Created: {result['case']['case_id']}")
    else:
        print(f"❌ Case Creation Failed: {result['case']['error']}")
    
    # Save detailed results if requested
    if "--save" in sys.argv:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save analysis results
        analysis_file = f"dpia_analysis_{timestamp}.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Detailed results saved to: {analysis_file}")
        
        # Save pathology table
        table_result = analyzer.summarizer.format_as_table(result['analysis']['scanning_data'])
        table_file = f"pathology_table_{timestamp}.txt"
        with open(table_file, 'w', encoding='utf-8') as f:
            f.write(table_result)
        print(f"💾 Pathology table saved to: {table_file}")
    
    # Show pathology table if requested
    if "--table" in sys.argv:
        print("\n📋 PATHOLOGY TABLE:")
        print("-" * 50)
        table_result = analyzer.summarizer.format_as_table(result['analysis']['scanning_data'])
        print(table_result)

if __name__ == "__main__":
    main() 
