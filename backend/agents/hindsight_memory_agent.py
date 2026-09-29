import time
from typing import List, Dict, Any, Tuple
from backend.agents.context import AgentContext
from backend.services.hindsight_service import hindsight_service
from backend.models.schemas import MemoryItem

def run_hindsight_memory_agent(context: AgentContext) -> Tuple[List[MemoryItem], List[str]]:
    """
    Hindsight Memory Agent:
    1. Recalls relevant institutional precedents, past approved exceptions, and policies.
    2. Correlates recalled memories with detected clauses and risk items.
    3. Retains new contract insights into Hindsight memory for continuous learning.
    """
    companies = context.entities.company_names if context.entities else []
    doc_type = context.classification.document_type if context.classification else "Agreement"
    
    # 1. Build Multi-Angle Recall Query
    query_parts = []
    if companies:
        query_parts.append(f"Vendor {' '.join(companies)}")
    if context.clauses:
        clause_names = [c.name for c in context.clauses[:4]]
        query_parts.append(" ".join(clause_names))
    query_parts.append("liability indemnification payment terms termination")
    
    recall_query = " ".join(query_parts)
    print(f"[HINDSIGHT_AGENT] Querying Hindsight Memory Bank: '{recall_query[:80]}...'")
    
    raw_memories = hindsight_service.recall(recall_query, top_k=5)
    
    # Convert to MemoryItem models
    recalled_items: List[MemoryItem] = []
    for m in raw_memories:
        recalled_items.append(MemoryItem(
            id=m.get("id", "mem_unknown"),
            bank_id=m.get("bank_id", "docpilot-legal-bank"),
            category=m.get("category", "Precedent"),
            content=m.get("content", ""),
            tags=m.get("tags", []),
            source_doc=m.get("source_doc"),
            timestamp=m.get("timestamp", ""),
            confidence=m.get("confidence", 0.90),
            cloud_synced=m.get("cloud_synced", False)
        ))
        
    # 2. Correlate with Risks and Redlines
    memory_insights: List[str] = []
    
    # Check for specific company match (e.g. Acme Corp)
    is_acme = any("acme" in c.lower() for c in companies) or "acme" in context.filename.lower()
    
    for mem in recalled_items:
        tags = [t.lower() for t in mem.tags]
        
        # Check Liability Cap Precedent
        if ("liability" in tags or "acme corp" in tags) and is_acme:
            # Check if there is a liability risk in context
            if context.risk_flags:
                for rf in context.risk_flags:
                    if "liability" in rf.clause_name.lower() or "liability" in rf.category.lower():
                        rf.memory_reference = f"🧠 Hindsight Precedent: Approved 1x cap exception for Acme Corp ({mem.id})"
                        if rf.severity in ["Critical", "High"]:
                            rf.reasoning += f" [Note: Hindsight Memory recalls historical exception: {mem.content[:90]}...]"
            
            insight = f"🧠 Vendor Precedent Applied ({companies[0] if companies else 'Counterparty'}): Recalled historical 1x cap exception approved in {mem.source_doc or 'prior agreement'}."
            if insight not in memory_insights:
                memory_insights.append(insight)
                
        # Check Payment Terms Policy
        if "payment_terms" in tags or "finance" in tags:
            insight = f"🧠 Policy Alignment: Recalled Procurement Rule — Net-30/45 standard enforced across agreements."
            if insight not in memory_insights:
                memory_insights.append(insight)
                
        # Check Indemnification
        if "indemnification" in tags:
            insight = f"🧠 Compliance Rule: Recalled requirement for mutual IP indemnification standards."
            if insight not in memory_insights:
                memory_insights.append(insight)

    if not memory_insights:
        memory_insights.append(f"🧠 Hindsight Engine connected: Recalled {len(recalled_items)} corporate precedents for {doc_type} evaluation.")

    # 3. Retain current document learnings for future memory
    try:
        summary_snippet = (context.summary.business_overview if context.summary else "")[:150]
        counterparty_str = ", ".join(companies) if companies else "Unknown Party"
        retain_content = (
            f"Analyzed {doc_type} with {counterparty_str} (File: {context.filename}). "
            f"Risk Score: {context.decision.overall_risk_score if context.decision else 'N/A'}/100. "
            f"Identified {len(context.clauses or [])} clauses. Overview: {summary_snippet}"
        )
        hindsight_service.retain(
            content=retain_content,
            category="Contract Audit History",
            tags=companies + [doc_type, "Audit"],
            source_doc=context.filename
        )
    except Exception as e:
        print(f"[HINDSIGHT_AGENT] Retain warning: {e}")

    return recalled_items, memory_insights
