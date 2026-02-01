"""Case Law Research Agent - Finds and analyzes precedents"""
from typing import Dict, Any, List
from app.agents.prompts import CASE_LAW_RESEARCH_PROMPT
from app.services.llm_service import llm_service


class CaseLawResearcherAgent:
    """Agent for researching case law and precedents"""
    
    def __init__(self):
        self.system_prompt = CASE_LAW_RESEARCH_PROMPT
    
    async def research_case_law(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Research case law and extract precedents
        
        Args:
            query: User query about case law
            retrieved_chunks: Retrieved case law chunks
        
        Returns:
            Dict with case analysis, precedents, citations
        """
        # Format case law context
        if retrieved_chunks:
            context = "\n\n".join([
                f"Case: {chunk.get('metadata', {}).get('title', 'Unknown')}\n"
                f"Court: {chunk.get('metadata', {}).get('court_level', 'Unknown')}\n"
                f"Jurisdiction: {chunk.get('metadata', {}).get('jurisdiction', 'Unknown')}\n"
                f"Year: {chunk.get('metadata', {}).get('year', 'Unknown')}\n"
                f"Excerpt:\n{chunk.get('text', '')}"
                for chunk in retrieved_chunks[:3]
            ])
        else:
            context = "No specific case law documents found. Please use your general legal knowledge about case law principles and precedents to answer."
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
User Query: {query}

Relevant Case Law:
{context}

Provide:
1. Full case citations (if documents provided)
2. Ratio decidendi (legal reasoning) - from documents or general principles
3. Binding vs. persuasive authority concepts
4. Relevant quotes from judgments (if available)
5. How case law principles apply to the query

Combine document-specific information (if any) with general case law knowledge. Be precise with citations when available.
"""}
        ]
        
        try:
            response = await llm_service.chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=1500
            )
            
            return {
                "case_analysis": response["content"],
                "agent": "case_law_researcher",
                "tokens_used": response["total_tokens"],
                "cost": response["cost"]
            }
            
        except Exception as e:
            return {
                "case_analysis": f"Error in case law research: {str(e)}",
                "agent": "case_law_researcher",
                "error": str(e)
            }


# Global case law researcher instance
case_law_researcher_agent = CaseLawResearcherAgent()
