#!/usr/bin/env python3
"""
Galileo AI Platform Integration for DPIA Chatbot
Replaces Claude with Galileo AI's LLM for enhanced analysis and monitoring
"""

import os
import json
import httpx
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class GalileoConfig(BaseModel):
    """Configuration for Galileo AI integration"""
    api_key: str
    project_id: str
    base_url: str = "https://api.galileo.ai/v1"
    environment: str = "production"
    enable_monitoring: bool = True
    model_name: str = "galileo-llm-v1"  # Galileo's LLM model
    temperature: float = 0.1
    max_tokens: int = 4000

class DPIAAnalysisRequest(BaseModel):
    """Request model for DPIA analysis using Galileo AI LLM"""
    text: str
    analysis_type: str = "dpia_analysis"
    metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    enhance_fields: bool = True

class DPIAAnalysisResult(BaseModel):
    """Result model for DPIA analysis from Galileo AI LLM"""
    
    # Core DPIA fields
    therapeutic_area: str
    procedure_type: str
    assay_type: str
    pi_name: Optional[str] = "Unknown"  # Make optional with default
    pathologist: Optional[str] = "Unknown"  # Make optional with default
    project_title: str
    request_purpose: str
    biospecimen_type: str
    data_volume: str
    sensitive_data: str
    cross_border_transfer: str
    
    # Analysis metadata
    missing_fields: List[str]
    confidence_scores: Dict[str, float]
    interactive_prompts: List[str]
    suggestions: List[str]
    analysis_summary: str
    
    # Case type recommendation fields
    recommended_case_type: Optional[str] = "Unknown"  # "CALM" or "DPIA"
    case_type_confidence: Optional[float] = 0.0  # 0.0-1.0
    case_type_reasoning: Optional[str] = ""  # Explanation for the recommendation

class GalileoLLMIntegration:
    """Main integration class for Galileo AI LLM platform"""
    
    def __init__(self, config: GalileoConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
                "X-Galileo-Project": config.project_id
            },
            timeout=60.0
        )
        logger.info(f"Galileo AI LLM integration initialized for project: {config.project_id}")
    
    async def analyze_dpia_text(self, request: DPIAAnalysisRequest) -> DPIAAnalysisResult:
        """
        Analyze DPIA text using Galileo AI's LLM instead of Claude
        """
        try:
            # Enhanced DPIA analysis prompt for Galileo AI LLM
            analysis_prompt = self._create_analysis_prompt(request.text)
            
            payload = {
                "model": self.config.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a specialized DPIA (Data Privacy Impact Assessment) analysis assistant for pharmaceutical research. Analyze research text and extract relevant DPIA fields with high accuracy."
                    },
                    {
                        "role": "user", 
                        "content": analysis_prompt
                    }
                ],
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "metadata": {
                    **(request.metadata or {}),
                    "timestamp": datetime.now().isoformat(),
                    "source": "dpia_chatbot",
                    "environment": self.config.environment,
                    "analysis_type": request.analysis_type
                },
                "user_id": request.user_id,
                "session_id": request.session_id
            }
            
            # Call Galileo AI LLM
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            result = response.json()
            llm_response = result["choices"][0]["message"]["content"]
            
            # Parse the structured response
            parsed_analysis = self._parse_llm_response(llm_response)
            
            # Get additional Galileo insights
            insights = await self._get_analysis_insights(request.text, parsed_analysis)
            
            return DPIAAnalysisResult(
                therapeutic_area=parsed_analysis.get("therapeutic_area", "Unknown"),
                procedure_type=parsed_analysis.get("procedure_type", "Unknown"),
                assay_type=parsed_analysis.get("assay_type", "Unknown"),
                pi_name=parsed_analysis.get("pi_name", "Unknown"),
                pathologist=parsed_analysis.get("pathologist", "Unknown"),
                project_title=parsed_analysis.get("project_title", "Research Analysis"),
                request_purpose=parsed_analysis.get("request_purpose", "Data Analysis"),
                biospecimen_type=parsed_analysis.get("biospecimen_type", "Unknown"),
                data_volume=parsed_analysis.get("data_volume", "Unknown"),
                sensitive_data=parsed_analysis.get("sensitive_data", "Unknown"),
                cross_border_transfer=parsed_analysis.get("cross_border_transfer", "Unknown"),
                missing_fields=parsed_analysis.get("missing_fields", []),
                confidence_scores=parsed_analysis.get("confidence_scores", {}),
                interactive_prompts=parsed_analysis.get("interactive_prompts", []),
                suggestions=parsed_analysis.get("suggestions", []),
                analysis_summary=parsed_analysis.get("analysis_summary", "Analysis completed"),
                recommended_case_type=parsed_analysis.get("recommended_case_type", "Unknown"),
                case_type_confidence=parsed_analysis.get("case_type_confidence", 0.0),
                case_type_reasoning=parsed_analysis.get("case_type_reasoning", "")
            )
            
        except httpx.HTTPError as e:
            logger.error(f"Galileo AI LLM API error: {e}")
            raise Exception(f"Galileo AI LLM analysis failed: {str(e)}")
        except Exception as e:
            logger.error(f"Galileo AI analysis failed: {str(e)}")
            # Return fallback analysis
            return DPIAAnalysisResult(
                therapeutic_area="Unknown",
                procedure_type="Unknown", 
                assay_type="Unknown",
                pi_name="Unknown",
                pathologist="Unknown",
                project_title="Research Analysis",
                request_purpose="Data Analysis",
                biospecimen_type="Unknown",
                data_volume="Unknown",
                sensitive_data="Unknown",
                cross_border_transfer="Unknown",
                missing_fields=["therapeutic_area", "procedure_type", "assay_type", "pi_name", "pathologist"],
                confidence_scores={"overall_analysis": 0.3},
                interactive_prompts=[
                    "Galileo AI LLM is not available for analysis",
                    "Please check your Galileo AI configuration", 
                    "Provide missing mandatory fields manually"
                ],
                suggestions=[
                    "Galileo AI LLM is not available for analysis",
                    "Please check your Galileo AI configuration", 
                    "Provide missing mandatory fields manually"
                ],
                analysis_summary=f"Fallback analysis completed. Error: {str(e)}",
                recommended_case_type="Unknown",
                case_type_confidence=0.0,
                case_type_reasoning=""
            )
    
    def _create_analysis_prompt(self, research_text: str) -> str:
        """Create a comprehensive analysis prompt for Galileo AI LLM"""
        return f"""
You are an expert DPIA (Data Protection Impact Assessment) analyst for research projects. Analyze the following research text and extract all relevant information for DPIA case creation.

**Research Text:** {research_text}

**CALM vs DPIA Service Definitions:**

**CALM-EM (Cellular Analysis and Light Microscopy - Electron Microscopy) Services:**
- Advanced Light Microscopy and Imaging services
- Electron Microscopy Laboratory services
- Research microscopy (confocal, live-cell imaging, light sheet microscopy, electron microscopy)
- Training and technical support for microscopy
- Sample preparation and analysis for research purposes
- Research microscopy and analysis projects

**DPIA (Digital Pathology and Image Analysis) Services:**
- Whole slide scanning (brightfield and fluorescent tissue sections)
- Digital pathology workflows and gSlide Viewer uploads
- Slide submission to DPIA lab for scanning services
- Custom analysis algorithms for whole-slide images
- High-content imaging studies for in vitro experiments
- **Tissue section analysis and quantification**
- **Systematic imaging of tissue samples for quantitative analysis**
- **Multi-group comparative studies requiring standardized imaging**

**Field Extraction Guidelines:**

**PI Name Extraction:**
- Look for patterns: "PI as [Name]", "PI: [Name]", "Principal Investigator [Name]", "PI [Name]"
- Extract the actual name (e.g., "PI as John" → extract "John")
- If no PI mentioned, use "Unknown"

**Pathologist Extraction:**
- Look for patterns: "Pathologist as [Name]", "Pathologist: [Name]", "Pathologist [Name]"
- Extract the actual name (e.g., "Pathologist as Smith" → extract "Smith")
- If no pathologist mentioned, use "Unknown"

**Therapeutic Area:**
- Determine from research context (mouse eyes → Ophthalmology, cancer → Oncology, lung → Pulmonology, etc.)
- If unclear, use "Unknown"

**Assay Type:**
- Extract staining/labeling methods (SOX9, NucSpot, DAPI, H&E, TRITC, etc.)
- Include fluorescent markers and antibodies
- If multiple, combine them (e.g., "SOX9 + NucSpot 750", "AT2-TRITC + DAPI")

**Interactive Prompts Generation:**
When fields are missing or "Unknown", generate specific interactive prompts to help users provide the missing information:

**For Missing PI Name:**
- "Who is the Principal Investigator (PI) for this research project?"
- "Please provide the name of the PI responsible for this study"
- "Which researcher is leading this project as the Principal Investigator?"

**For Missing Pathologist:**
- "Is a pathologist involved in this research? If yes, please provide their name"
- "Will this research require pathologist review or consultation?"
- "Please specify the pathologist who will be involved in sample analysis"

**For Missing/Unknown Therapeutic Area:**
- Based on research context, suggest likely therapeutic areas and ask for confirmation:
  - If mentions "cancer", "tumor", "oncology" → "Is this oncology research? Please confirm the therapeutic area"
  - If mentions "immune", "antibody", "T-cell" → "Is this immunology research? Please specify the therapeutic area"
  - If mentions "eye", "retina", "vision" → "Is this ophthalmology research? Please confirm the therapeutic area"
  - If mentions "brain", "neuron", "neural" → "Is this neuroscience research? Please specify the therapeutic area"
  - If mentions "heart", "cardiac", "cardiovascular" → "Is this cardiovascular research? Please confirm the therapeutic area"
  - If mentions "lung", "pulmonary", "respiratory" → "Is this pulmonology research? Please confirm the therapeutic area"
  - If unclear → "What is the primary therapeutic area or medical field for this research?"

**For Missing Assay Type:**
- "What specific assays, staining methods, or markers will be used in this research?"
- "Please specify the experimental techniques or assays planned for this study"
- "What type of analysis or detection methods will be employed?"

**Instructions:**
Extract the following information and provide a JSON response:

{{
    "therapeutic_area": "specific medical field (e.g., Oncology, Immunology, Ophthalmology, Pulmonology, etc.)",
    "procedure_type": "type of procedure (e.g., Fluorescence (IF), Brightfield, etc.)",
    "assay_type": "assay classification",
    "pi_name": "Principal Investigator name (extract from patterns like 'PI as John')",
    "pathologist": "Pathologist name if involved (extract from patterns like 'Pathologist as Smith')",
    "project_title": "descriptive project title",
    "request_purpose": "purpose and objectives of the research",
    "biospecimen_type": "type of biological specimen",
    "data_volume": "estimated data volume (Small/Medium/Large)",
    "sensitive_data": "whether sensitive data is involved (Yes/No)",
    "cross_border_transfer": "whether cross-border data transfer occurs (Yes/No/Unknown)",
    "missing_fields": ["list of fields that couldn't be determined"],
    "confidence_scores": {{"field_name": confidence_value}},
    "interactive_prompts": ["specific questions to ask user for missing information - generate intelligent prompts based on missing fields"],
    "suggestions": ["list of actionable suggestions for DPIA completion"],
    "analysis_summary": "brief summary of the research and DPIA implications",
    "recommended_case_type": "CALM or DPIA",
    "case_type_confidence": 0.0-1.0,
    "case_type_reasoning": "Explanation for the recommendation"
}}

**Interactive Prompts Priority:**
1. Always generate prompts for missing PI, Pathologist, and Therapeutic Area
2. Make prompts specific and contextual based on the research text
3. Provide multiple prompt options when appropriate
4. Include suggestions or examples in prompts when helpful

**Case Type Recommendation Guidelines:**

**CRITICAL: Recommend DPIA when the text contains ANY of these indicators (HIGHEST PRIORITY):**
- **Slide scanning keywords**: "slide scanning", "scan slides", "scanning", "slide submission", "submit slides"
- **Digital pathology services**: "digital pathology", "gSlide Viewer", "DPIA lab", "whole slide scanning"
- **Tissue section analysis**: "lung section", "tissue section", "per section", "section analysis", "cells per lung section"
- **Quantification metrics**: "quantification", "# of cells per", "normalized by total area", "cells per lung section", "normalized by # of DAPI cells"
- **Multi-group studies**: "4 groups", "N=9-10 per group", "treatment groups", "control groups", "healthy, injured"
- **Systematic imaging**: "need imaging and quantification", "imaging of multiple samples"
- **Brightfield/fluorescent scanning**: "brightfield scanning", "fluorescent tissue sections"
- **Standardized analysis**: comparative studies requiring consistent imaging protocols

**MANDATORY DPIA CLASSIFICATION RULES:**
1. **ANY mention of "slide scanning" OR "scan slides" OR "scanning" → ALWAYS DPIA**
2. **ANY mention of "DPIA lab" OR "digital pathology" → ALWAYS DPIA**
3. **ANY mention of "tissue section" OR "lung section" → ALWAYS DPIA**
4. **ANY mention of "quantification" with tissue analysis → ALWAYS DPIA**
5. **ANY mention of "submit slides" OR "slide submission" → ALWAYS DPIA**

**Recommend CALM when the text contains (ONLY if NO DPIA indicators above):**
- **Individual cell research**: single cell analysis, live-cell imaging without tissue sections
- **Basic microscopy research**: "research on", "want to research" with simple biological samples (NOT tissue sections)
- **Sample preparation focus**: staining, cleared samples, preparation techniques (without quantification)
- **Research microscopy**: confocal, electron microscopy, light sheet without quantification
- **Training requests**: microscopy training, technical support
- **Explicit CALM requests**: "CALM request", "CALM service"

**Key Decision Logic (STRICT PRIORITY ORDER - FOLLOW EXACTLY):**
1. **If mentions "slide scanning" OR "scan slides" OR "scanning" → DPIA** (ABSOLUTE HIGHEST PRIORITY)
2. **If mentions "DPIA lab" OR "digital pathology" → DPIA** (ABSOLUTE HIGHEST PRIORITY)
3. **If mentions "submit slides" OR "slide submission" → DPIA** (ABSOLUTE HIGHEST PRIORITY)
4. **If mentions "lung section" OR "tissue section" OR "cells per section" → DPIA** (HIGHEST PRIORITY)
5. **If mentions quantification metrics like "normalized by total area" → DPIA** 
6. **Multi-group studies with imaging → DPIA** (systematic analysis across groups)
7. **Whole slide scanning/digital workflows → DPIA**
8. **Individual biological research with samples/staining → CALM** (ONLY if no tissue sections)
9. **Research microscopy without tissue sections → CALM**
10. **Training and technical support → CALM**

**Example Classifications (FOLLOW THESE EXACTLY):**
- "I need slide scanning on lung cell tissue sections" → **DPIA** (contains "slide scanning" and "tissue sections")
- "Please scan my lung tissue slides" → **DPIA** (contains "scan" and "slides")
- "Submit slides to DPIA lab for scanning" → **DPIA** (contains "submit slides", "DPIA lab", "scanning")
- "Whole slide scanning for digital pathology" → **DPIA** (contains "slide scanning" and "digital pathology")
- "Lung stem cells (AT2-TRITC) and total cells (DAPI) are stained. # of AT2 cells per lung section" → **DPIA** (contains "lung section" and quantification)
- "3D Image analysis of Cleared Mouse Eyes stained with SOX9 + NucSpot 750" → **CALM** (individual biological research, no tissue sections, no scanning)
- "CALM request for CD19/CD20 Allo1 CAR-T MS" → **CALM** (explicit CALM request)

**CRITICAL SLIDE SCANNING DETECTION:**
- **"slide scanning"** → DPIA (100% confidence)
- **"scan slides"** → DPIA (100% confidence)  
- **"scanning" + "slides"** → DPIA (100% confidence)
- **"scanning" + "tissue"** → DPIA (100% confidence)
- **"submit slides"** → DPIA (100% confidence)
- **"DPIA lab"** → DPIA (100% confidence)
- **"digital pathology"** → DPIA (100% confidence)

**MANDATORY PRE-CLASSIFICATION CHECK:**
Before making any recommendation, check if the text contains:
- "slide scanning" OR "scan slides" OR "scanning" → If YES, SET recommended_case_type = "DPIA"
- "DPIA lab" OR "digital pathology" → If YES, SET recommended_case_type = "DPIA"  
- "submit slides" OR "slide submission" → If YES, SET recommended_case_type = "DPIA"
- "tissue section" OR "lung section" → If YES, SET recommended_case_type = "DPIA"

**CRITICAL CLASSIFICATION INSTRUCTION:**
For the current research text: "{research_text}"

**STEP 1: MANDATORY DPIA CHECK (Check these first, in order):**
1. Does text contain "slide scanning" OR "scan slides" OR "scanning"? → If YES: DPIA
2. Does text contain "DPIA lab" OR "digital pathology"? → If YES: DPIA
3. Does text contain "submit slides" OR "slide submission"? → If YES: DPIA
4. Does text contain "tissue section" OR "lung section"? → If YES: DPIA
5. Does text contain quantification with tissue analysis? → If YES: DPIA

**STEP 2: If none of the above, then check CALM indicators**

**STEP 3: Set case_type_confidence to 1.0 for slide scanning/DPIA lab mentions, 0.9 for tissue sections**

**MANDATORY: If the text mentions slide scanning, DPIA lab, or digital pathology services, you MUST classify as DPIA regardless of other content.**

Respond with valid JSON only.
"""
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse the structured JSON response from Galileo AI LLM"""
        try:
            # Clean the response to extract JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            
            parsed = json.loads(response)
            
            # Debug: Log the parsed response to see what Galileo AI is returning
            logger.info(f"🔍 Galileo AI parsed response keys: {list(parsed.keys())}")
            if 'recommended_case_type' in parsed:
                logger.info(f"🎯 Case type recommendation found: {parsed['recommended_case_type']}")
            else:
                logger.warning("⚠️ No case type recommendation in Galileo AI response")
                logger.info(f"🔍 Full response: {json.dumps(parsed, indent=2)}")
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response content: {response}")
            
            # Fallback parsing for non-JSON responses
            return self._fallback_parse_response(response)
    
    def _fallback_parse_response(self, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON parsing fails"""
        # Generate intelligent interactive prompts for missing fields
        interactive_prompts = [
            "Who is the Principal Investigator (PI) for this research project?",
            "Is a pathologist involved in this research? If yes, please provide their name",
            "What is the primary therapeutic area or medical field for this research?",
            "What specific assays, staining methods, or markers will be used?",
            "Please provide more details about the research objectives and methodology"
        ]
        
        return {
            "therapeutic_area": "Unknown",
            "procedure_type": "Unknown", 
            "assay_type": "Unknown",
            "pi_name": "Unknown",
            "pathologist": "Unknown",
            "project_title": "Research Analysis",
            "request_purpose": "Data Analysis",
            "biospecimen_type": "Unknown",
            "data_volume": "Unknown",
            "sensitive_data": "Unknown",
            "cross_border_transfer": "Unknown",
            "missing_fields": ["therapeutic_area", "procedure_type", "assay_type", "pi_name", "pathologist"],
            "confidence_scores": {"overall_analysis": 0.3},
            "interactive_prompts": interactive_prompts,
            "suggestions": [
                "Please provide more specific information about the research",
                "Consider specifying the Principal Investigator and therapeutic area",
                "Include details about experimental methods and assays"
            ],
            "analysis_summary": "Analysis completed with limited information extraction - additional details needed",
            "recommended_case_type": "Unknown",
            "case_type_confidence": 0.0,
            "case_type_reasoning": "Insufficient information to determine case type"
        }
    
    async def _get_analysis_insights(self, text: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get additional insights from Galileo AI platform"""
        try:
            insights_payload = {
                "analysis_result": analysis,
                "input_text_length": len(text),
                "timestamp": datetime.now().isoformat()
            }
            
            response = await self.client.post("/insights/analysis", json=insights_payload)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.warning(f"Failed to get Galileo insights: {e}")
            return {
                "model_performance": "standard",
                "analysis_quality": "good",
                "recommendations": []
            }
    
    async def log_analysis_metrics(self, 
                                 analysis_input: str,
                                 analysis_output: DPIAAnalysisResult,
                                 user_feedback: Optional[Dict[str, Any]] = None):
        """
        Log analysis metrics to Galileo AI for monitoring and improvement
        """
        if not self.config.enable_monitoring:
            return
        
        try:
            metrics_payload = {
                "timestamp": datetime.now().isoformat(),
                "input_text": analysis_input,
                "input_length": len(analysis_input),
                "analysis_result": analysis_output.dict(),
                "user_feedback": user_feedback,
                "metadata": {
                    "source": "dpia_chatbot",
                    "environment": self.config.environment,
                    "model_name": self.config.model_name,
                    "integration_version": "2.0.0"
                }
            }
            
            response = await self.client.post("/metrics/log", json=metrics_payload)
            response.raise_for_status()
            
            logger.info("Analysis metrics logged to Galileo AI")
            
        except Exception as e:
            logger.warning(f"Failed to log metrics to Galileo AI: {e}")
    
    async def get_model_performance(self) -> Dict[str, Any]:
        """Get model performance metrics from Galileo AI"""
        try:
            response = await self.client.get("/metrics/performance")
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get model performance: {e}")
            return {}
    
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        General chat completion using Galileo AI LLM
        """
        try:
            payload = {
                "model": self.config.model_name,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                **kwargs
            }
            
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Initialize Galileo AI LLM integration
def create_galileo_llm_integration() -> Optional[GalileoLLMIntegration]:
    """
    Create Galileo AI LLM integration instance from environment variables
    """
    api_key = os.getenv("GALILEO_API_KEY")
    project_id = os.getenv("GALILEO_PROJECT_ID")
    
    if not api_key or not project_id:
        logger.warning("Galileo AI credentials not found. Integration disabled.")
        return None
    
    config = GalileoConfig(
        api_key=api_key,
        project_id=project_id,
        base_url=os.getenv("GALILEO_BASE_URL", "https://api.galileo.ai/v1"),
        environment=os.getenv("GALILEO_ENVIRONMENT", "production"),
        enable_monitoring=os.getenv("GALILEO_ENABLE_MONITORING", "true").lower() == "true",
        model_name=os.getenv("GALILEO_MODEL_NAME", "galileo-llm-v1"),
        temperature=float(os.getenv("GALILEO_TEMPERATURE", "0.1")),
        max_tokens=int(os.getenv("GALILEO_MAX_TOKENS", "4000"))
    )
    
    return GalileoLLMIntegration(config)

# Global instance - lazy initialization
_galileo_llm_instance = None

def galileo_llm() -> Optional[GalileoLLMIntegration]:
    """Get the Galileo LLM instance, creating it if needed (lazy initialization)"""
    global _galileo_llm_instance
    if _galileo_llm_instance is None:
        _galileo_llm_instance = create_galileo_llm_integration()
    return _galileo_llm_instance 