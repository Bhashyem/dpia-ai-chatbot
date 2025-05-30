#!/usr/bin/env python3
"""
Claude LLM Integration for DPIA Chatbot
Provides intelligent analysis and conversation capabilities using Anthropic's Claude
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import anthropic
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class ClaudeConfig:
    """Configuration for Claude LLM integration"""
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        self.max_tokens = int(os.getenv("CLAUDE_MAX_TOKENS", "4000"))
        self.temperature = float(os.getenv("CLAUDE_TEMPERATURE", "0.3"))
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

class ConversationMessage(BaseModel):
    """Represents a message in the conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.now()

class AnalysisResult(BaseModel):
    """Represents the result of text analysis"""
    detected_fields: Dict[str, str]
    missing_fields: List[str]
    confidence_scores: Dict[str, float]
    interactive_prompts: List[Dict[str, Any]]
    suggestions: List[str]
    analysis_summary: str

class ClaudeIntegration:
    """Main class for Claude LLM integration"""
    
    def __init__(self):
        self.config = ClaudeConfig()
        self.client = anthropic.Anthropic(api_key=self.config.api_key)
        self.conversation_history: List[ConversationMessage] = []
        
        # DPIA field definitions
        self.mandatory_fields = [
            "PI", "Pathologist", "Therapeutic Area", "Procedure", 
            "Assay Type/Staining Type", "Project Title", "Request Purpose"
        ]
        
        self.therapeutic_areas = [
            "CVRM", "Neurology", "Oncology", "Ophthalmology", 
            "Infectious Diseases", "Immunology", "Unknown"
        ]
        
        self.procedures = [
            "Bright-field (BF)", "Fluorescence (IF)", "BF+IF", "Unknown"
        ]
        
        self.assay_types = [
            "H&E", "IHC", "Special Stain", "Other", "Unknown"
        ]
        
        # Additional context for enhanced analysis
        self.reference_context = ""
        self.analysis_guidelines = ""

    def set_reference_context(self, context: str):
        """Set additional reference context for enhanced analysis"""
        self.reference_context = context
        logger.info("Reference context updated for enhanced analysis")

    def set_analysis_guidelines(self, guidelines: str):
        """Set specific analysis guidelines from reference documents"""
        self.analysis_guidelines = guidelines
        logger.info("Analysis guidelines updated")

    def load_context_from_file(self, file_path: str):
        """Load additional context from a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                context = f.read()
                self.set_reference_context(context)
                logger.info(f"Loaded context from {file_path}")
        except Exception as e:
            logger.error(f"Failed to load context from {file_path}: {e}")

    def add_to_conversation(self, role: str, content: str):
        """Add a message to the conversation history"""
        message = ConversationMessage(role=role, content=content)
        self.conversation_history.append(message)
        
        # Keep only last 10 messages to manage context length
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

    async def analyze_research_text(self, research_text: str, use_enhanced_context: bool = True) -> AnalysisResult:
        """Analyze research text using Claude to extract DPIA-relevant information"""
        
        # Build enhanced system prompt with reference context
        base_system_prompt = f"""You are an expert AI assistant specializing in analyzing biomedical research text for DPIA (Data Privacy Impact Assessment) case creation. Your task is to extract specific information from research text and identify missing mandatory fields.

MANDATORY FIELDS TO EXTRACT:
{', '.join(self.mandatory_fields)}

FIELD DEFINITIONS:
- PI: Primary Investigator (person leading the research)
- Pathologist: Medical professional reviewing pathology
- Therapeutic Area: Medical domain ({', '.join(self.therapeutic_areas)})
- Procedure: Imaging/analysis method ({', '.join(self.procedures)})
- Assay Type/Staining Type: Laboratory technique ({', '.join(self.assay_types)})
- Project Title: Descriptive name for the research project
- Request Purpose: Objective/goal of the research"""

        # Add reference context if available
        if use_enhanced_context and self.reference_context:
            enhanced_context = f"""

ADDITIONAL REFERENCE CONTEXT:
The following reference material provides additional guidance for DPIA analysis:

{self.reference_context[:2000]}  # Limit context to avoid token limits

Use this reference context to:
- Better understand DPIA requirements
- Improve field extraction accuracy
- Provide more relevant suggestions
- Generate better interactive prompts"""
            base_system_prompt += enhanced_context

        # Add analysis guidelines if available
        if use_enhanced_context and self.analysis_guidelines:
            guidelines_context = f"""

SPECIFIC ANALYSIS GUIDELINES:
{self.analysis_guidelines[:1000]}

Follow these guidelines when analyzing research text and extracting DPIA information."""
            base_system_prompt += guidelines_context

        system_prompt = base_system_prompt + f"""

ANALYSIS INSTRUCTIONS:
1. Carefully read the research text
2. Extract any explicitly mentioned information for each mandatory field
3. Use intelligent inference for fields that can be reasonably deduced
4. Apply the reference context and guidelines to improve accuracy
5. Mark fields as "Unknown" only if no reasonable inference can be made
6. Provide confidence scores (0.0-1.0) for each detected field
7. Generate interactive prompts for missing/uncertain fields
8. Suggest improvements and next steps based on reference materials

RESPONSE FORMAT:
Return a JSON object with this exact structure:
{{
    "detected_fields": {{
        "PI": "extracted or inferred value",
        "Pathologist": "extracted or inferred value",
        "Therapeutic Area": "one of the valid options",
        "Procedure": "one of the valid options", 
        "Assay Type/Staining Type": "one of the valid options",
        "Project Title": "descriptive title",
        "Request Purpose": "research objective"
    }},
    "confidence_scores": {{
        "PI": 0.8,
        "Pathologist": 0.3,
        // ... scores for each field
    }},
    "missing_fields": ["list of fields marked as Unknown"],
    "interactive_prompts": [
        {{
            "field": "field_name",
            "question": "User-friendly question",
            "input_type": "selection" or "text_input",
            "options": ["option1", "option2"] // for selection type
        }}
    ],
    "suggestions": ["helpful suggestions for the user"],
    "analysis_summary": "Brief summary of what was found and what's needed"
}}

Be thorough but concise. Focus on accuracy and user experience."""

        user_prompt = f"""Please analyze this research text for DPIA case creation:

RESEARCH TEXT:
{research_text}

Extract all possible information for the mandatory fields, provide confidence scores, and generate appropriate prompts for missing information."""

        try:
            # Add to conversation history
            self.add_to_conversation("user", f"Analyze research text: {research_text[:200]}...")
            
            response = await self._call_claude(system_prompt, user_prompt)
            
            # Add response to conversation history
            self.add_to_conversation("assistant", response[:200] + "...")
            
            # Parse the JSON response
            analysis_data = json.loads(response)
            
            return AnalysisResult(**analysis_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            # Fallback to basic analysis
            return self._fallback_analysis(research_text)
        except Exception as e:
            logger.error(f"Error in Claude analysis: {e}")
            return self._fallback_analysis(research_text)

    async def generate_conversational_response(self, user_message: str, context: Dict[str, Any] = None) -> str:
        """Generate a conversational response using Claude"""
        
        system_prompt = """You are a helpful AI assistant for a DPIA (Data Privacy Impact Assessment) analysis chatbot. You help researchers analyze their text and create DPIA cases in a Pega system.

PERSONALITY:
- Professional but friendly
- Expert in biomedical research and data privacy
- Patient and helpful with explanations
- Use appropriate emojis to make interactions engaging
- Provide clear, actionable guidance

CAPABILITIES:
- Analyze research text for DPIA-relevant information
- Guide users through missing field completion
- Explain DPIA processes and requirements
- Help with Pega case creation
- Provide research methodology insights

RESPONSE STYLE:
- Use clear, structured responses
- Include relevant emojis (🔬, 📋, ✅, ❌, 💡, etc.)
- Provide specific, actionable next steps
- Be encouraging and supportive
- Keep responses concise but comprehensive"""

        # Build context from conversation history
        conversation_context = ""
        if self.conversation_history:
            recent_messages = self.conversation_history[-5:]  # Last 5 messages
            for msg in recent_messages:
                conversation_context += f"{msg.role}: {msg.content[:100]}...\n"

        user_prompt = f"""CONVERSATION CONTEXT:
{conversation_context}

CURRENT USER MESSAGE:
{user_message}

ADDITIONAL CONTEXT:
{json.dumps(context) if context else 'None'}

Please provide a helpful, conversational response that addresses the user's message while maintaining context of our ongoing conversation about DPIA analysis."""

        try:
            response = await self._call_claude(system_prompt, user_prompt)
            self.add_to_conversation("user", user_message)
            self.add_to_conversation("assistant", response)
            return response
        except Exception as e:
            logger.error(f"Error generating conversational response: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again or contact support if the issue persists."

    async def enhance_field_detection(self, field_name: str, research_text: str, current_value: str) -> Tuple[str, float]:
        """Use Claude to enhance detection of a specific field"""
        
        system_prompt = f"""You are an expert at extracting specific information from biomedical research text. Focus on finding the {field_name} from the provided text.

FIELD: {field_name}

INSTRUCTIONS:
- Analyze the text carefully for any mention or indication of {field_name}
- Use context clues and domain knowledge to make reasonable inferences
- If you find a value, provide it exactly as it should appear
- If uncertain, return "Unknown"
- Provide a confidence score from 0.0 to 1.0

RESPONSE FORMAT:
Return only a JSON object: {{"value": "extracted_value", "confidence": 0.8}}"""

        user_prompt = f"""Current detected value: {current_value}

Research text to analyze:
{research_text}

Please extract or improve the {field_name} value."""

        try:
            response = await self._call_claude(system_prompt, user_prompt)
            result = json.loads(response)
            return result.get("value", current_value), result.get("confidence", 0.0)
        except Exception as e:
            logger.error(f"Error enhancing field detection for {field_name}: {e}")
            return current_value, 0.0

    async def generate_project_title(self, research_text: str) -> str:
        """Generate a descriptive project title based on research text"""
        
        system_prompt = """You are an expert at creating concise, descriptive titles for biomedical research projects. Create a professional title that captures the essence of the research.

GUIDELINES:
- Keep it under 80 characters
- Be specific and descriptive
- Use proper scientific terminology
- Include key elements like cell types, procedures, or objectives
- Make it suitable for official documentation

Return only the title, nothing else."""

        user_prompt = f"Create a project title for this research:\n\n{research_text}"

        try:
            title = await self._call_claude(system_prompt, user_prompt)
            return title.strip().strip('"')
        except Exception as e:
            logger.error(f"Error generating project title: {e}")
            return "Research Analysis Project"

    async def _call_claude(self, system_prompt: str, user_prompt: str) -> str:
        """Make a call to Claude API"""
        try:
            message = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise

    def _fallback_analysis(self, research_text: str) -> AnalysisResult:
        """Fallback analysis when Claude is unavailable"""
        logger.warning("Using fallback analysis due to Claude API issues")
        
        # Basic keyword-based analysis
        text_lower = research_text.lower()
        
        detected_fields = {}
        confidence_scores = {}
        
        # Therapeutic Area detection
        if any(word in text_lower for word in ["lung", "stem cell", "at2", "respiratory"]):
            detected_fields["Therapeutic Area"] = "Neurology"
            confidence_scores["Therapeutic Area"] = 0.7
        elif any(word in text_lower for word in ["cancer", "tumor", "oncology"]):
            detected_fields["Therapeutic Area"] = "Oncology"
            confidence_scores["Therapeutic Area"] = 0.8
        elif any(word in text_lower for word in ["mammalian", "cell", "molecule"]):
            detected_fields["Therapeutic Area"] = "Unknown"  # Need more context
            confidence_scores["Therapeutic Area"] = 0.0
        else:
            detected_fields["Therapeutic Area"] = "Unknown"
            confidence_scores["Therapeutic Area"] = 0.0
        
        # Procedure detection
        if any(word in text_lower for word in ["tritc", "dapi", "fluorescence", "fluorescent"]):
            detected_fields["Procedure"] = "Fluorescence (IF)"
            confidence_scores["Procedure"] = 0.8
        elif any(word in text_lower for word in ["time-lapse", "imaging", "microscopy", "leica", "sp8"]):
            detected_fields["Procedure"] = "Fluorescence (IF)"  # Time-lapse imaging typically uses fluorescence
            confidence_scores["Procedure"] = 0.9
        else:
            detected_fields["Procedure"] = "Unknown"
            confidence_scores["Procedure"] = 0.0
        
        # Assay Type detection
        if any(word in text_lower for word in ["time-lapse", "imaging", "monitoring"]):
            detected_fields["Assay Type/Staining Type"] = "Time-lapse imaging"
            confidence_scores["Assay Type/Staining Type"] = 0.9
        elif any(word in text_lower for word in ["tritc", "dapi", "fluorescent"]):
            detected_fields["Assay Type/Staining Type"] = "Other"
            confidence_scores["Assay Type/Staining Type"] = 0.7
        else:
            detected_fields["Assay Type/Staining Type"] = "Unknown"
            confidence_scores["Assay Type/Staining Type"] = 0.0
        
        # Project Title generation
        if "time-lapse" in text_lower and "imaging" in text_lower:
            detected_fields["Project Title"] = research_text.strip()
            confidence_scores["Project Title"] = 0.95
        elif len(research_text.strip()) > 10:
            detected_fields["Project Title"] = research_text.strip()
            confidence_scores["Project Title"] = 0.8
        else:
            detected_fields["Project Title"] = "Unknown"
            confidence_scores["Project Title"] = 0.0
        
        # Request Purpose generation
        if "monitor" in text_lower and "distribution" in text_lower:
            detected_fields["Request Purpose"] = "Time-lapse imaging to monitor small molecule distribution in mammalian cells"
            confidence_scores["Request Purpose"] = 0.95
        elif "imaging" in text_lower:
            detected_fields["Request Purpose"] = f"Imaging analysis: {research_text.strip()}"
            confidence_scores["Request Purpose"] = 0.7
        else:
            detected_fields["Request Purpose"] = "Unknown"
            confidence_scores["Request Purpose"] = 0.0
        
        # Set remaining fields as Unknown
        for field in self.mandatory_fields:
            if field not in detected_fields:
                detected_fields[field] = "Unknown"
                confidence_scores[field] = 0.0
        
        missing_fields = [field for field, value in detected_fields.items() if value == "Unknown"]
        found_fields = [field for field, value in detected_fields.items() if value != "Unknown"]
        
        # Generate basic prompts
        interactive_prompts = []
        for field in missing_fields:
            if field == "Therapeutic Area":
                interactive_prompts.append({
                    "field": field,
                    "question": f"Which therapeutic area does this research belong to?",
                    "input_type": "selection",
                    "options": self.therapeutic_areas
                })
            else:
                interactive_prompts.append({
                    "field": field,
                    "question": f"Please provide the {field}:",
                    "input_type": "text_input"
                })
        
        return AnalysisResult(
            detected_fields=detected_fields,
            missing_fields=missing_fields,
            confidence_scores=confidence_scores,
            interactive_prompts=interactive_prompts,
            suggestions=["Please provide the missing information to create a complete DPIA case"],
            analysis_summary=f"Basic analysis completed. Found {len(found_fields)} fields, need {len(missing_fields)} more."
        )

# Global instance
claude_integration = ClaudeIntegration() 