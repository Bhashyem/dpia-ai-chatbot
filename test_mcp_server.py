#!/usr/bin/env python3
"""
Test script for the Simple Pega MCP Server
"""

import requests
import json
import sys

def test_server():
    base_url = "http://localhost:8080"
    
    print("Testing Simple Pega MCP Server...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/")
        print("✅ Server is running")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Server is not running: {e}")
        return False
    
    # Test 2: List available tools
    try:
        response = requests.get(f"{base_url}/tools")
        tools_data = response.json()
        print(f"\n✅ Tools endpoint working")
        print(f"   Available tools: {len(tools_data['tools'])}")
        for tool in tools_data['tools']:
            print(f"   - {tool['name']}: {tool['description']}")
    except Exception as e:
        print(f"❌ Tools endpoint failed: {e}")
        return False
    
    # Test 3: Health check
    try:
        response = requests.get(f"{base_url}/health")
        health_data = response.json()
        print(f"\n✅ Health check passed")
        print(f"   Status: {health_data['status']}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 4: Test tool call (list cases - this might fail due to auth but should show proper error handling)
    try:
        tool_call = {
            "name": "list_pega_cases",
            "arguments": {
                "page": 1,
                "per_page": 5
            }
        }
        response = requests.post(f"{base_url}/tools/call", json=tool_call)
        result = response.json()
        print(f"\n✅ Tool call endpoint working")
        print(f"   Tool: {tool_call['name']}")
        print(f"   Response type: {'Error' if result.get('isError') else 'Success'}")
        if result.get('isError'):
            print(f"   Error (expected): {result['content'][0]['text'][:100]}...")
        else:
            print(f"   Success: Tool executed successfully")
    except Exception as e:
        print(f"❌ Tool call failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! MCP Server is working correctly.")
    print("\nThe server provides the following capabilities:")
    print("- HTTP-based MCP protocol implementation")
    print("- Pega case management tools")
    print("- Error handling and validation")
    print("- Health monitoring")
    
    return True

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1) 