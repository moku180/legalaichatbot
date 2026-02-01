"""Legal chat API with multi-agent system"""
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.core.dependencies import get_current_user, get_current_organization
from app.models.user import User
from app.models.organization import Organization
from app.models.query_history import QueryHistory
from app.api.schemas import ChatQuery, ChatResponse, Citation
from app.agents.orchestrator import orchestrator_agent
from app.agents.safety_agent import safety_agent
from app.agents.verification_agent import verification_agent
from app.agents.retriever import retriever_agent
from app.agents.statutory_interpreter import statutory_interpreter_agent
from app.agents.case_law_researcher import case_law_researcher_agent
from app.agents.contract_analyzer import contract_analyzer_agent
from app.agents.compliance_agent import compliance_agent


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/query", response_model=ChatResponse)
async def submit_query(
    query_data: ChatQuery,
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Submit legal query and get AI-powered response"""
    
    start_time = time.time()
    
    # Step 1: Safety check
    safety_result = await safety_agent.check_safety(
        query=query_data.query,
        jurisdiction=query_data.jurisdiction
    )
    
    if safety_agent.should_refuse(safety_result):
        # Refuse the request
        return ChatResponse(
            query_id=0,
            query=query_data.query,
            response=f"Request refused: {safety_result['reason']}\n\n{safety_result['suggested_action']}",
            intent="refused",
            agents_used=["safety"],
            citations=[],
            confidence_score=0.0,
            safety_check=safety_result["safety_check"],
            disclaimer=safety_result["disclaimer_text"],
            tokens_used=0,
            cost_estimate=0.0,
            response_time_ms=int((time.time() - start_time) * 1000)
        )
    
    # Step 2: Intent classification
    classification = await orchestrator_agent.classify_intent(query_data.query)
    
    # Step 3: Retrieve relevant documents
    retrieved_chunks = await retriever_agent.retrieve_with_mmr(
        organization_id=organization.id,
        query=query_data.query,
        jurisdiction=query_data.jurisdiction,
        top_k=5
    )
    
    # Step 4: Route to appropriate specialist agent
    intent = classification.get("intent", "general_legal")
    response_text = ""
    total_tokens = 0
    total_cost = 0.0
    agents_used = ["orchestrator", "safety", "retriever"]
    
    # Always pass retrieved_chunks to agents (even if empty) so they can combine with general knowledge
    if intent == "statutory_interpretation":
        result = await statutory_interpreter_agent.interpret_statute(
            query=query_data.query,
            retrieved_chunks=retrieved_chunks  # Pass even if empty
        )
        response_text = result.get("interpretation", "")
        total_tokens += result.get("tokens_used", 0)
        total_cost += result.get("cost", 0.0)
        agents_used.append("statutory_interpreter")
        
    elif intent == "case_law_research":
        result = await case_law_researcher_agent.research_case_law(
            query=query_data.query,
            retrieved_chunks=retrieved_chunks  # Pass even if empty
        )
        response_text = result.get("case_analysis", "")
        total_tokens += result.get("tokens_used", 0)
        total_cost += result.get("cost", 0.0)
        agents_used.append("case_law_researcher")
        
    elif intent == "contract_analysis":
        result = await contract_analyzer_agent.analyze_contract(
            query=query_data.query,
            contract_text=query_data.query  # Assume query contains contract
        )
        response_text = result.get("contract_analysis", "")
        total_tokens += result.get("tokens_used", 0)
        total_cost += result.get("cost", 0.0)
        agents_used.append("contract_analyzer")
        
    elif intent == "compliance_check":
        result = await compliance_agent.check_compliance(
            query=query_data.query,
            retrieved_chunks=retrieved_chunks  # Pass even if empty
        )
        response_text = result.get("compliance_analysis", "")
        total_tokens += result.get("tokens_used", 0)
        total_cost += result.get("cost", 0.0)
        agents_used.append("compliance_agent")
    else:
        # Hybrid approach: ALWAYS combine documents with general knowledge
        from app.agents.prompts import HYBRID_LEGAL_PROMPT
        from app.services.llm_service import llm_service
        
        # Build context from retrieved documents (if any)
        context = ""
        if retrieved_chunks:
            context = "\n\n--- RELEVANT DOCUMENTS ---\n\n"
            context += "\n\n".join([f"Document: {chunk['metadata'].get('title', 'Unknown')}\n{chunk['text']}" 
                                     for chunk in retrieved_chunks[:3]])
            context += "\n\n--- END DOCUMENTS ---\n\n"
        
        # Always use hybrid legal agent to combine document info with general knowledge
        hybrid_response = await llm_service.chat_completion(
            messages=[
                {"role": "system", "content": HYBRID_LEGAL_PROMPT},
                {"role": "user", "content": f"{context}\n\nUser Query: {query_data.query}\n\nPlease answer by combining information from the provided documents (if any) with relevant general legal knowledge to give a comprehensive response."}
            ],
            temperature=0.3
        )
        response_text = hybrid_response.get("content", "")
        total_tokens += hybrid_response.get("total_tokens", 0)
        total_cost += hybrid_response.get("cost", 0.0)
        agents_used.append("hybrid_legal_agent")
    
    # Step 5: Verification
    verification = await verification_agent.verify_response(
        query=query_data.query,
        response=response_text,
        retrieved_chunks=retrieved_chunks
    )
    agents_used.append("verification")
    
    # Step 6: Add disclaimer
    final_response = f"{response_text}\n\n---\n\n{safety_result['disclaimer_text']}"
    
    # Step 7: Extract citations
    citations = [
        Citation(
            source=chunk["metadata"].get("title", "Unknown"),
            text=chunk["text"][:200] + "...",
            metadata=chunk["metadata"]
        )
        for chunk in retrieved_chunks[:3]
    ] if query_data.include_citations else []
    
    # Step 8: Save to query history
    query_history = QueryHistory(
        organization_id=organization.id,
        user_id=current_user.id,
        query=query_data.query,
        response=final_response,
        intent_classification=intent,
        agents_used=agents_used,
        citations=[c.dict() for c in citations],
        confidence_score=verification.get("confidence_score", 0.0),
        total_tokens=total_tokens,
        cost_estimate=total_cost,
        response_time_ms=int((time.time() - start_time) * 1000),
        safety_triggered=safety_result.get("safety_check") if safety_result.get("safety_check") != "PASS" else None
    )
    db.add(query_history)
    await db.commit()
    await db.refresh(query_history)
    
    return ChatResponse(
        query_id=query_history.id,
        query=query_data.query,
        response=final_response,
        intent=intent,
        agents_used=agents_used,
        citations=citations,
        confidence_score=verification.get("confidence_score", 0.0),
        safety_check=safety_result["safety_check"],
        disclaimer=safety_result["disclaimer_text"],
        tokens_used=total_tokens,
        cost_estimate=total_cost,
        response_time_ms=int((time.time() - start_time) * 1000)
    )
