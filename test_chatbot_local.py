#!/usr/bin/env python3
"""
Test script to verify DPIA Analysis AI Chatbot local setup
"""

import requests
import json
import time

def test_server_health():
    """Test if the MCP server is running and healthy"""
    try:
        response = requests.get('http://localhost:8080/health', timeout=5)
        if response.status_code == 200:
            print("✅ MCP Server is running and healthy")
            return True
        else:
            print(f"❌ MCP Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ MCP Server is not running or not accessible on localhost:8080")
        return False
    except Exception as e:
        print(f"❌ Error connecting to MCP Server: {e}")
        return False

def test_analyze_api():
    """Test the analyze_and_create_dpia API endpoint"""
    try:
        test_data = {
            "name": "analyze_and_create_dpia",
            "arguments": {
                "research_text": "We have 4 groups (healthy, injured+vehicle control, treatment 1(Rmim), treatment 2 (Wmim).Lung stem cells (AT2-TRITC) and total cells (DAPI) are stained. N=9-10 per group were stained and need imaging and quantification.",
                "action": "analyze_only"
            }
        }
        
        response = requests.post(
            'http://localhost:8080/tools/call',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis API is working")
            print(f"📊 Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Analysis API returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Analysis API: {e}")
        return False

def test_chatbot_files():
    """Check if chatbot files exist"""
    import os
    
    files_to_check = [
        'dpia_chatbot.html',
        'dpia_chatbot_production.html',
        'simple_mcp_server.py'
    ]
    
    all_exist = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} is missing")
            all_exist = False
    
    return all_exist

def main():
    print("🤖 DPIA Analysis AI Chatbot - Local Setup Test")
    print("=" * 50)
    
    # Test 1: Check files
    print("\n1. Checking required files...")
    files_ok = test_chatbot_files()
    
    # Test 2: Check server health
    print("\n2. Testing MCP Server health...")
    server_ok = test_server_health()
    
    # Test 3: Test API
    if server_ok:
        print("\n3. Testing Analysis API...")
        api_ok = test_analyze_api()
    else:
        print("\n3. Skipping API test (server not running)")
        api_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY:")
    print(f"Files: {'✅ OK' if files_ok else '❌ MISSING'}")
    print(f"Server: {'✅ RUNNING' if server_ok else '❌ NOT RUNNING'}")
    print(f"API: {'✅ WORKING' if api_ok else '❌ NOT WORKING'}")
    
    if all([files_ok, server_ok, api_ok]):
        print("\n🎉 All tests passed! Your local setup is working correctly.")
        print("\n🚀 Next steps:")
        print("1. Open dpia_chatbot_production.html in your browser")
        print("2. You should see 'Connected to DPIA Analysis Server' status")
        print("3. Try the sample text to test the full workflow")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        if not server_ok:
            print("\n💡 To start the MCP server:")
            print("   python3 simple_mcp_server.py")

if __name__ == "__main__":
    main() 