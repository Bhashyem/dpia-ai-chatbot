#!/usr/bin/env python3
"""
Galileo AI LLM Adapter - Replaces Claude Integration
Maintains the same interface as claude_integration.py but uses Galileo AI LLM
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel
from galileo_integration import galileo_llm, DPIAAnalysisRequest, DPIAAnalysisResult

logger = logging.getLogger(__name__)

# Maintain compatibility with existing AnalysisResult model
class AnalysisResult(BaseModel):
    """Analysis result model compatible with existing claude_integration interface"""
    detected_fields: Dict[str, str]
    missing_fields: List[str]
    confidence_scores: Dict[str, float]
    interactive_prompts: List[Dict[str, Any]]
    suggestions: List[str]
    analysis_summary: str
    
    # Additional Galileo-specific fields (optional, won't break compatibility)
    therapeutic_area: Optional[str] = None
    procedure_type: Optional[str] = None
    assay_type: Optional[str] = None
    pi_name: Optional[str] = None
    pathologist: Optional[str] = None
    project_title: Optional[str] = None
    request_purpose: Optional[str] = None
    compliance_status: Optional[str] = None
    galileo_insights: Optional[Dict[str, Any]] = None
    # Add case type recommendation fields
    recommended_case_type: Optional[str] = None
    case_type_confidence: Optional[float] = None
    case_type_reasoning: Optional[str] = None

class GalileoClaudeAdapter:
    """
    Adapter class that replaces Claude with Galileo AI LLM
    Maintains the same interface as the original claude_integration
    """
    
    def __init__(self):
        self.context_data = {
            "reference_context": "",
            "analysis_guidelines": ""
        }
        logger.info("Galileo AI LLM adapter initialized (replacing Claude)")
    
    @property
    def galileo_client(self):
        """Get the Galileo client instance (lazy loading)"""
        return galileo_llm()
    
    async def analyze_research_text(self, 
                                  research_text: str, 
                                  enhance_fields: bool = True,
                                  user_id: Optional[str] = None,
                                  session_id: Optional[str] = None) -> AnalysisResult:
        """
        Analyze research text using Galileo AI LLM instead of Claude
        Maintains compatibility with existing claude_integration interface
        """
        if not self.galileo_client:
            logger.error("Galileo AI LLM client not available")
            return self._create_fallback_result(research_text)
        
        try:
            # Create Galileo AI analysis request
            request = DPIAAnalysisRequest(
                text=research_text,
                analysis_type="dpia_analysis",
                metadata={
                    "context": self.context_data,
                    "enhance_fields": enhance_fields
                },
                user_id=user_id,
                session_id=session_id,
                enhance_fields=enhance_fields
            )
            
            # Perform analysis using Galileo AI LLM
            galileo_result = await self.galileo_client.analyze_dpia_text(request)
            
            # Convert to compatible AnalysisResult format
            detected_fields = {
                "therapeutic_area": galileo_result.therapeutic_area,
                "procedure_type": galileo_result.procedure_type,
                "assay_type": galileo_result.assay_type,
                "pi_name": galileo_result.pi_name,
                "pathologist": galileo_result.pathologist,
                "project_title": galileo_result.project_title,
                "request_purpose": galileo_result.request_purpose,
                "biospecimen_type": galileo_result.biospecimen_type,
                "data_volume": galileo_result.data_volume,
                "sensitive_data": galileo_result.sensitive_data,
                "cross_border_transfer": galileo_result.cross_border_transfer,
                # Include case type recommendation in detected_fields
                "recommended_case_type": galileo_result.recommended_case_type
            }
            
            # Convert interactive_prompts to proper format if needed
            interactive_prompts = []
            if galileo_result.interactive_prompts:
                for prompt in galileo_result.interactive_prompts:
                    if isinstance(prompt, str):
                        # Convert string to dictionary format
                        interactive_prompts.append({
                            "question": prompt,
                            "field": "unknown",
                            "type": "text"
                        })
                    elif isinstance(prompt, dict):
                        interactive_prompts.append(prompt)
                    else:
                        # Fallback for other types
                        interactive_prompts.append({
                            "question": str(prompt),
                            "field": "unknown", 
                            "type": "text"
                        })
            
            analysis_result = AnalysisResult(
                detected_fields=detected_fields,
                missing_fields=galileo_result.missing_fields,
                confidence_scores=galileo_result.confidence_scores,
                interactive_prompts=interactive_prompts,
                suggestions=galileo_result.suggestions,
                analysis_summary=galileo_result.analysis_summary,
                therapeutic_area=galileo_result.therapeutic_area,
                procedure_type=galileo_result.procedure_type,
                assay_type=galileo_result.assay_type,
                pi_name=galileo_result.pi_name,
                pathologist=galileo_result.pathologist,
                project_title=galileo_result.project_title,
                request_purpose=galileo_result.request_purpose,
                compliance_status="Requires Review",  # Default value since not in new model
                galileo_insights={"analysis_type": "dpia_analysis"},
                recommended_case_type=galileo_result.recommended_case_type,
                case_type_confidence=galileo_result.case_type_confidence,
                case_type_reasoning=galileo_result.case_type_reasoning
            )
            
            # Log metrics to Galileo AI
            if self.galileo_client.config.enable_monitoring:
                await self.galileo_client.log_analysis_metrics(
                    analysis_input=research_text,
                    analysis_output=galileo_result
                )
            
            logger.info(f"Galileo AI analysis completed. Detected {len(analysis_result.detected_fields)} fields")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Galileo AI analysis failed: {e}")
            return self._create_fallback_result(research_text, error=str(e))
    
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        General chat completion using Galileo AI LLM
        Replaces Claude chat functionality
        """
        if not self.galileo_client:
            return "Galileo AI LLM is not available. Please check your configuration."
        
        try:
            response = await self.galileo_client.chat_completion(messages, **kwargs)
            return response
            
        except Exception as e:
            logger.error(f"Galileo AI chat completion failed: {e}")
            return f"I apologize, but I'm experiencing technical difficulties. Error: {str(e)}"
    
    async def generate_conversational_response(self, 
                                             user_message: str,
                                             context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate conversational response using Galileo AI LLM
        Maintains compatibility with existing interface
        """
        if not self.galileo_client:
            return "Galileo AI LLM is not available. Please check your configuration."
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful DPIA (Data Privacy Impact Assessment) assistant for pharmaceutical research. Provide clear, accurate, and helpful responses about data privacy, research compliance, and DPIA requirements."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
            
            # Add context if provided
            if context:
                context_str = f"Additional context: {json.dumps(context, indent=2)}"
                messages[0]["content"] += f"\n\n{context_str}"
            
            response = await self.galileo_client.chat_completion(messages)
            return response
            
        except Exception as e:
            logger.error(f"Galileo AI conversational response failed: {e}")
            return f"I apologize, but I'm experiencing technical difficulties. Error: {str(e)}"
    
    async def enhance_field_detection(self, 
                                    field: str,
                                    research_text: str, 
                                    current_value: str) -> tuple[str, float]:
        """
        Enhance field detection using Galileo AI LLM
        Maintains compatibility with existing claude_integration interface
        
        Args:
            field: The field name to enhance
            research_text: The research text to analyze
            current_value: The current detected value
            
        Returns:
            Tuple of (enhanced_value, confidence_score)
        """
        if not self.galileo_client:
            logger.warning("Galileo AI not available for field enhancement")
            return current_value, 0.3
        
        try:
            # Create enhancement prompt
            enhancement_prompt = f"""
            Analyze the following research text and improve the detection of the field '{field}'.
            Current detected value: '{current_value}'
            
            Research text: {research_text}
            
            Please provide:
            1. An improved value for the field '{field}' based on the text
            2. A confidence score (0.0-1.0) for your detection
            
            Respond in JSON format:
            {{"enhanced_value": "improved_value", "confidence": 0.8}}
            """
            
            messages = [{"role": "user", "content": enhancement_prompt}]
            response = await self.galileo_client.chat_completion(messages)
            
            # Parse response
            import json
            try:
                result = json.loads(response)
                enhanced_value = result.get("enhanced_value", current_value)
                confidence = float(result.get("confidence", 0.5))
                return enhanced_value, confidence
            except (json.JSONDecodeError, ValueError):
                logger.warning(f"Failed to parse enhancement response: {response}")
                return current_value, 0.3
                
        except Exception as e:
            logger.error(f"Field enhancement failed: {e}")
            return current_value, 0.3
    
    def set_context(self, context: str, context_type: str = "reference"):
        """
        Set analysis context (reference materials or guidelines)
        """
        if context_type == "reference":
            self.context_data["reference_context"] = context
        elif context_type == "guidelines":
            self.context_data["analysis_guidelines"] = context
        else:
            self.context_data[context_type] = context
        
        logger.info(f"Updated {context_type} context ({len(context)} characters)")
    
    def get_context_status(self) -> Dict[str, Any]:
        """
        Get current context status
        """
        return {
            "reference_context_length": len(self.context_data.get("reference_context", "")),
            "guidelines_length": len(self.context_data.get("analysis_guidelines", "")),
            "has_reference_context": bool(self.context_data.get("reference_context")),
            "has_guidelines": bool(self.context_data.get("analysis_guidelines")),
            "llm_provider": "Galileo AI",
            "model_name": self.galileo_client.config.model_name if self.galileo_client else "Not Available",
            "monitoring_enabled": self.galileo_client.config.enable_monitoring if self.galileo_client else False
        }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get Galileo AI model performance metrics
        """
        if not self.galileo_client:
            return {"error": "Galileo AI client not available"}
        
        try:
            return await self.galileo_client.get_model_performance()
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {"error": str(e)}
    
    def _create_fallback_result(self, research_text: str, error: Optional[str] = None) -> AnalysisResult:
        """
        Create a fallback analysis result when Galileo AI is not available
        """
        return AnalysisResult(
            detected_fields={
                "therapeutic_area": "Unknown",
                "procedure_type": "Unknown",
                "assay_type": "Unknown",
                "pi_name": "Unknown",
                "pathologist": "Unknown",
                "project_title": "Research Analysis",
                "request_purpose": "Data Analysis"
            },
            missing_fields=["therapeutic_area", "procedure_type", "assay_type", "pi_name", "pathologist"],
            confidence_scores={"overall_analysis": 0.3},
            interactive_prompts=[],
            suggestions=[
                "Galileo AI LLM is not available for analysis",
                "Please check your Galileo AI configuration",
                "Provide missing mandatory fields manually"
            ],
            analysis_summary=f"Fallback analysis completed. {'Error: ' + error if error else 'Galileo AI LLM not available.'}",
            compliance_status="Requires Review",
            recommended_case_type=None,
            case_type_confidence=None,
            case_type_reasoning=None
        )
    
    async def close(self):
        """Close connections"""
        if self.galileo_client:
            await self.galileo_client.close()
    
    async def generate_project_title(self, research_text: str) -> str:
        """
        Generate a project title from research text using Galileo AI LLM
        Maintains compatibility with existing claude_integration interface
        
        Args:
            research_text: The research text to analyze
            
        Returns:
            Generated project title
        """
        if not self.galileo_client:
            # Fallback to simple title generation
            return self._generate_simple_title(research_text)
        
        try:
            prompt = f"""Based on the following research text, generate a concise and descriptive project title (maximum 100 characters):

Research Text:
{research_text}

Generate a professional project title that captures the main research focus. The title should be:
- Concise (under 100 characters)
- Descriptive of the research
- Professional and scientific
- Suitable for a DPIA case

Project Title:"""

            response = await self.galileo_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.galileo_client.config.model_name,
                temperature=0.1,
                max_tokens=100
            )
            
            if response and response.choices:
                title = response.choices[0].message.content.strip()
                # Clean up the title
                title = title.replace('"', '').replace("'", "").strip()
                if title.lower().startswith("project title:"):
                    title = title[14:].strip()
                return title[:100]  # Ensure max length
            
        except Exception as e:
            logger.error(f"Error generating project title with Galileo AI: {e}")
        
        # Fallback to simple title generation
        return self._generate_simple_title(research_text)
    
    def _generate_simple_title(self, research_text: str) -> str:
        """Generate a simple project title from research text"""
        text_lower = research_text.lower()
        
        # Look for key research terms
        research_terms = []
        
        # Cell types
        if "stem cell" in text_lower:
            research_terms.append("Stem Cell")
        if "lung" in text_lower:
            research_terms.append("Lung")
        if "at2" in text_lower:
            research_terms.append("AT2")
        if "cancer" in text_lower:
            research_terms.append("Cancer")
        if "tumor" in text_lower:
            research_terms.append("Tumor")
        
        # Research activities
        activities = []
        if "quantification" in text_lower:
            activities.append("Quantification")
        if "imaging" in text_lower:
            activities.append("Imaging")
        if "analysis" in text_lower:
            activities.append("Analysis")
        if "stain" in text_lower:
            activities.append("Staining")
        
        # Create title
        if research_terms and activities:
            return f"{' '.join(research_terms)} {' '.join(activities)} Study"
        elif research_terms:
            return f"{' '.join(research_terms)} Research Study"
        elif activities:
            return f"{' '.join(activities)} Research Project"
        else:
            # Extract first meaningful sentence
            sentences = research_text.split('.')
            if sentences and len(sentences[0].strip()) > 10:
                title = sentences[0].strip()
                return title[:100] if len(title) <= 100 else title[:97] + "..."
            
            return "Research Analysis Project"

# Create global instance to replace claude_integration
galileo_claude_adapter = GalileoClaudeAdapter()

# Maintain compatibility with existing imports
claude_integration = galileo_claude_adapter 