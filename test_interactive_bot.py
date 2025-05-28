#!/usr/bin/env python3
"""
Test the Interactive DPIA Analysis AI Bot
"""

import requests
import json

def test_interactive_bot():
    """Test the interactive prompting functionality"""
    
    research_text = """We have 4 groups (healthy, injured+vehicle control, treatment 1(Rmim), treatment 2 (Wmim).Lung stem cells (AT2-TRITC) and total cells (DAPI) are stained. N=9-10 per group were stained and need imaging and quantification. I am interested in imaging of AT2 (TRITC) stem cells and DAPI and quantification of: 1. # of AT2 cells per lung section 2. # of AT2 cells normalized by total area of lung section 3. # of AT2 cells normalized by # of DAPI cells per lung section"""
    
    print("🤖 Testing Interactive DPIA Analysis AI Bot")
    print("=" * 60)
    
    # Step 1: Initial analysis (should trigger interactive prompts)
    print("Step 1: Initial Analysis - Should trigger interactive prompts")
    print("-" * 50)
    
    payload = {
        "name": "analyze_and_create_dpia",
        "arguments": {
            "research_text": research_text,
            "auto_create": True  # Try to create, but should prompt for missing fields
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
            
            print(f"✅ Success: {content['success']}")
            print(f"📝 Message: {content['message']}")
            print(f"🔄 Requires Interaction: {content.get('requires_interaction', False)}")
            
            if content.get('analysis') and content['analysis'].get('interactive_prompts'):
                print(f"\n🤖 Interactive Prompts ({len(content['analysis']['interactive_prompts'])}):")
                for i, prompt in enumerate(content['analysis']['interactive_prompts'], 1):
                    print(f"\n   {i}. {prompt['field']} ({prompt['type']}):")
                    print(f"      {prompt['prompt']}")
                    if prompt['type'] == 'selection':
                        print(f"      Options: {', '.join(prompt['options'])}")
                    elif prompt['type'] == 'text_input' and 'suggestions' in prompt:
                        print(f"      Suggestions: {', '.join(prompt['suggestions'])}")
                
                # Step 2: Provide responses to prompts
                print(f"\n" + "=" * 60)
                print("Step 2: Providing responses to interactive prompts")
                print("-" * 50)
                
                # Simulate user responses
                prompt_responses = {}
                for prompt in content['analysis']['interactive_prompts']:
                    if prompt['field'] == 'Pathologist':
                        prompt_responses['Pathologist'] = 'Dr. Bhashyam'
                        print(f"   🔬 Pathologist: Dr. Bhashyam")
                    elif prompt['field'] == 'Therapeutic Area':
                        prompt_responses['Therapeutic Area'] = 'Neurology'
                        print(f"   🏥 Therapeutic Area: Neurology")
                    elif prompt['field'] == 'Project Title':
                        prompt_responses['Project Title'] = 'Lung Stem Cell AT2 Quantification Study'
                        print(f"   📋 Project Title: Lung Stem Cell AT2 Quantification Study")
                    elif prompt['field'] == 'PI':
                        prompt_responses['PI'] = 'Dr. Research Lead'
                        print(f"   👨‍🔬 PI: Dr. Research Lead")
                
                # Step 3: Submit responses and create case
                print(f"\n" + "=" * 60)
                print("Step 3: Submitting responses and creating DPIA case")
                print("-" * 50)
                
                payload_with_responses = {
                    "name": "analyze_and_create_dpia",
                    "arguments": {
                        "research_text": research_text,
                        "auto_create": True,
                        "prompt_responses": prompt_responses
                    }
                }
                
                response2 = requests.post(
                    "http://localhost:8080/tools/call",
                    json=payload_with_responses,
                    timeout=30
                )
                
                if response2.status_code == 200:
                    result2 = response2.json()
                    content2 = json.loads(result2["content"][0]["text"])
                    
                    print(f"✅ Success: {content2['success']}")
                    print(f"📝 Message: {content2['message']}")
                    
                    if content2.get('case_created'):
                        print(f"\n🎉 DPIA Case Created Successfully!")
                        print(f"   📋 Case ID: {content2['case_id']}")
                        print(f"   ✅ Validation: {content2['summary']['validation_status']}")
                        print(f"   📊 Fields: {content2['summary']['detected_fields']}/{content2['summary']['total_fields']}")
                        
                        # Show final detected fields
                        if content2.get('analysis') and content2['analysis'].get('detected_fields'):
                            print(f"\n📋 Final Field Values:")
                            for field, value in content2['analysis']['detected_fields'].items():
                                status = "✅" if value != "Unknown" else "❌"
                                print(f"   {status} {field}: {value}")
                    else:
                        print(f"❌ Case creation failed")
                        if 'error' in content2:
                            print(f"   Error: {content2['error']}")
                
                else:
                    print(f"❌ Error in step 3: {response2.status_code} - {response2.text}")
            
            else:
                print("ℹ️ No interactive prompts needed - all fields detected!")
                
        else:
            print(f"❌ Error in step 1: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("💡 Make sure the MCP server is running on localhost:8080")

if __name__ == "__main__":
    test_interactive_bot() 