#!/usr/bin/env python3
"""
Pega Model Context Protocol Server

This server provides MCP tools for interacting with Pega systems,
allowing AI assistants to create, read, update, and manage Pega cases.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import requests
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pega-mcp-server")

# Pega Configuration
PEGA_BASE_URL = os.getenv("PEGA_BASE_URL", "https://roche-gtech-dt1.pegacloud.net/prweb/api/v1")
PEGA_USERNAME = os.getenv("PEGA_USERNAME", "nadadhub")
PEGA_PASSWORD = os.getenv("PEGA_PASSWORD", "Pwrm*2025")

# Basic auth header
BASIC_AUTH = base64.b64encode(f"{PEGA_USERNAME}:{PEGA_PASSWORD}".encode()).decode()

class PegaMCPServer:
    def __init__(self):
        self.server = Server("pega-mcp-server")
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available Pega tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="create_pega_case",
                        description="Create a new case in Pega",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "caseTypeID": {
                                    "type": "string",
                                    "description": "The case type ID (e.g., 'Roche-Pathworks-Work-DPIA')"
                                },
                                "processID": {
                                    "type": "string",
                                    "description": "The process ID (default: 'pyStartCase')",
                                    "default": "pyStartCase"
                                },
                                "content": {
                                    "type": "object",
                                    "description": "Case content and properties",
                                    "properties": {
                                        "pyLabel": {"type": "string", "description": "Case label/title"},
                                        "pyDescription": {"type": "string", "description": "Case description"},
                                        "pxCreatedFromChannel": {"type": "string", "description": "Channel (default: 'Web')"}
                                    }
                                }
                            },
                            "required": ["caseTypeID"]
                        }
                    ),
                    Tool(
                        name="get_pega_case",
                        description="Retrieve details of a specific Pega case",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "case_id": {
                                    "type": "string",
                                    "description": "The case ID to retrieve"
                                }
                            },
                            "required": ["case_id"]
                        }
                    ),
                    Tool(
                        name="list_pega_cases",
                        description="List Pega cases with optional filters",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "description": "Filter by case status"
                                },
                                "caseTypeID": {
                                    "type": "string",
                                    "description": "Filter by case type"
                                },
                                "page": {
                                    "type": "integer",
                                    "description": "Page number (default: 1)",
                                    "default": 1
                                },
                                "per_page": {
                                    "type": "integer",
                                    "description": "Items per page (default: 25)",
                                    "default": 25
                                }
                            }
                        }
                    ),
                    Tool(
                        name="update_pega_case",
                        description="Update an existing Pega case",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "case_id": {
                                    "type": "string",
                                    "description": "The case ID to update"
                                },
                                "content": {
                                    "type": "object",
                                    "description": "Updated case content and properties"
                                }
                            },
                            "required": ["case_id", "content"]
                        }
                    ),
                    Tool(
                        name="get_pega_assignments",
                        description="Get assignments for a specific case",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "case_id": {
                                    "type": "string",
                                    "description": "The case ID to get assignments for"
                                }
                            },
                            "required": ["case_id"]
                        }
                    )
                ]
            )

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls."""
            try:
                if name == "create_pega_case":
                    return await self._create_case(arguments)
                elif name == "get_pega_case":
                    return await self._get_case(arguments)
                elif name == "list_pega_cases":
                    return await self._list_cases(arguments)
                elif name == "update_pega_case":
                    return await self._update_case(arguments)
                elif name == "get_pega_assignments":
                    return await self._get_assignments(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )

    async def _create_case(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Create a new Pega case."""
        try:
            headers = {
                "Authorization": f"Basic {BASIC_AUTH}",
                "Content-Type": "application/json"
            }
            
            case_type_id = arguments.get("caseTypeID", "Roche-Pathworks-Work-DPIA")
            process_id = arguments.get("processID", "pyStartCase")
            content = arguments.get("content", {})
            
            payload = {
                "caseTypeID": case_type_id,
                "processID": process_id,
                "content": content
            }
            
            response = requests.post(
                f"{PEGA_BASE_URL}/cases",
                json=payload,
                headers=headers,
                verify=True
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Case created successfully:\n{json.dumps(result, indent=2)}"
                    )]
                )
            else:
                error_msg = f"Failed to create case. Status: {response.status_code}, Response: {response.text}"
                return CallToolResult(
                    content=[TextContent(type="text", text=error_msg)]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error creating case: {str(e)}")]
            )

    async def _get_case(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get a specific Pega case."""
        try:
            case_id = arguments["case_id"]
            headers = {
                "Authorization": f"Basic {BASIC_AUTH}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{PEGA_BASE_URL}/cases/{case_id}",
                headers=headers,
                verify=True
            )
            
            if response.status_code == 200:
                result = response.json()
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Case details:\n{json.dumps(result, indent=2)}"
                    )]
                )
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Failed to get case. Status: {response.status_code}, Response: {response.text}"
                    )]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting case: {str(e)}")]
            )

    async def _list_cases(self, arguments: Dict[str, Any]) -> CallToolResult:
        """List Pega cases."""
        try:
            headers = {
                "Authorization": f"Basic {BASIC_AUTH}",
                "Content-Type": "application/json"
            }
            
            params = {}
            if "status" in arguments:
                params["status"] = arguments["status"]
            if "caseTypeID" in arguments:
                params["caseTypeID"] = arguments["caseTypeID"]
            if "page" in arguments:
                params["page"] = arguments["page"]
            if "per_page" in arguments:
                params["per_page"] = arguments["per_page"]
            
            response = requests.get(
                f"{PEGA_BASE_URL}/cases",
                headers=headers,
                params=params,
                verify=True
            )
            
            if response.status_code == 200:
                result = response.json()
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Cases list:\n{json.dumps(result, indent=2)}"
                    )]
                )
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Failed to list cases. Status: {response.status_code}, Response: {response.text}"
                    )]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error listing cases: {str(e)}")]
            )

    async def _update_case(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Update a Pega case."""
        try:
            case_id = arguments["case_id"]
            content = arguments["content"]
            
            headers = {
                "Authorization": f"Basic {BASIC_AUTH}",
                "Content-Type": "application/json"
            }
            
            response = requests.put(
                f"{PEGA_BASE_URL}/cases/{case_id}",
                json=content,
                headers=headers,
                verify=True
            )
            
            if response.status_code in [200, 204]:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Case {case_id} updated successfully"
                    )]
                )
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Failed to update case. Status: {response.status_code}, Response: {response.text}"
                    )]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error updating case: {str(e)}")]
            )

    async def _get_assignments(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get assignments for a case."""
        try:
            case_id = arguments["case_id"]
            headers = {
                "Authorization": f"Basic {BASIC_AUTH}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{PEGA_BASE_URL}/cases/{case_id}/assignments",
                headers=headers,
                verify=True
            )
            
            if response.status_code == 200:
                result = response.json()
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Case assignments:\n{json.dumps(result, indent=2)}"
                    )]
                )
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Failed to get assignments. Status: {response.status_code}, Response: {response.text}"
                    )]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting assignments: {str(e)}")]
            )

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="pega-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

async def main():
    """Main entry point."""
    server = PegaMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main()) 