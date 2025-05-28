#!/usr/bin/env python3
"""
Test client for the DPIA Analysis AI Bot
"""

import requests
import json

def test_ai_bot():
    """Test the DPIA Analysis AI Bot"""
    
    # Your lung research text
    research_text = """We have 4 groups (healthy, injured+vehicle control, treatment 1(Rmim), treatment 2 (Wmim).Lung stem cells (AT2-TRITC) and total cells (DAPI) are stained. N=9-10 per group were stained and need imaging and quantification. I am interested in imaging of AT2 (TRITC) stem cells and DAPI and quantification of: 1. # of AT2 cells per lung section 2. # of AT2 cells normalized by total area of lung section 3. # of AT2 cells normalized by # of DAPI cells per lung section"""
    
    # Test 1: Analysis only (without creating case)
    print("🤖 Testing DPIA Analysis AI Bot")
    print("=" * 50)
    
    payload = {
        "name": "analyze_and_create_dpia",
        "arguments": {
            "research_text": research_text,
            "auto_create": False  # Just analyze first
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/tools/call",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = json.loads(result["content"][0]["text"])
            
            print("📊 Analysis Results:")
            print(f"✅ Success: {content['success']}")
            print(f"📝 Message: {content['message']}")
            
            if "analysis" in content:
                analysis = content["analysis"]
                print(f"\n🔍 Detected Fields:")
                for field, value in analysis["detected_fields"].items():
                    status = "✅" if value != "Unknown" else "❌"
                    print(f"   {status} {field}: {value}")
                
                print(f"\n💡 AI Recommendations:")
                for rec in analysis["recommendations"]:
                    print(f"   {rec}")
                
                if content["summary"]["validation_status"] == "PASSED":
                    print(f"\n🎉 Ready to create DPIA case!")
                else:
                    print(f"\n⚠️ Missing fields need to be provided")
            
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("💡 Make sure the MCP server is running on localhost:8080")

    # Test 2: Full analysis with case creation
    print("\n" + "=" * 50)
    print("🏢 Testing with Case Creation")
    
    payload_with_case = {
        "name": "analyze_and_create_dpia",
        "arguments": {
            "research_text": research_text,
            "pathologist": "Bhashyam",
            "therapeutic_area": "Neurology",
            "project_title": "Lung Stem Cell AT2 Analysis Study",
            "pi": "Research Team Lead",
            "auto_create": True  # Create the case
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/tools/call",
            json=payload_with_case,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = json.loads(result["content"][0]["text"])
            
            print("📊 Full Analysis + Case Creation:")
            print(f"✅ Success: {content['success']}")
            print(f"📝 Message: {content['message']}")
            
            if content.get("case_created"):
                print(f"🎉 DPIA Case Created!")
                print(f"   Case ID: {content['case_id']}")
                print(f"   Validation: {content['summary']['validation_status']}")
                print(f"   Fields Detected: {content['summary']['detected_fields']}/{content['summary']['total_fields']}")
            
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_ai_bot() 