#!/usr/bin/env python3
"""
Simple MCP-compatible Pega Server for Python 3.9
This server provides basic MCP functionality without requiring the official MCP package.
Enhanced with DPIA Analysis AI Bot functionality.
"""

import json
import sys
import os
import asyncio
import base64
import requests
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from datetime import datetime

# Import our scanning summarizer
from scanning_summarizer import ScanningRequestSummarizer

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Pega Configuration
PEGA_BASE_URL = os.getenv("PEGA_BASE_URL", "https://roche-gtech-dt1.pegacloud.net/prweb/api/v1")
PEGA_USERNAME = os.getenv("PEGA_USERNAME", "nadadhub")
PEGA_PASSWORD = os.getenv("PEGA_PASSWORD", "Pwrm*2025")

# Basic auth header
BASIC_AUTH = base64.b64encode(f"{PEGA_USERNAME}:{PEGA_PASSWORD}".encode()).decode()

app = FastAPI(title="Pega DPIA Analysis MCP Server", version="2.0.0")

# MCP Protocol Models
class Tool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]

class ToolResult(BaseModel):
    content: List[Dict[str, Any]]
    isError: bool = False

# Available tools
TOOLS = [
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
        name="analyze_and_create_dpia",
        description="AI Bot: Analyze research text for DPIA requirements and create a validated case in Pega. This is an intelligent assistant that will guide you through the process.",
        inputSchema={
            "type": "object",
            "properties": {
                "research_text": {
                    "type": "string",
                    "description": "The research text to analyze for DPIA requirements"
                },
                "pathologist": {
                    "type": "string",
                    "description": "Pathologist name (optional - will be prompted if not provided)"
                },
                "therapeutic_area": {
                    "type": "string",
                    "description": "Therapeutic area (optional - will be auto-detected or prompted)"
                },
                "project_title": {
                    "type": "string",
                    "description": "Project title (optional - will be prompted if not provided)"
                },
                "pi": {
                    "type": "string",
                    "description": "Primary Investigator name (optional - will be prompted if not provided)"
                },
                "auto_create": {
                    "type": "boolean",
                    "description": "Whether to automatically create the DPIA case after analysis (default: true)",
                    "default": True
                }
            },
            "required": ["research_text"]
        }
    )
]

@app.get("/")
async def root():
    return {
        "message": "Pega DPIA Analysis MCP Server with AI Bot", 
        "version": "2.0.0",
        "features": [
            "🤖 AI-powered DPIA analysis",
            "🔍 Automatic field detection",
            "✅ Validation and recommendations", 
            "🏢 Automated Pega case creation",
            "📊 Interactive analysis results"
        ],
        "ai_bot": {
            "name": "DPIA Analysis AI Bot",
            "description": "Intelligent assistant for analyzing research text and creating validated DPIA cases",
            "capabilities": [
                "Detect therapeutic areas, procedures, and assay types",
                "Extract PI, pathologist, and project information",
                "Validate mandatory fields",
                "Provide intelligent recommendations",
                "Create complete DPIA cases in Pega"
            ]
        }
    }

@app.get("/tools")
async def list_tools():
    """List available tools"""
    return {"tools": [tool.dict() for tool in TOOLS]}

@app.post("/tools/call")
async def call_tool(tool_call: ToolCall):
    """Execute a tool"""
    try:
        if tool_call.name == "create_pega_case":
            result = await create_case(tool_call.arguments)
        elif tool_call.name == "get_pega_case":
            result = await get_case(tool_call.arguments)
        elif tool_call.name == "list_pega_cases":
            result = await list_cases(tool_call.arguments)
        elif tool_call.name == "analyze_and_create_dpia":
            result = await analyze_and_create_dpia(tool_call.arguments)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_call.name}")
        
        return ToolResult(content=[{"type": "text", "text": json.dumps(result, indent=2)}])
    
    except Exception as e:
        return ToolResult(
            content=[{"type": "text", "text": f"Error: {str(e)}"}],
            isError=True
        )

async def create_case(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new Pega case"""
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
    
    url = f"{PEGA_BASE_URL}/cases"
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to create case: {str(e)}")

async def get_case(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get a specific Pega case"""
    headers = {
        "Authorization": f"Basic {BASIC_AUTH}",
        "Content-Type": "application/json"
    }
    
    case_id = arguments.get("case_id")
    if not case_id:
        raise Exception("case_id is required")
    
    url = f"{PEGA_BASE_URL}/cases/{case_id}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get case: {str(e)}")

async def list_cases(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """List Pega cases"""
    headers = {
        "Authorization": f"Basic {BASIC_AUTH}",
        "Content-Type": "application/json"
    }
    
    params = {}
    if arguments.get("status"):
        params["status"] = arguments["status"]
    if arguments.get("caseTypeID"):
        params["caseTypeID"] = arguments["caseTypeID"]
    
    page = arguments.get("page", 1)
    per_page = arguments.get("per_page", 25)
    params["page"] = page
    params["per_page"] = per_page
    
    url = f"{PEGA_BASE_URL}/cases"
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to list cases: {str(e)}")

async def analyze_and_create_dpia(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """AI Bot: Analyze research text for DPIA requirements and create a validated case in Pega"""
    
    research_text = arguments.get("research_text", "")
    if not research_text:
        return {"error": "Research text is required"}
    
    # Initialize the scanning summarizer
    summarizer = ScanningRequestSummarizer()
    
    # Step 1: Analyze the research text
    analysis_result = {
        "step": "analysis",
        "message": "🤖 DPIA Analysis AI Bot - Starting Analysis...",
        "text_length": len(research_text),
        "detected_fields": {},
        "missing_fields": [],
        "recommendations": [],
        "interactive_prompts": []
    }
    
    try:
        # Detect fields from text
        therapeutic_area = arguments.get("therapeutic_area") or summarizer.detect_therapeutic_area(research_text)
        procedure = summarizer.detect_procedure(research_text)
        assay_staining_type = summarizer.detect_assay_staining_type(research_text)
        pi = arguments.get("pi") or summarizer.detect_pi(research_text)
        pathologist = arguments.get("pathologist") or summarizer.detect_pathologist(research_text)
        project_title = arguments.get("project_title") or summarizer.detect_project_title(research_text)
        request_purpose = summarizer.detect_request_purpose(research_text)
        
        # Store detected fields
        detected_fields = {
            "Therapeutic Area": therapeutic_area,
            "Procedure": procedure,
            "Assay Type/Staining Type": assay_staining_type,
            "PI": pi,
            "Pathologist": pathologist,
            "Project Title": project_title,
            "Request Purpose": request_purpose
        }
        
        analysis_result["detected_fields"] = detected_fields
        
        # Check for missing mandatory fields and create interactive prompts
        missing_fields = []
        interactive_prompts = []
        
        # Enhanced validation - check ALL important fields, not just mandatory ones
        all_important_fields = ["Pathologist", "Therapeutic Area", "Project Title", "PI", "Procedure", "Assay Type/Staining Type", "Request Purpose"]
        
        for field in all_important_fields:
            if field not in detected_fields or detected_fields[field] == "Unknown" or not detected_fields[field]:
                missing_fields.append(field)
                
                # Create interactive prompts for each missing field
                if field == "Pathologist":
                    interactive_prompts.append({
                        "field": "Pathologist",
                        "question": "🔬 I couldn't detect the pathologist name from your research text. Could you please provide the pathologist's name?",
                        "input_type": "text_input",
                        "suggestions": ["Dr. Bhashyam", "Dr. Smith", "Dr. Johnson", "Dr. Wilson"]
                    })
                elif field == "Therapeutic Area":
                    interactive_prompts.append({
                        "field": "Therapeutic Area",
                        "question": "🏥 I couldn't determine the therapeutic area from your research. Please select the most appropriate therapeutic area:",
                        "input_type": "selection",
                        "options": ["CVRM", "Neurology", "Oncology", "Ophthalmology", "Infectious Diseases", "Immunology", "Unknown"]
                    })
                elif field == "Project Title":
                    interactive_prompts.append({
                        "field": "Project Title",
                        "question": "📋 I couldn't extract a clear project title from your research text. Could you provide a descriptive project title?",
                        "input_type": "text_input",
                        "suggestions": ["Lung Stem Cell Analysis", "AT2 Cell Quantification Study", "Fluorescence Imaging Project", "Pathology Research Study"]
                    })
                elif field == "PI":
                    interactive_prompts.append({
                        "field": "PI",
                        "question": "👨‍🔬 I couldn't identify the Primary Investigator from your research text. Who is the PI for this project?",
                        "input_type": "text_input",
                        "suggestions": ["Dr. Research Lead", "Principal Investigator", "Study Director", "Project Lead"]
                    })
                elif field == "Procedure":
                    interactive_prompts.append({
                        "field": "Procedure",
                        "question": "🔬 I couldn't determine the procedure type from your research. Please select the most appropriate procedure:",
                        "input_type": "selection",
                        "options": ["Bright-field (BF)", "Fluorescence (IF)", "BF+IF", "Unknown"]
                    })
                elif field == "Assay Type/Staining Type":
                    interactive_prompts.append({
                        "field": "Assay Type/Staining Type",
                        "question": "🧪 I couldn't identify the assay/staining type from your research. Please select the most appropriate type:",
                        "input_type": "selection",
                        "options": ["H&E", "IHC", "Special Stain", "Other", "Unknown"]
                    })
                elif field == "Request Purpose":
                    interactive_prompts.append({
                        "field": "Request Purpose",
                        "question": "🎯 I couldn't determine the purpose of your research request. Please select or specify the main purpose:",
                        "input_type": "selection",
                        "options": ["Quantification and analysis", "Imaging and documentation", "Biomarker analysis", "Research validation", "Diagnostic support", "Other"]
                    })
        
        analysis_result["missing_fields"] = missing_fields
        analysis_result["interactive_prompts"] = interactive_prompts
        
        # Generate AI recommendations
        recommendations = []
        
        if therapeutic_area != "Unknown":
            recommendations.append(f"✅ Detected therapeutic area: {therapeutic_area}")
        else:
            recommendations.append("⚠️ Could not detect therapeutic area from text. Will prompt for selection.")
            
        if procedure != "Unknown":
            recommendations.append(f"✅ Detected procedure: {procedure}")
        else:
            recommendations.append("⚠️ Could not detect procedure type from text.")
            
        if "TRITC" in research_text.upper() or "DAPI" in research_text.upper():
            recommendations.append("✅ Fluorescent staining detected (TRITC/DAPI)")
            
        if "quantification" in research_text.lower():
            recommendations.append("✅ Quantification analysis detected")
            
        if missing_fields:
            recommendations.append(f"🤖 I need to ask you about {len(missing_fields)} missing field(s): {', '.join(missing_fields)}")
            recommendations.append("💬 I'll guide you through providing this information interactively")
        else:
            recommendations.append("✅ All mandatory fields detected or provided!")
            
        analysis_result["recommendations"] = recommendations
        
        # Step 2: Handle interactive mode or auto-create
        auto_create = arguments.get("auto_create", True)
        
        # Check if we have responses to interactive prompts
        prompt_responses = arguments.get("prompt_responses", {})
        
        # Update fields with prompt responses
        if prompt_responses:
            for field, response in prompt_responses.items():
                if field in detected_fields:
                    detected_fields[field] = response
                    analysis_result["detected_fields"][field] = response
            
            # Recheck missing fields after responses using the same field list
            missing_fields = []
            for field in all_important_fields:
                if field not in detected_fields or detected_fields[field] == "Unknown" or not detected_fields[field]:
                    missing_fields.append(field)
            
            analysis_result["missing_fields"] = missing_fields
        
        # If we still have missing fields, return interactive prompts
        if missing_fields and not prompt_responses:
            return {
                "success": True,
                "analysis": analysis_result,
                "case_created": False,
                "requires_interaction": True,
                "message": f"🤖 Hi! I've analyzed your research and detected {len([f for f in detected_fields.values() if f != 'Unknown'])} out of {len(detected_fields)} fields. I need to ask you about {len(missing_fields)} missing field(s) to create a complete DPIA case.",
                "next_action": "Please provide the missing information using the interactive prompts below.",
                "summary": {
                    "detected_fields": len([f for f in detected_fields.values() if f != "Unknown"]),
                    "total_fields": len(detected_fields),
                    "validation_status": "PENDING_INTERACTION",
                    "recommendations_count": len(recommendations)
                }
            }
        
        # If auto_create is True and all fields are present, create the case
        if auto_create and not missing_fields:
            # Create the DPIA case
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Create a shorter label that fits Pega's 64 character limit
            project_title = detected_fields['Project Title']
            if len(project_title) > 40:
                project_title = project_title[:37] + "..."
            short_label = f"DPIA - {project_title}"
            
            case_content = {
                "pyLabel": short_label,
                "pyDescription": f"DPIA Scanning Request - AI Bot Analysis\n\nAnalysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nText Length: {len(research_text)} characters\n\nDetected Fields:\n" +
                               "\n".join([f"- {k}: {v}" for k, v in detected_fields.items()]) +
                               f"\n\nOriginal Research Text:\n{research_text[:500]}{'...' if len(research_text) > 500 else ''}",
                "pxCreatedFromChannel": "MCP-AI-Bot"
            }
            
            case_args = {
                "caseTypeID": "Roche-Pathworks-Work-DPIA",
                "processID": "pyStartCase",
                "content": case_content
            }
            
            try:
                case_result = await create_case(case_args)
                
                return {
                    "success": True,
                    "analysis": analysis_result,
                    "case_created": True,
                    "case_id": case_result.get("ID", "Unknown"),
                    "case_details": case_result,
                    "message": "🎉 Perfect! I've successfully created your DPIA case with all the information gathered through our conversation!",
                    "summary": {
                        "detected_fields": len([f for f in detected_fields.values() if f != "Unknown"]),
                        "total_fields": len(detected_fields),
                        "validation_status": "PASSED",
                        "recommendations_count": len(recommendations)
                    }
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "analysis": analysis_result,
                    "case_created": False,
                    "error": f"Failed to create DPIA case: {str(e)}",
                    "message": "❌ I completed the analysis but encountered an error while creating the case in Pega"
                }
        
        else:
            # Return analysis only
            return {
                "success": True,
                "analysis": analysis_result,
                "case_created": False,
                "message": "🔍 Analysis completed successfully! All fields are ready." if not missing_fields else "🤖 Analysis completed. Please provide the missing information to proceed.",
                "next_steps": [
                    f"Provide {field}" for field in missing_fields
                ] if missing_fields else ["Set auto_create=true to create the DPIA case"],
                "summary": {
                    "detected_fields": len([f for f in detected_fields.values() if f != "Unknown"]),
                    "total_fields": len(detected_fields),
                    "validation_status": "PASSED" if not missing_fields else "PENDING",
                    "recommendations_count": len(recommendations)
                }
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Analysis failed: {str(e)}",
            "message": "❌ DPIA Analysis AI Bot encountered an error during analysis"
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/web")
async def web_interface():
    """Serve the AI Bot web interface"""
    return FileResponse("dpia_chatbot_production.html")

if __name__ == "__main__":
    print("Starting Simple Pega MCP Server...")
    print(f"Pega Base URL: {PEGA_BASE_URL}")
    print(f"Server will be available at: http://localhost:8080")
    
    uvicorn.run(app, host="0.0.0.0", port=8080) 