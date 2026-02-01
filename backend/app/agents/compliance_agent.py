"""Compliance & Regulatory Agent - Checks regulatory compliance"""
from typing import Dict, Any, List
from app.agents.prompts import COMPLIANCE_REGULATORY_PROMPT
from app.services.llm_service import llm_service


class ComplianceAgent:
    """Agent for regulatory compliance checking"""
    
    def __init__(self):
        self.system_prompt = COMPLIANCE_REGULATORY_PROMPT
    
    async def check_compliance(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check compliance against regulations
        
        Args:
            query: User query about compliance
            retrieved_chunks: Retrieved regulatory text chunks
        
        Returns:
            Dict with compliance verdict, rationale, regulations
        """
        # Format regulatory context
        if retrieved_chunks:
            context = "\n\n".join([
                f"Regulation: {chunk.get('metadata', {}).get('title', 'Unknown')}\n"
                f"Jurisdiction: {chunk.get('metadata', {}).get('jurisdiction', 'Unknown')}\n"
                f"Text:\n{chunk.get('text', '')}"
                for chunk in retrieved_chunks[:3]
            ])
        else:
            context = "No specific regulatory documents found. Please use your general knowledge of compliance frameworks and regulatory principles to answer."
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
User Query: {query}

Applicable Regulations:
{context}

Provide:
1. Compliance verdict: COMPLIANT / NON-COMPLIANT / UNCLEAR
2. Detailed rationale with specific rule citations (if documents provided) or general regulatory principles
3. Jurisdiction (if applicable)
4. Areas requiring expert review

Combine document-specific regulations (if any) with general compliance knowledge. Be conservative - if unclear, mark as UNCLEAR.
"""}
        ]
        
        try:
            response = await llm_service.chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=1500
            )
            
            # Extract verdict from response
            content = response["content"]
            verdict = "UNCLEAR"
            if "COMPLIANT" in content.upper() and "NON-COMPLIANT" not in content.upper():
                verdict = "COMPLIANT"
            elif "NON-COMPLIANT" in content.upper():
                verdict = "NON-COMPLIANT"
            
            return {
                "compliance_analysis": content,
                "verdict": verdict,
                "agent": "compliance_agent",
                "tokens_used": response["total_tokens"],
                "cost": response["cost"]
            }
            
        except Exception as e:
            return {
                "compliance_analysis": f"Error in compliance check: {str(e)}",
                "verdict": "UNCLEAR",
                "agent": "compliance_agent",
                "error": str(e)
            }


# Global compliance agent instance
compliance_agent = ComplianceAgent()
