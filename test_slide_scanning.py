#!/usr/bin/env python3

import asyncio
import json
from galileo_integration import create_galileo_llm_integration, DPIAAnalysisRequest

async def test_slide_scanning():
    """Test slide scanning classification"""
    galileo = create_galileo_llm_integration()
    if not galileo:
        print('❌ Galileo AI not available')
        return
    
    # Test cases that should be DPIA
    test_cases = [
        "I need slide scanning on lung cell tissue sections for quantitative analysis",
        "Please scan my lung tissue slides for digital pathology analysis",
        "Submit slides to DPIA lab for brightfield scanning of lung sections",
        "Whole slide scanning for lung tissue sections with quantification",
        "I need slide scanning services for tissue section analysis"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {text}")
        try:
            request = DPIAAnalysisRequest(text=text)
            result = await galileo.analyze_dpia_text(request)
            
            print(f"   📊 Case Type: {result.recommended_case_type}")
            print(f"   🎯 Confidence: {result.case_type_confidence}")
            print(f"   💭 Reasoning: {result.case_type_reasoning}")
            
            # Check if classification is correct
            expected = "DPIA"
            actual = result.recommended_case_type
            status = "✅ CORRECT" if actual == expected else "❌ INCORRECT"
            print(f"   {status} (Expected: {expected}, Got: {actual})")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    await galileo.close()

if __name__ == "__main__":
    asyncio.run(test_slide_scanning()) 