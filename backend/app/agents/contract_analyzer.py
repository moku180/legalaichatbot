"""Contract Analysis Agent - Analyzes contracts and identifies risks"""
from typing import Dict, Any
from app.agents.prompts import CONTRACT_ANALYSIS_PROMPT
from app.services.llm_service import llm_service


class ContractAnalyzerAgent:
    """Agent for analyzing contracts and identifying risks"""
    
    def __init__(self):
        self.system_prompt = CONTRACT_ANALYSIS_PROMPT
    
    async def analyze_contract(
        self,
        query: str,
        contract_text: str = None
    ) -> Dict[str, Any]:
        """
        Analyze contract for clauses, risks, and obligations
        
        Args:
            query: User query about contract
            contract_text: Contract text to analyze (if provided)
        
        Returns:
            Dict with clause analysis, risks, obligations
        """
        if not contract_text:
            contract_text = "No contract text provided. Please provide contract text for analysis."
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
User Query: {query}

Contract Text:
{contract_text[:5000]}  # Limit to first 5000 chars

Provide:
1. Key clauses identified (payment, termination, liability, IP, etc.)
2. Potential risks and unusual terms
3. Obligations for each party
4. Missing standard clauses
5. Areas requiring legal review

Quote exact clause text when referencing.
"""}
        ]
        
        try:
            response = await llm_service.chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=2000
            )
            
            return {
                "contract_analysis": response["content"],
                "agent": "contract_analyzer",
                "tokens_used": response["total_tokens"],
                "cost": response["cost"]
            }
            
        except Exception as e:
            return {
                "contract_analysis": f"Error in contract analysis: {str(e)}",
                "agent": "contract_analyzer",
                "error": str(e)
            }


# Global contract analyzer instance
contract_analyzer_agent = ContractAnalyzerAgent()
