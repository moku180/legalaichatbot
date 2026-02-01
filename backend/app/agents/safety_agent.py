"""Safety & Policy Agent - Enforces legal and ethical guardrails"""
import json
from typing import Dict, Any
from app.agents.prompts import SAFETY_POLICY_PROMPT, LEGAL_DISCLAIMER
from app.services.llm_service import llm_service


class SafetyAgent:
    """Agent for safety checks and policy enforcement"""
    
    def __init__(self):
        self.system_prompt = SAFETY_POLICY_PROMPT
    
    async def check_safety(
        self,
        query: str,
        jurisdiction: str = None
    ) -> Dict[str, Any]:
        """
        Check if query passes safety guidelines
        
        Args:
            query: User query
            jurisdiction: Expected jurisdiction
        
        Returns:
            Dict with safety_check, reason, suggested_action, disclaimer_added
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
Analyze this query for safety concerns:

Query: {query}
Expected Jurisdiction: {jurisdiction or "Not specified"}

Check for:
1. Requests for personalized legal advice
2. Jurisdiction mismatches
3. Illegal activity requests
4. Confidential data generation requests

Provide your safety assessment as JSON.
"""}
        ]
        
        try:
            response = await llm_service.chat_completion(
                messages=messages,
                temperature=0.0,
                max_tokens=500
            )
            
            # Parse JSON response
            content = response["content"]
            
            # Try to extract JSON from response
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
            
            safety_result = json.loads(json_str)
            
            # Ensure disclaimer is added
            safety_result["disclaimer_added"] = True
            safety_result["disclaimer_text"] = LEGAL_DISCLAIMER
            
            return safety_result
            
        except Exception as e:
            # Default to safe behavior on error
            return {
                "safety_check": "WARN",
                "reason": f"Safety check failed: {str(e)}. Proceeding with caution.",
                "suggested_action": "Review response carefully and consult a legal professional.",
                "disclaimer_added": True,
                "disclaimer_text": LEGAL_DISCLAIMER
            }
    
    def should_refuse(self, safety_result: Dict[str, Any]) -> bool:
        """Check if request should be refused"""
        return safety_result.get("safety_check") == "REFUSE"
    
    def should_warn(self, safety_result: Dict[str, Any]) -> bool:
        """Check if warning should be shown"""
        return safety_result.get("safety_check") in ["WARN", "REFUSE"]


# Global safety agent instance
safety_agent = SafetyAgent()
