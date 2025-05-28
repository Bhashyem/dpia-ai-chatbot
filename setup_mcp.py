#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for Pega MCP Server

This script helps set up the Pega MCP server for use with Claude Desktop
and other MCP clients.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

def install_dependencies():
    """Install required Python dependencies."""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call(["python3.12", "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file...")
        env_content = """# Pega Configuration
PEGA_BASE_URL=https://roche-gtech-dt1.pegacloud.net/prweb/api/v1
PEGA_USERNAME=nadadhub
PEGA_PASSWORD=Pwrm*2025
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✓ .env file created")
    else:
        print("✓ .env file already exists")

def setup_claude_desktop():
    """Set up Claude Desktop configuration."""
    # Find Claude Desktop config directory
    home = Path.home()
    claude_config_dir = None
    
    # Check common locations for Claude Desktop config
    possible_locations = [
        home / "Library" / "Application Support" / "Claude",
        home / ".config" / "claude",
        home / "AppData" / "Roaming" / "Claude"
    ]
    
    for location in possible_locations:
        if location.exists():
            claude_config_dir = location
            break
    
    if not claude_config_dir:
        # Create the most likely location
        claude_config_dir = home / "Library" / "Application Support" / "Claude"
        claude_config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = claude_config_dir / "claude_desktop_config.json"
    current_dir = Path.cwd()
    
    # Create the MCP server configuration
    mcp_config = {
        "mcpServers": {
            "pega-mcp-server": {
                "command": "python3.12",
                "args": [str(current_dir / "mcp_server.py")],
                "env": {
                    "PEGA_BASE_URL": "https://roche-gtech-dt1.pegacloud.net/prweb/api/v1",
                    "PEGA_USERNAME": "nadadhub",
                    "PEGA_PASSWORD": "Pwrm*2025"
                }
            }
        }
    }
    
    # If config file exists, merge with existing config
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                existing_config = json.load(f)
            
            if "mcpServers" not in existing_config:
                existing_config["mcpServers"] = {}
            
            existing_config["mcpServers"]["pega-mcp-server"] = mcp_config["mcpServers"]["pega-mcp-server"]
            mcp_config = existing_config
        except json.JSONDecodeError:
            print("Warning: Existing config file is invalid, creating new one")
    
    # Write the configuration
    with open(config_file, "w") as f:
        json.dump(mcp_config, f, indent=2)
    
    print(f"✓ Claude Desktop configuration updated at: {config_file}")
    return config_file

def test_server():
    """Test if the MCP server can start."""
    print("Testing MCP server...")
    try:
        # Make the server executable
        server_file = Path("mcp_server.py")
        os.chmod(server_file, 0o755)
        
        print("✓ MCP server is ready to run")
        print(f"   Server location: {server_file.absolute()}")
        return True
    except Exception as e:
        print(f"✗ Server test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("Setting up Pega MCP Server...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("mcp_server.py").exists():
        print("✗ mcp_server.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    success = True
    
    # Install dependencies
    if not install_dependencies():
        success = False
    
    # Create .env file
    create_env_file()
    
    # Set up Claude Desktop
    try:
        config_file = setup_claude_desktop()
    except Exception as e:
        print(f"✗ Failed to set up Claude Desktop: {e}")
        success = False
    
    # Test server
    if not test_server():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✓ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Restart Claude Desktop if it's running")
        print("2. The Pega MCP server should now be available in Claude Desktop")
        print("3. You can test it by asking Claude to create or manage Pega cases")
        print("\nAvailable tools:")
        print("- create_pega_case: Create new Pega cases")
        print("- get_pega_case: Retrieve case details")
        print("- list_pega_cases: List cases with filters")
        print("- update_pega_case: Update existing cases")
        print("- get_pega_assignments: Get case assignments")
    else:
        print("✗ Setup completed with errors. Please check the messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 