#!/usr/bin/env python3
"""
Test script for full interactive DPIA validation flow with all 7 fields
"""

import requests
import json

def test_full_interactive_flow():
    """Test the full interactive flow with responses to all prompts"""
    
    # Test research text
    research_text = """
    We have 4 groups (healthy, injured+vehicle control, treatment 1(Rmim), treatment 2 (Wmim).
    Lung stem cells (AT2-TRITC) and total cells (DAPI) are stained. N=9-10 per group were stained 
    and need imaging and quantification. I am interested in imaging of AT2 (TRITC) stem cells and 
    DAPI and quantification of: 1. # of AT2 cells per lung section 2. # of AT2 cells normalized 
    by total area of lung section 3. # of AT2 cells normalized by # of DAPI cells per lung section
    """
    
    print("🧪 Testing Full Interactive DPIA Validation Flow")
    print("=" * 60)
    print(f"📝 Research Text: {research_text[:100]}...")
    print()
    
    # Step 1: Initial analysis (no auto-create)
    print("🔍 Step 1: Initial Analysis")
    print("-" * 30)
    
    payload_step1 = {
        "name": "analyze_and_create_dpia",
        "arguments": {
            "research_text": research_text,
            "auto_create": False
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/tools/call",
            headers={"Content-Type": "application/json"},
            json=payload_step1,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("content") and result["content"][0].get("text"):
                analysis = json.loads(result["content"][0]["text"])
                
                if analysis.get("success"):
                    detected_fields = analysis.get("analysis", {}).get("detected_fields", {})
                    missing_fields = analysis.get("analysis", {}).get("missing_fields", [])
                    interactive_prompts = analysis.get("analysis", {}).get("interactive_prompts", [])
                    
                    print("✅ Initial Analysis Results:")
                    for field, value in detected_fields.items():
                        status = "✅" if value != "Unknown" else "❌"
                        print(f"   {status} {field}: {value}")
                    
                    print(f"\n📊 Summary: {len([v for v in detected_fields.values() if v != 'Unknown'])}/7 fields detected")
                    print(f"❌ Missing Fields: {', '.join(missing_fields)}")
                    
                    if interactive_prompts:
                        print(f"\n💬 Interactive Prompts Required: {len(interactive_prompts)}")
                        
                        # Step 2: Provide responses to interactive prompts
                        print("\n🤖 Step 2: Providing Interactive Responses")
                        print("-" * 40)
                        
                        # Simulate user responses
                        prompt_responses = {
                            "Pathologist": "Dr. Bhashyam",
                            "Therapeutic Area": "Neurology",
                            "Project Title": "Lung Stem Cell AT2 Quantification Study",
                            "PI": "Dr. Research Lead"
                        }
                        
                        print("📝 Simulated User Responses:")
                        for field, response in prompt_responses.items():
                            print(f"   • {field}: {response}")
                        
                        # Step 3: Submit with responses and create case
                        print("\n🚀 Step 3: Creating DPIA Case with Complete Information")
                        print("-" * 50)
                        
                        payload_step3 = {
                            "name": "analyze_and_create_dpia",
                            "arguments": {
                                "research_text": research_text,
                                "prompt_responses": prompt_responses,
                                "auto_create": True
                            }
                        }
                        
                        response_step3 = requests.post(
                            "http://localhost:8080/tools/call",
                            headers={"Content-Type": "application/json"},
                            json=payload_step3,
                            timeout=30
                        )
                        
                        if response_step3.status_code == 200:
                            result_step3 = response_step3.json()
                            
                            if result_step3.get("content") and result_step3["content"][0].get("text"):
                                final_analysis = json.loads(result_step3["content"][0]["text"])
                                
                                if final_analysis.get("success"):
                                    print("🎉 DPIA Case Creation Results:")
                                    
                                    if final_analysis.get("case_created"):
                                        case_id = final_analysis.get("case_id", "Unknown")
                                        print(f"   ✅ Case Created Successfully!")
                                        print(f"   📋 Case ID: {case_id}")
                                        
                                        final_fields = final_analysis.get("analysis", {}).get("detected_fields", {})
                                        print(f"\n📊 Final Field Status:")
                                        for field, value in final_fields.items():
                                            print(f"   ✅ {field}: {value}")
                                        
                                        validation_status = final_analysis.get("summary", {}).get("validation_status", "Unknown")
                                        print(f"\n🎯 Final Validation Status: {validation_status}")
                                        print(f"💡 Message: {final_analysis.get('message', 'No message')}")
                                        
                                    else:
                                        print(f"   ❌ Case creation failed: {final_analysis.get('error', 'Unknown error')}")
                                else:
                                    print(f"   ❌ Final analysis failed: {final_analysis.get('error', 'Unknown error')}")
                            else:
                                print("   ❌ Invalid response format from step 3")
                        else:
                            print(f"   ❌ Server error in step 3: {response_step3.status_code}")
                    else:
                        print("✅ No interactive prompts needed - all fields detected!")
                else:
                    print(f"❌ Initial analysis failed: {analysis.get('error', 'Unknown error')}")
            else:
                print("❌ Invalid response format from step 1")
        else:
            print(f"❌ Server error in step 1: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_full_interactive_flow() 