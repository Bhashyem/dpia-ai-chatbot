#!/usr/bin/env python3
"""
Simple DPIA Case Creation Tool
Creates a Scanning request case in Pega with a single command.
"""

import requests
import json
import base64
import sys
import os
from datetime import datetime

# Pega Configuration
PEGA_BASE_URL = "https://roche-gtech-dt1.pegacloud.net/prweb/api/v1"
PEGA_USERNAME = "nadadhub"
PEGA_PASSWORD = "Pwrm*2025"

# Basic auth header
BASIC_AUTH = base64.b64encode(f"{PEGA_USERNAME}:{PEGA_PASSWORD}".encode()).decode()

def create_dpia_case(title=None, description=None):
    """Create a Scanning request case in Pega"""
    
    # Default values if not provided
    if not title:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        title = f"Scanning request - {timestamp}"
    
    if not description:
        description = "DPIA Scanning Request"
    
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
            "pxCreatedFromChannel": "API"
        }
    }
    
    url = f"{PEGA_BASE_URL}/cases"
    
    print("🔄 Creating Scanning request case...")
    print(f"   Title: {title}")
    print(f"   Description: {description}")
    print(f"   Pega URL: {PEGA_BASE_URL}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        print("\n✅ Scanning request case created successfully!")
        print(f"   Case ID: {result.get('ID', 'N/A')}")
        print(f"   Case Key: {result.get('caseID', 'N/A')}")
        print(f"   Status: {result.get('status', 'N/A')}")
        
        # Pretty print the full response
        print("\n📋 Full Response:")
        print(json.dumps(result, indent=2))
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Failed to create Scanning request case: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"   Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"   Response text: {e.response.text}")
        return None

def main():
    """Main function to handle command line arguments"""
    
    print("🏢 DPIA Scanning Request Tool")
    print("=" * 40)
    
    # Check for command line arguments
    title = None
    description = None
    
    if len(sys.argv) > 1:
        title = sys.argv[1]
    
    if len(sys.argv) > 2:
        description = " ".join(sys.argv[2:])
    
    # Create the DPIA case
    result = create_dpia_case(title, description)
    
    if result:
        print("\n🎉 Scanning request case creation completed!")
        sys.exit(0)
    else:
        print("\n💥 Scanning request case creation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 