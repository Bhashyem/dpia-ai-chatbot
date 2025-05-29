#!/usr/bin/env python3
"""
Enhanced DPIA Chatbot Server with Claude LLM Integration
Combines Pega case management with intelligent Claude-powered analysis
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import requests
import os
from dotenv import load_dotenv
import logging
import base64
import json
from datetime import datetime, timedelta
import asyncio
import uuid

# Import our Claude integration
from claude_integration import claude_integration, AnalysisResult

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DPIA Chatbot Server with Claude LLM",
    description="Intelligent DPIA analysis and case creation with Claude AI",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pega Configuration
PEGA_BASE_URL = os.getenv("PEGA_BASE_URL", "https://roche-gtech-dt1.pegacloud.net/prweb/api/v1")
PEGA_USERNAME = os.getenv("PEGA_USERNAME", "nadadhub")
PEGA_PASSWORD = os.getenv("PEGA_PASSWORD", "Pwrm*2025")

# Basic auth header
BASIC_AUTH = base64.b64encode(f"{PEGA_USERNAME}:{PEGA_PASSWORD}".encode()).decode()

# DPIA questionnaire flow - integrated with Claude analysis
dpia_questions = {
    "start": {
        "question": "Welcome to the DPIA Assessment with Claude AI! I can analyze your research text or guide you through our questionnaire. Would you like to start?",
        "options": ["Yes", "No"],
        "next": {"Yes": "input_method", "No": "end"}
    },
    "input_method": {
        "question": "How would you like to provide your information?",
        "options": ["Paste research text for AI analysis", "Answer questionnaire step by step"],
        "next": {"Paste research text for AI analysis": "text_analysis", "Answer questionnaire step by step": "project_name"}
    },
    "text_analysis": {
        "question": "Please paste your research text below and I'll analyze it with Claude AI to extract DPIA information:",
        "type": "text",
        "next": "analyze_text"
    },
    "project_name": {
        "question": "What is the name of your project or initiative?",
        "type": "text",
        "next": "department"
    },
    "department": {
        "question": "Which department is responsible for this initiative?",
        "type": "text",
        "next": "personal_data"
    },
    "personal_data": {
        "question": "Will this project involve any Pathologist inputs?",
        "options": ["Yes", "No"],
        "next": {"Yes": "end_no_dpia", "No": "data_volume"}
    },
    "data_volume": {
        "question": "Will this project involve processing a large sample data?",
        "options": ["Yes", "No"],
        "next": {"Yes": "sensitive_data", "No": "sensitive_data"}
    },
    "sensitive_data": {
        "question": "Will you be processing any sensitive experiments?",
        "options": ["Yes", "No"],
        "next": {"Yes": "automated_decision", "No": "automated_decision"}
    },
    "automated_decision": {
        "question": "Will this project involve automated decision-making that affects individuals?",
        "options": ["Yes", "No"],
        "next": {"Yes": "monitoring", "No": "monitoring"}
    },
    "monitoring": {
        "question": "Will this project involve systematic monitoring of individuals?",
        "options": ["Yes", "No"],
        "next": {"Yes": "cross_border", "No": "cross_border"}
    },
    "cross_border": {
        "question": "Will this project involve transferring data across borders?",
        "options": ["Yes", "No"],
        "next": {"Yes": "collect_answers", "No": "collect_answers"}
    },
    "end_no_dpia": {
        "question": "Based on your response, a DPIA may not be required. Would you like to review your answers?",
        "options": ["Review Answers", "Exit"],
        "next": {"Review Answers": "review", "Exit": "end"}
    },
    "collect_answers": {
        "question": "Based on your responses, a DPIA is recommended. Would you like to create a DPIA case now?",
        "options": ["Yes", "No"],
        "next": {"Yes": "create_case", "No": "review"}
    }
}

# Session storage for questionnaire and Claude analysis
session_data = {}
enhanced_sessions = {}

# Request/Response Models
class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    analysis_result: Optional[AnalysisResult] = None
    suggestions: List[str] = []
    next_action: Optional[str] = None
    missing_fields: Optional[List[str]] = None
    detected_fields: Optional[Dict[str, str]] = None

class AnalysisRequest(BaseModel):
    research_text: str
    enhance_fields: bool = True

class FieldUpdateRequest(BaseModel):
    field_responses: Dict[str, str]
    original_analysis: Dict[str, Any]

class CaseCreationRequest(BaseModel):
    detected_fields: Dict[str, str]
    research_text: str
    user_responses: Optional[Dict[str, str]] = None

class CaseRequest(BaseModel):
    caseTypeID: str
    processID: Optional[str] = None
    content: Dict[str, Any] = Field(default_factory=dict)

class CaseResponse(BaseModel):
    ID: str
    status: str
    nextAssignmentID: Optional[str]
    nextAssignmentName: Optional[str]
    links: Optional[List[Dict[str, str]]]

# Claude-powered endpoints
@app.post("/chat", response_model=ChatResponse)
async def chat_with_claude(chat_request: ChatMessage):
    """Enhanced chat endpoint that integrates Claude analysis with questionnaire workflow"""
    try:
        user_id = chat_request.user_id or str(uuid.uuid4())
        session_id = chat_request.session_id or str(uuid.uuid4())
        message = chat_request.message
        
        logger.info(f"Chat request from user {user_id}: {message[:100]}...")
        
        # Initialize session if needed
        if session_id not in enhanced_sessions:
            enhanced_sessions[session_id] = {
                "user_id": user_id,
                "analysis_results": {},
                "extracted_fields": {},
                "conversation_history": [],
                "current_task": "chat",
                "questionnaire_state": "start",
                "missing_fields": [],
                "created_at": datetime.now().isoformat()
            }
        
        session = enhanced_sessions[session_id]
        
        # Check if this looks like research text for analysis
        research_keywords = [
            "cells", "stain", "analysis", "research", "study", "groups", "pathologist", "therapeutic", "assay",
            "imaging", "microscopy", "time-lapse", "molecule", "distribution", "mammalian", "fluorescence",
            "confocal", "leica", "sp8", "quantification", "monitoring", "protocol", "experiment", "specimen",
            "biospecimen", "tissue", "biopsy", "slide", "section", "antibody", "protein", "gene", "dna", "rna"
        ]
        
        # More flexible detection: shorter text OR contains research keywords
        is_research_text = (
            (len(message) > 50 and any(keyword in message.lower() for keyword in research_keywords)) or
            (len(message) > 100 and any(keyword in message.lower() for keyword in ["cells", "stain", "analysis", "research", "study"]))
        )
        
        if is_research_text:
            # This looks like research text - analyze it with Claude
            logger.info("Research text detected, performing Claude analysis")
            analysis_result = await claude_integration.analyze_research_text(message)
            
            # Update session with analysis results
            session["analysis_results"] = {
                "detected_fields": analysis_result.detected_fields,
                "missing_fields": analysis_result.missing_fields,
                "confidence_scores": analysis_result.confidence_scores,
                "analysis_summary": analysis_result.analysis_summary
            }
            session["extracted_fields"].update(analysis_result.detected_fields)
            session["missing_fields"] = analysis_result.missing_fields
            session["current_task"] = "dpia_analysis"
            
            # Generate response based on analysis
            if analysis_result.missing_fields:
                missing_fields_text = ", ".join(analysis_result.missing_fields)
                response_text = f"""🤖 **Claude AI Analysis Complete!**

I've analyzed your research text and extracted the following information:

**✅ Detected Fields:**
{_format_extracted_fields(analysis_result.detected_fields)}

**❓ Missing Information:**
To complete your DPIA assessment, I still need:
• {missing_fields_text.replace(', ', chr(10) + '• ')}

Please provide the missing information, and I'll create your DPIA case automatically!"""
                
                return ChatResponse(
                    response=response_text,
                    analysis_result=analysis_result,
                    suggestions=[f"Please provide: {field}" for field in analysis_result.missing_fields],
                    next_action="provide_missing_fields",
                    missing_fields=analysis_result.missing_fields,
                    detected_fields=analysis_result.detected_fields
                )
            else:
                response_text = f"""🎉 **Perfect! Claude AI Analysis Complete!**

I've successfully analyzed your research text and extracted all required fields:

{_format_extracted_fields(analysis_result.detected_fields)}

✅ All mandatory fields detected! Would you like me to create a DPIA case now?"""
                
                return ChatResponse(
                    response=response_text,
                    analysis_result=analysis_result,
                    suggestions=["Create DPIA case", "Review information", "Make changes"],
                    next_action="create_case",
                    missing_fields=[],
                    detected_fields=analysis_result.detected_fields
                )
        
        # Handle missing field responses
        elif session.get("missing_fields") and session.get("current_task") == "dpia_analysis":
            # Try to extract missing field information from the response
            updated_fields = {}
            for field in session["missing_fields"]:
                # Simple field extraction based on context
                if field.lower() in message.lower():
                    # Extract the value after the field name
                    field_pattern = rf"{field.lower()}[:\-\s]*([^\n\r,;.]*)"
                    import re
                    match = re.search(field_pattern, message.lower())
                    if match and match.group(1).strip():
                        updated_fields[field] = match.group(1).strip().title()
                elif len(session["missing_fields"]) == 1:
                    # If only one field is missing, assume the entire message is the answer
                    updated_fields[field] = message.strip()
            
            # Update session with new field values
            session["extracted_fields"].update(updated_fields)
            remaining_missing = [f for f in session["missing_fields"] if f not in updated_fields]
            session["missing_fields"] = remaining_missing
            
            if remaining_missing:
                response_text = f"""✅ **Updated!** Thank you for providing: {', '.join(updated_fields.keys())}

**Still needed:**
• {chr(10).join(['• ' + field for field in remaining_missing])}

Please provide the remaining information."""
                
                return ChatResponse(
                    response=response_text,
                    suggestions=[f"Please provide: {field}" for field in remaining_missing],
                    next_action="provide_missing_fields",
                    missing_fields=remaining_missing,
                    detected_fields=session["extracted_fields"]
                )
            else:
                response_text = f"""🎉 **All fields complete!**

**Final Information:**
{_format_extracted_fields(session["extracted_fields"])}

Ready to create your DPIA case! Shall I proceed?"""
                
                return ChatResponse(
                    response=response_text,
                    suggestions=["Yes, create DPIA case", "Let me review first"],
                    next_action="create_case",
                    missing_fields=[],
                    detected_fields=session["extracted_fields"]
                )
        
        # Handle case creation confirmation
        elif ("yes" in message.lower() or "create" in message.lower()) and session.get("current_task") == "dpia_analysis" and not session.get("missing_fields"):
            # Create the DPIA case
            try:
                case_request = CaseCreationRequest(
                    detected_fields=session["extracted_fields"],
                    research_text=session.get("original_text", "")
                )
                case_response = await create_dpia_case_with_claude(case_request)
                
                response_text = f"""🎉 **DPIA Case Created Successfully!**

**Case ID:** {case_response.ID}
**Status:** {case_response.status}

Your DPIA assessment has been submitted and is now in the system for review. You'll receive updates on the case progress.

Is there anything else I can help you with?"""
                
                # Reset session for new conversation
                session["current_task"] = "chat"
                session["missing_fields"] = []
                
                return ChatResponse(
                    response=response_text,
                    suggestions=["Start new analysis", "Check case status", "Exit"],
                    next_action="completed"
                )
                
            except Exception as e:
                logger.error(f"Error creating case: {e}")
                response_text = f"❌ **Error creating DPIA case:** {str(e)}\n\nWould you like to try again or review the information?"
                
                return ChatResponse(
                    response=response_text,
                    suggestions=["Try again", "Review information", "Start over"],
                    next_action="retry_case_creation"
                )
        
        else:
            # Regular conversational response using Claude
            context = {
                "analysis_results": session.get("analysis_results", {}),
                "missing_fields": session.get("missing_fields", []),
                "current_task": session.get("current_task", "chat"),
                "extracted_fields": session.get("extracted_fields", {})
            }
            
            response_text = await claude_integration.generate_conversational_response(
                message, context
            )
            
            # Update conversation history
            session["conversation_history"].append({
                "user": message,
                "assistant": response_text,
                "timestamp": datetime.now().isoformat()
            })
            
            return ChatResponse(
                response=response_text,
                suggestions=["Paste research text for analysis", "Ask a question", "Start questionnaire"],
                next_action="await_input"
            )
            
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

# Original questionnaire endpoint - enhanced with Claude integration
@app.post("/question")
async def get_question(
    current_state: str = Form(...),
    answer: Optional[str] = Form(None),
    user_id: str = Form(...)
):
    """Enhanced questionnaire endpoint that integrates with Claude analysis"""
    try:
        logger.info(f"Questionnaire request - State: {current_state}, Answer: {answer}, User ID: {user_id}")
        
        if current_state not in dpia_questions:
            logger.error(f"Invalid state received: {current_state}")
            raise HTTPException(status_code=400, detail="Invalid state")

        # Store the answer if provided (but not for initial state)
        if answer is not None and current_state != "start":
            if user_id not in session_data:
                session_data[user_id] = {}
            session_data[user_id][current_state] = answer
            logger.info(f"Stored answer for user {user_id}: {current_state} = {answer}")

        current_question = dpia_questions[current_state]
        
        # Handle text analysis state
        if current_state == "text_analysis" and answer:
            logger.info("Performing Claude analysis on provided text")
            try:
                # Analyze the text with Claude
                analysis_result = await claude_integration.analyze_research_text(answer)
                
                # Store analysis results in session
                if user_id not in session_data:
                    session_data[user_id] = {}
                
                session_data[user_id]["claude_analysis"] = {
                    "detected_fields": analysis_result.detected_fields,
                    "missing_fields": analysis_result.missing_fields,
                    "confidence_scores": analysis_result.confidence_scores,
                    "original_text": answer
                }
                
                # If we have missing fields, ask for them
                if analysis_result.missing_fields:
                    missing_fields_text = ", ".join(analysis_result.missing_fields)
                    return {
                        "question": f"""Claude AI has analyzed your text and found:

**Detected Information:**
{_format_extracted_fields(analysis_result.detected_fields)}

**Missing Information:**
{missing_fields_text}

Please provide the missing information to complete your DPIA assessment.""",
                        "type": "text",
                        "state": "collect_missing_fields",
                        "analysis_result": analysis_result.dict(),
                        "missing_fields": analysis_result.missing_fields
                    }
                else:
                    # All fields detected, proceed to case creation
                    return {
                        "question": f"""Perfect! Claude AI has extracted all required information:

{_format_extracted_fields(analysis_result.detected_fields)}

Based on this analysis, a DPIA is recommended. Would you like to create a DPIA case now?""",
                        "options": ["Yes", "No"],
                        "state": "collect_answers",
                        "analysis_result": analysis_result.dict()
                    }
                    
            except Exception as e:
                logger.error(f"Error in Claude analysis: {e}")
                return {
                    "question": f"I encountered an error analyzing your text: {str(e)}. Would you like to try the step-by-step questionnaire instead?",
                    "options": ["Yes, use questionnaire", "Try analysis again"],
                    "state": "error_fallback"
                }
        
        # Handle missing fields collection
        if current_state == "collect_missing_fields" and answer:
            claude_analysis = session_data[user_id].get("claude_analysis", {})
            missing_fields = claude_analysis.get("missing_fields", [])
            
            # Try to extract field values from the answer
            updated_fields = claude_analysis.get("detected_fields", {}).copy()
            
            # Simple field extraction (can be enhanced)
            for field in missing_fields:
                if field.lower() in answer.lower():
                    # Extract value after field name
                    import re
                    pattern = rf"{field.lower()}[:\-\s]*([^\n\r,;.]*)"
                    match = re.search(pattern, answer.lower())
                    if match and match.group(1).strip():
                        updated_fields[field] = match.group(1).strip().title()
                elif len(missing_fields) == 1:
                    # If only one field missing, assume entire answer is the value
                    updated_fields[field] = answer.strip()
            
            # Update session with new fields
            session_data[user_id]["claude_analysis"]["detected_fields"] = updated_fields
            
            # Check if all fields are now complete
            remaining_missing = [f for f in missing_fields if updated_fields.get(f) == "Unknown" or not updated_fields.get(f)]
            
            if remaining_missing:
                return {
                    "question": f"Thank you! I still need: {', '.join(remaining_missing)}. Please provide this information.",
                    "type": "text",
                    "state": "collect_missing_fields",
                    "missing_fields": remaining_missing
                }
            else:
                return {
                    "question": f"""Excellent! All information is now complete:

{_format_extracted_fields(updated_fields)}

Based on this analysis, a DPIA is recommended. Would you like to create a DPIA case now?""",
                    "options": ["Yes", "No"],
                    "state": "collect_answers"
                }
        
        # For initial state or when no answer is provided
        if current_state == "start" and answer is None:
            logger.info("Returning initial question")
            return {
                "question": dpia_questions["start"]["question"],
                "options": dpia_questions["start"]["options"],
                "type": dpia_questions["start"].get("type", "options"),
                "state": "start"
            }
        
        # Handle next state based on the answer
        next_state = None
        if "options" in current_question:
            next_state = current_question["next"].get(answer) if answer else None
        else:
            next_state = current_question["next"]

        # If we're at collect_answers and user wants to create case
        if current_state == "collect_answers" and answer == "Yes":
            logger.info(f"Creating case for user {user_id}")
            
            if user_id not in session_data:
                raise HTTPException(status_code=400, detail="No responses found for user")
            
            # Check if we have Claude analysis results
            claude_analysis = session_data[user_id].get("claude_analysis")
            if claude_analysis:
                # Use Claude-enhanced case creation
                case_data = prepare_enhanced_case_data(
                    claude_analysis["detected_fields"], 
                    session_data[user_id]
                )
            else:
                # Use traditional questionnaire data
                case_data = prepare_case_data(session_data[user_id])
            
            logger.info(f"Prepared case data: {json.dumps(case_data)}")
            
            # Create case in Pega
            try:
                case_result = await create_pega_case(case_data)
                logger.info(f"Case creation result: {json.dumps(case_result)}")
                
                if case_result.get("success"):
                    response_data = {
                        "completed": True,
                        "success": True,
                        "case_id": case_result.get("case_id"),
                        "status": case_result.get("status"),
                        "message": case_result.get("message"),
                        "next_steps": case_result.get("next_steps", "Your DPIA assessment has been submitted successfully."),
                        "claude_enhanced": bool(claude_analysis)
                    }
                    logger.info(f"Returning success response: {json.dumps(response_data)}")
                    return response_data
                else:
                    error_response = {
                        "completed": True,
                        "success": False,
                        "message": case_result.get("error", "Unknown error"),
                        "error": True
                    }
                    logger.error(f"Returning error response: {json.dumps(error_response)}")
                    return error_response
            except Exception as e:
                logger.error(f"Error creating case: {str(e)}")
                return {
                    "completed": True,
                    "success": False,
                    "message": f"Failed to create case: {str(e)}",
                    "error": True
                }

        # Continue with questionnaire flow
        if next_state and next_state in dpia_questions:
            next_question = dpia_questions[next_state]
            return {
                "question": next_question["question"],
                "options": next_question.get("options", []),
                "type": next_question.get("type", "options"),
                "state": next_state
            }
        else:
            return {
                "completed": True,
                "message": "Thank you for completing the DPIA questionnaire."
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_question: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Helper functions
def _format_extracted_fields(fields: Dict[str, Any]) -> str:
    """Format extracted fields for display"""
    formatted = []
    field_labels = {
        "PI": "Principal Investigator",
        "Pathologist": "Pathologist", 
        "Therapeutic Area": "Therapeutic Area",
        "Procedure": "Procedure",
        "Assay Type/Staining Type": "Assay/Staining Type",
        "Project Title": "Project Title",
        "Request Purpose": "Request Purpose"
    }
    
    for field, value in fields.items():
        if value and value != "Unknown":
            label = field_labels.get(field, field.replace("_", " ").title())
            formatted.append(f"• **{label}:** {value}")
    
    return "\n".join(formatted) if formatted else "No fields detected"

def prepare_enhanced_case_data(extracted_fields: Dict[str, Any], session_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare enhanced case data with Claude-extracted fields"""
    
    # Calculate risk level based on extracted fields
    risk_level = calculate_enhanced_risk_level(extracted_fields)
    
    # Generate enhanced description
    description = generate_enhanced_description(extracted_fields, session_data)
    
    case_data = {
        "caseTypeID": "Roche-Pathworks-Work-DPIA",
        "processID": "pyStartCase",
        "content": {}
    }
    
    return case_data

def calculate_enhanced_risk_level(extracted_fields: Dict[str, Any]) -> str:
    """Calculate risk level based on Claude-extracted fields"""
    risk_score = 0
    
    # High-risk therapeutic areas
    high_risk_areas = ["Oncology", "Neurology", "Rare Disease"]
    therapeutic_area = extracted_fields.get("Therapeutic Area", "")
    if any(area in therapeutic_area for area in high_risk_areas):
        risk_score += 3
    
    # Medium-risk areas
    medium_risk_areas = ["CVRM", "Immunology"]
    if any(area in therapeutic_area for area in medium_risk_areas):
        risk_score += 2
    
    # Risk based on procedure complexity
    procedure = extracted_fields.get("Procedure", "")
    if "BF+IF" in procedure or "complex" in procedure.lower():
        risk_score += 2
    elif "IF" in procedure:
        risk_score += 1
    
    # Risk based on assay type
    assay_type = extracted_fields.get("Assay Type/Staining Type", "")
    if "IHC" in assay_type or "Special" in assay_type:
        risk_score += 1
    
    if risk_score >= 4:
        return "High"
    elif risk_score >= 2:
        return "Medium"
    else:
        return "Low"

def generate_enhanced_description(extracted_fields: Dict[str, Any], session_data: Dict[str, Any]) -> str:
    """Generate enhanced description with Claude-extracted information"""
    
    description_parts = [
        f"DPIA case created via Claude AI analysis for: {extracted_fields.get('Project Title', 'Research Project')}",
        f"Principal Investigator: {extracted_fields.get('PI', 'Not specified')}",
        f"Pathologist: {extracted_fields.get('Pathologist', 'Not specified')}",
        f"Therapeutic Area: {extracted_fields.get('Therapeutic Area', 'Not specified')}",
        f"Procedure: {extracted_fields.get('Procedure', 'Not specified')}",
        f"Assay Type: {extracted_fields.get('Assay Type/Staining Type', 'Not specified')}",
        f"Purpose: {extracted_fields.get('Request Purpose', 'Not specified')}"
    ]
    
    # Add confidence information if available
    confidence_scores = session_data.get("claude_analysis", {}).get("confidence_scores", {})
    if confidence_scores:
        avg_confidence = sum(confidence_scores.values()) / len(confidence_scores)
        description_parts.append(f"AI Analysis Confidence: {avg_confidence:.2f}")
    
    return " | ".join(description_parts)

def prepare_case_data(responses: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare case data from traditional questionnaire responses"""
    
    # Calculate risk level based on responses
    risk_level = calculate_risk_level(responses)
    
    # Generate description
    description = generate_description(responses)
    
    case_data = {
        "caseTypeID": "Roche-Pathworks-Work-DPIA",
        "processID": "pyStartCase",
        "content": {}
    }
    
    return case_data

def calculate_risk_level(responses: Dict[str, Any]) -> str:
    """Calculate risk level based on questionnaire responses"""
    risk_score = 0
    
    # Add risk points based on responses
    if responses.get("personal_data") == "Yes":
        risk_score += 2
    if responses.get("data_volume") == "Yes":
        risk_score += 1
    if responses.get("sensitive_data") == "Yes":
        risk_score += 3
    if responses.get("automated_decision") == "Yes":
        risk_score += 2
    if responses.get("monitoring") == "Yes":
        risk_score += 2
    if responses.get("cross_border") == "Yes":
        risk_score += 1
    
    if risk_score >= 6:
        return "High"
    elif risk_score >= 3:
        return "Medium"
    else:
        return "Low"

def determine_dpia_requirement(responses: Dict[str, Any]) -> bool:
    """Determine if DPIA is required based on responses"""
    # DPIA is required if any high-risk factors are present
    high_risk_factors = [
        responses.get("sensitive_data") == "Yes",
        responses.get("automated_decision") == "Yes",
        responses.get("monitoring") == "Yes"
    ]
    
    return any(high_risk_factors)

def generate_justification(responses: Dict[str, Any]) -> str:
    """Generate justification for DPIA requirement"""
    justifications = []
    
    if responses.get("sensitive_data") == "Yes":
        justifications.append("Processing of sensitive data")
    if responses.get("automated_decision") == "Yes":
        justifications.append("Automated decision-making")
    if responses.get("monitoring") == "Yes":
        justifications.append("Systematic monitoring")
    if responses.get("cross_border") == "Yes":
        justifications.append("Cross-border data transfer")
    
    if justifications:
        return "DPIA required due to: " + ", ".join(justifications)
    else:
        return "DPIA may not be required based on current responses"

def generate_description(responses: Dict[str, Any]) -> str:
    """Generate description from questionnaire responses"""
    
    description_parts = [
        f"DPIA assessment for project: {responses.get('project_name', 'Unnamed Project')}",
        f"Department: {responses.get('department', 'Not specified')}",
        f"Personal data involved: {responses.get('personal_data', 'Not specified')}",
        f"Large data volume: {responses.get('data_volume', 'Not specified')}",
        f"Sensitive data: {responses.get('sensitive_data', 'Not specified')}",
        f"Automated decisions: {responses.get('automated_decision', 'Not specified')}",
        f"Monitoring: {responses.get('monitoring', 'Not specified')}",
        f"Cross-border transfer: {responses.get('cross_border', 'Not specified')}"
    ]
    
    return " | ".join(description_parts)

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_research_text(analysis_request: AnalysisRequest):
    """Analyze research text using Claude LLM"""
    try:
        logger.info(f"Analyzing research text: {len(analysis_request.research_text)} characters")
        
        analysis_result = await claude_integration.analyze_research_text(analysis_request.research_text)
        
        # Optionally enhance field detection
        if analysis_request.enhance_fields:
            enhanced_fields = {}
            for field, value in analysis_result.detected_fields.items():
                if value == "Unknown" or analysis_result.confidence_scores.get(field, 0) < 0.5:
                    enhanced_value, confidence = await claude_integration.enhance_field_detection(
                        field, analysis_request.research_text, value
                    )
                    enhanced_fields[field] = enhanced_value
                    analysis_result.confidence_scores[field] = confidence
            
            # Update with enhanced fields
            analysis_result.detected_fields.update(enhanced_fields)
            
            # Recalculate missing fields
            analysis_result.missing_fields = [
                field for field, value in analysis_result.detected_fields.items() 
                if value == "Unknown"
            ]
        
        logger.info(f"Analysis complete. Found {len(analysis_result.detected_fields) - len(analysis_result.missing_fields)} fields")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error in analysis endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/update-fields")
async def update_fields_with_responses(update_request: FieldUpdateRequest):
    """Update analysis with user-provided field responses"""
    try:
        logger.info(f"Updating fields with user responses: {list(update_request.field_responses.keys())}")
        
        # Merge user responses with original analysis
        updated_fields = update_request.original_analysis.get("detected_fields", {}).copy()
        updated_fields.update(update_request.field_responses)
        
        # Generate a conversational response about the updates
        response_text = await claude_integration.generate_conversational_response(
            f"Thank you for providing the additional information! I've updated the following fields: {', '.join(update_request.field_responses.keys())}",
            {"updated_fields": updated_fields}
        )
        
        return {
            "status": "success",
            "updated_fields": updated_fields,
            "response": response_text,
            "ready_for_case_creation": len([v for v in updated_fields.values() if v != "Unknown"]) >= 7
        }
        
    except Exception as e:
        logger.error(f"Error updating fields: {e}")
        raise HTTPException(status_code=500, detail=f"Field update failed: {str(e)}")

@app.post("/create-case", response_model=CaseResponse)
async def create_dpia_case_with_claude(case_request: CaseCreationRequest):
    """Create a DPIA case in Pega with Claude-enhanced data"""
    try:
        logger.info("Creating DPIA case with Claude-enhanced data")
        
        # Merge detected fields with user responses
        final_fields = case_request.detected_fields.copy()
        if case_request.user_responses:
            final_fields.update(case_request.user_responses)
        
        # Generate a better project title if needed
        if final_fields.get("Project Title") == "Unknown" or not final_fields.get("Project Title"):
            final_fields["Project Title"] = await claude_integration.generate_project_title(case_request.research_text)
        
        # Validate mandatory fields
        mandatory_fields = ["PI", "Pathologist", "Therapeutic Area", "Procedure", "Assay Type/Staining Type", "Project Title", "Request Purpose"]
        missing_fields = [field for field in mandatory_fields if final_fields.get(field) == "Unknown" or not final_fields.get(field)]
        
        if missing_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing mandatory fields: {', '.join(missing_fields)}"
            )
        
        # Create Pega case
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        case_id = f"DPIA-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Prepare Pega case content
        case_content = {}
        
        # Call Pega API
        pega_request = CaseRequest(
            caseTypeID="Roche-Pathworks-Work-DPIA",
            processID="pyStartCase",
            content=case_content
        )
        
        case_response = await create_pega_case(pega_request)
        
        # Generate success message with Claude
        success_message = await claude_integration.generate_conversational_response(
            f"Successfully created DPIA case {case_response.ID} with all the analyzed information!",
            {"case_created": True, "case_id": case_response.ID}
        )
        
        logger.info(f"DPIA case created successfully: {case_response.ID}")
        return case_response
        
    except Exception as e:
        logger.error(f"Error creating DPIA case: {e}")
        raise HTTPException(status_code=500, detail=f"Case creation failed: {str(e)}")

# Enhanced tools endpoint for MCP compatibility
@app.post("/tools/call")
async def call_tool(tool_request: Dict[str, Any]):
    """Enhanced tools endpoint with Claude integration"""
    try:
        tool_name = tool_request.get("name")
        arguments = tool_request.get("arguments", {})
        
        logger.info(f"Tool called: {tool_name}")
        
        if tool_name == "analyze_and_create_dpia":
            research_text = arguments.get("research_text", "")
            action = arguments.get("action", "analyze_only")
            auto_create = arguments.get("auto_create", False)
            
            # Analyze with Claude
            analysis_result = await claude_integration.analyze_research_text(research_text)
            
            result = {
                "analysis": {
                    "detected_fields": analysis_result.detected_fields,
                    "missing_fields": analysis_result.missing_fields,
                    "confidence_scores": analysis_result.confidence_scores,
                    "interactive_prompts": analysis_result.interactive_prompts,
                    "suggestions": analysis_result.suggestions,
                    "analysis_summary": analysis_result.analysis_summary
                }
            }
            
            # Auto-create case if requested and all fields are available
            if auto_create and not analysis_result.missing_fields:
                try:
                    case_request = CaseCreationRequest(
                        detected_fields=analysis_result.detected_fields,
                        research_text=research_text
                    )
                    case_response = await create_dpia_case_with_claude(case_request)
                    result["case_created"] = True
                    result["case_id"] = case_response.ID
                    result["case_status"] = case_response.status
                except Exception as e:
                    logger.error(f"Auto case creation failed: {e}")
                    result["case_created"] = False
                    result["case_error"] = str(e)
            
            return {"content": [{"text": json.dumps(result)}]}
            
        elif tool_name == "chat_with_claude":
            message = arguments.get("message", "")
            context = arguments.get("context", {})
            
            chat_request = ChatMessage(message=message, context=context)
            chat_response = await chat_with_claude(chat_request)
            
            return {"content": [{"text": chat_response.response}]}
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
            
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

# Original Pega endpoints (enhanced)
async def create_pega_case(case_request) -> CaseResponse:
    """Create a case in Pega system - handles both CaseRequest objects and dictionaries"""
    try:
        # Handle both CaseRequest objects and dictionaries
        if isinstance(case_request, dict):
            # Convert dictionary to expected format
            case_type_id = case_request.get("caseTypeID", "ROCHE-GTECH-WORK-DPIA")
            process_id = case_request.get("processID", "pyStartCase")
            content = case_request.get("content", {})
        else:
            # CaseRequest object
            case_type_id = case_request.caseTypeID
            process_id = case_request.processID or "pyStartCase"
            content = case_request.content
        
        logger.info("Attempting to create case with type: %s", case_type_id)
        
        # Set headers with basic auth
        headers = {
            "Authorization": f"Basic {BASIC_AUTH}",
            "Content-Type": "application/json"
        }
        
        # Prepare request payload
        payload = {
            "caseTypeID": case_type_id,
            "processID": process_id,
            "content": content
        }
        
        logger.info("Sending request to Pega API: %s", PEGA_BASE_URL)
        response = requests.post(
            f"{PEGA_BASE_URL}/cases",
            json=payload,
            headers=headers,
            verify=True,
            timeout=30
        )
        
        logger.info("Pega API response status: %d", response.status_code)
        
        if response.status_code in [201, 200]:
            result = response.json()
            logger.info("Case created successfully: %s", result)
            return CaseResponse(
                ID=result.get("ID", ""),
                status="Created",
                nextAssignmentID=result.get("nextPageID", ""),
                nextAssignmentName="Review Case",
                links=[{"rel": "self", "href": f"{PEGA_BASE_URL}/cases/{result.get('ID', '')}"}]
            )
        else:
            error_msg = f"Failed to create case. Status code: {response.status_code}"
            try:
                error_data = response.json()
                if "errors" in error_data:
                    error_details = error_data["errors"][0].get("message", "")
                    validation_messages = error_data["errors"][0].get("ValidationMessages", [])
                    if validation_messages:
                        error_details += " - " + validation_messages[0].get("ValidationMessage", "")
                    error_msg = error_details
            except:
                error_msg = response.text
            logger.error(error_msg)
            
            # Return demo mode response if Pega is unavailable
            demo_case_id = f"DEMO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            logger.info(f"Returning demo case: {demo_case_id}")
            return CaseResponse(
                ID=demo_case_id,
                status="Demo Mode",
                nextAssignmentID="demo_assignment",
                nextAssignmentName="Demo Review",
                links=[{"rel": "demo", "href": f"demo/cases/{demo_case_id}"}]
            )
            
    except requests.exceptions.RequestException as e:
        logger.error("Network error: %s", str(e), exc_info=True)
        # Return demo mode response
        demo_case_id = f"DEMO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Network error - returning demo case: {demo_case_id}")
        return CaseResponse(
            ID=demo_case_id,
            status="Demo Mode (Network Error)",
            nextAssignmentID="demo_assignment",
            nextAssignmentName="Demo Review",
            links=[{"rel": "demo", "href": f"demo/cases/{demo_case_id}"}]
        )
    except Exception as e:
        logger.error("Unexpected error: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/cases", response_model=CaseResponse)
async def create_case(case_request: CaseRequest):
    """Legacy endpoint for direct Pega case creation"""
    return await create_pega_case(case_request)

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint"""
    try:
        # Check Claude integration
        claude_status = "healthy"
        try:
            # Quick test of Claude integration
            await claude_integration.generate_conversational_response("Health check", {})
        except Exception as e:
            claude_status = f"error: {str(e)}"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "claude_integration": claude_status,
            "version": "2.0.0"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/cases/{case_id}")
async def get_case(case_id: str):
    """Get a specific case from Pega"""
    try:
        headers = {
            "Authorization": f"Basic {BASIC_AUTH}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{PEGA_BASE_URL}/cases/{case_id}",
            headers=headers,
            verify=True,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving case: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving case: {str(e)}")

@app.get("/cases")
async def list_cases(
    status: Optional[str] = None,
    caseTypeID: Optional[str] = None,
    page: int = 1,
    per_page: int = 25
):
    """List cases from Pega"""
    try:
        headers = {
            "Authorization": f"Basic {BASIC_AUTH}",
            "Content-Type": "application/json"
        }
        
        params = {
            "page": page,
            "per_page": per_page
        }
        if status:
            params["status"] = status
        if caseTypeID:
            params["caseTypeID"] = caseTypeID
            
        response = requests.get(
            f"{PEGA_BASE_URL}/cases",
            headers=headers,
            params=params,
            verify=True,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error listing cases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing cases: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def serve_chatbot_interface():
    """Serve the Claude-enhanced DPIA chatbot HTML interface"""
    try:
        with open("dpia_chatbot_claude.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        # Fallback to basic HTML if the file doesn't exist
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DPIA Chatbot with Claude LLM</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .status { padding: 20px; background: #f0f8ff; border-radius: 8px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 DPIA Chatbot with Claude LLM</h1>
                <div class="status">
                    <h2>✅ Server is Running!</h2>
                    <p>Your Claude-enhanced DPIA chatbot server is operational.</p>
                    <h3>Available Endpoints:</h3>
                    <ul>
                        <li><strong>Chat API:</strong> <code>POST /chat</code></li>
                        <li><strong>Analysis API:</strong> <code>POST /analyze</code></li>
                        <li><strong>Health Check:</strong> <code>GET /health</code></li>
                        <li><strong>API Documentation:</strong> <a href="/docs">/docs</a></li>
                    </ul>
                    <p><em>Note: The full HTML interface (dpia_chatbot_claude.html) was not found. Please ensure the file exists in the server directory.</em></p>
                </div>
            </div>
        </body>
        </html>
        """)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 