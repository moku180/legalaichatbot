"""Orchestrator Agent - Routes queries to appropriate specialist agents"""
import json
from typing import Dict, Any, List
from app.agents.prompts import ORCHESTRATOR_PROMPT
from app.services.llm_service import llm_service


class OrchestratorAgent:
    """Agent for intent classification and routing"""
    
    def __init__(self):
        self.system_prompt = ORCHESTRATOR_PROMPT
    
    async def classify_intent(self, query: str) -> Dict[str, Any]:
        """
        Classify user intent and determine which agents to call
        
        Args:
            query: User query
        
        Returns:
            Dict with intent, agents_to_call, confidence, reasoning
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
Classify this legal query:

Query: {query}

Determine:
1. Primary intent category
2. Which specialist agents should handle this
3. Your confidence in the classification
4. Brief reasoning

Respond with JSON only.
"""}
        ]
        
        try:
            response = await llm_service.chat_completion(
                messages=messages,
                temperature=0.0,
                max_tokens=300
            )
            
            content = response["content"]
            
            # Extract JSON
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
            
            classification = json.loads(json_str)
            
            # Always include verification and safety agents
            agents = classification.get("agents_to_call", [])
            if "verification" not in [a.lower() for a in agents]:
                agents.append("verification")
            if "safety" not in [a.lower() for a in agents]:
                agents.append("safety")
            
            classification["agents_to_call"] = agents
            
            return classification
            
        except Exception as e:
            # Default classification on error
            return {
                "intent": "general_legal",
                "agents_to_call": ["retriever", "verification", "safety"],
                "confidence": 0.5,
                "reasoning": f"Classification failed: {str(e)}. Using default routing."
            }
    
    def get_agent_priority(self, intent: str) -> List[str]:
        """Get ordered list of agents based on intent"""
        priority_map = {
            "statutory_interpretation": ["retriever", "statutory_interpreter", "verification", "safety"],
            "case_law_research": ["retriever", "case_law_researcher", "verification", "safety"],
            "contract_analysis": ["contract_analyzer", "verification", "safety"],
            "compliance_check": ["retriever", "compliance_agent", "verification", "safety"],
            "general_legal": ["retriever", "verification", "safety"]
        }
        
        return priority_map.get(intent, ["retriever", "verification", "safety"])


# Global orchestrator instance
orchestrator_agent = OrchestratorAgent()
