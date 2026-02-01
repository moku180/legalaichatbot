"""Statutory Interpretation Agent - Interprets laws and statutes"""
from typing import Dict, Any, List
from app.agents.prompts import STATUTORY_INTERPRETATION_PROMPT
from app.services.llm_service import llm_service


class StatutoryInterpreterAgent:
    """Agent for interpreting statutes, acts, and legal provisions"""
    
    def __init__(self):
        self.system_prompt = STATUTORY_INTERPRETATION_PROMPT
    
    async def interpret_statute(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Interpret statutory provisions
        
        Args:
            query: User query about statute
            retrieved_chunks: Retrieved legal text chunks
        
        Returns:
            Dict with interpretation, citations, jurisdiction
        """
        # Format context from retrieved chunks
        if retrieved_chunks:
            context = "\n\n".join([
                f"Legal Text:\n{chunk.get('text', '')}\n"
                f"Source: {chunk.get('metadata', {}).get('title', 'Unknown')}\n"
                f"Jurisdiction: {chunk.get('metadata', {}).get('jurisdiction', 'Unknown')}"
                for chunk in retrieved_chunks[:3]
            ])
        else:
            context = "No specific documents found. Please use your general legal knowledge to answer."
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
User Query: {query}

Relevant Legal Provisions:
{context}

Provide:
1. The exact legal text (if available from documents)
2. Plain-language interpretation combining document info (if any) with general legal knowledge
3. Key terms explained
4. Cross-references if any
5. Proper citations (if documents provided)

Be clear, educational, and combine both document-specific and general legal knowledge.
"""}
        ]
        
        try:
            response = await llm_service.chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=1500
            )
            
            return {
                "interpretation": response["content"],
                "agent": "statutory_interpreter",
                "tokens_used": response["total_tokens"],
                "cost": response["cost"]
            }
            
        except Exception as e:
            return {
                "interpretation": f"Error in statutory interpretation: {str(e)}",
                "agent": "statutory_interpreter",
                "error": str(e)
            }


# Global statutory interpreter instance
statutory_interpreter_agent = StatutoryInterpreterAgent()
