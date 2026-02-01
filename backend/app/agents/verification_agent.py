"""Verification & Citation Agent - Ensures response quality and citations"""
import json
from typing import Dict, Any, List
from app.agents.prompts import VERIFICATION_CITATION_PROMPT
from app.services.llm_service import llm_service


class VerificationAgent:
    """Agent for verifying citations and detecting hallucinations"""
    
    def __init__(self):
        self.system_prompt = VERIFICATION_CITATION_PROMPT
    
    async def verify_response(
        self,
        query: str,
        response: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify response has proper citations and is supported by sources
        
        Args:
            query: Original user query
            response: Generated response to verify
            retrieved_chunks: Source chunks used for generation
        
        Returns:
            Dict with citations_valid, unsupported_claims, confidence_score, verification_notes
        """
        # Format retrieved chunks for context
        sources_text = "\n\n".join([
            f"Source {i+1}:\n{chunk.get('text', '')}\nMetadata: {chunk.get('metadata', {})}"
            for i, chunk in enumerate(retrieved_chunks[:5])
        ])
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
Verify this legal response:

Original Query: {query}

Response to Verify:
{response}

Available Source Documents:
{sources_text}

Check:
1. Are all legal claims properly cited?
2. Are there unsupported statements?
3. Do citations match source documents?
4. What is the confidence score (0.0-1.0)?

Provide verification as JSON.
"""}
        ]
        
        try:
            llm_response = await llm_service.chat_completion(
                messages=messages,
                temperature=0.0,
                max_tokens=500
            )
            
            content = llm_response["content"]
            
            # Extract JSON
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
            
            verification = json.loads(json_str)
            
            # Ensure confidence score is present
            if "confidence_score" not in verification:
                verification["confidence_score"] = 0.7
            
            return verification
            
        except Exception as e:
            # Default verification on error
            return {
                "citations_valid": False,
                "unsupported_claims": [],
                "confidence_score": 0.5,
                "verification_notes": f"Verification failed: {str(e)}. Manual review recommended."
            }
    
    def is_high_confidence(self, verification: Dict[str, Any], threshold: float = 0.6) -> bool:
        """Check if response meets confidence threshold"""
        return verification.get("confidence_score", 0.0) >= threshold


# Global verification agent instance
verification_agent = VerificationAgent()
