from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import requests
import os
from dotenv import load_dotenv
import logging
import base64
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pega Model Context Protocol Server")

# Pega Configuration
PEGA_BASE_URL = os.getenv("PEGA_BASE_URL", "https://roche-gtech-dt1.pegacloud.net/prweb/api/v1")
PEGA_USERNAME = os.getenv("PEGA_USERNAME", "nadadhub")
PEGA_PASSWORD = os.getenv("PEGA_PASSWORD", "Pwrm*2025")

# Basic auth header
BASIC_AUTH = base64.b64encode(f"{PEGA_USERNAME}:{PEGA_PASSWORD}".encode()).decode()

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

@app.post("/cases", response_model=CaseResponse)
async def create_case(case_request: CaseRequest):
    try:
        logger.info("Attempting to create case with type: %s", case_request.caseTypeID)
        
        # Set headers with basic auth
        headers = {
            "Authorization": f"Basic {BASIC_AUTH}",
            "Content-Type": "application/json"
        }
        
        # Transform the content to match Pega's expected schema
        transformed_content = {
            "pxObjClass": case_request.content.get("pxObjClass", "Roche-Pathworks-Work-DPIA"),
            "pyLabel": case_request.content.get("pyLabel"),
            "pyDescription": case_request.content.get("pyDescription"),
            "pyWorkPage": case_request.content.get("pyWorkPage", {}),
            "pxCreatedFromChannel": case_request.content.get("pxCreatedFromChannel", "Web")
        }
        
        # Prepare request payload
        payload = {
            "caseTypeID": "Roche-Pathworks-Work-DPIA",
            "processID": case_request.processID or "pyStartCase",
            "content": transformed_content
        }
        
        logger.info("Sending request to Pega API: %s", PEGA_BASE_URL)
        response = requests.post(
            f"{PEGA_BASE_URL}/cases",
            json=payload,
            headers=headers,
            verify=True
        )
        
        logger.info("Pega API response status: %d", response.status_code)
        logger.info("Pega API response body: %s", response.text)
        
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
            raise HTTPException(status_code=response.status_code, detail=error_msg)
            
    except requests.exceptions.RequestException as e:
        logger.error("Network error: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except Exception as e:
        logger.error("Unexpected error: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/cases/{case_id}")
async def get_case(case_id: str):
    try:
        headers = {
            "Authorization": f"Basic {BASIC_AUTH}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{PEGA_BASE_URL}/cases/{case_id}",
            headers=headers,
            verify=True
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
            verify=True
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error listing cases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing cases: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 