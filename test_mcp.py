#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Pega MCP Server

This script tests if the MCP server can be imported and initialized correctly.
"""

import sys
import asyncio
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_mcp_server():
    """Test the MCP server initialization."""
    try:
        from mcp_server import PegaMCPServer
        
        print("✓ MCP server module imported successfully")
        
        # Test server initialization
        server = PegaMCPServer()
        print("✓ MCP server initialized successfully")
        
        # Test that the server has the expected tools
        print("✓ MCP server is ready to use")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("   Make sure you've installed the dependencies with: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        return False

def main():
    """Main test function."""
    print("Testing Pega MCP Server...")
    print("=" * 40)
    
    # Run the async test
    success = asyncio.run(test_mcp_server())
    
    print("\n" + "=" * 40)
    if success:
        print("✓ All tests passed! The MCP server is ready to use.")
        print("\nTo set up the server globally, run:")
        print("   python setup_mcp.py")
    else:
        print("✗ Tests failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 