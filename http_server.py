from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import uuid

app = FastAPI()

class CaseRequest(BaseModel):
    caseTypeID: str
    processID: str
    content: Dict[str, Any]

@app.post("/cases")
async def create_case(case: CaseRequest):
    # Generate a fake case ID
    case_id = str(uuid.uuid4())
    # Return the case_id in the response
    return {
        "status": "success",
        "case_id": case_id,
        "case_details": case.content
    } 