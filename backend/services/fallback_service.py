"""
fallback_service.py
-------------------
Generates a DOCUMENT-AWARE heuristic fallback response when Gemini API is
unavailable. Crucially, the hardcoded "sample document" data path has been
REMOVED — every fallback now reads from the actual document text so that
different documents produce meaningfully different outputs even without Gemini.

The old implementation had:
  1. A global IS_SAMPLE_RUN flag that never reset between requests
  2. Hardcoded Northfield/Brightwave data returned for ANY document once the
     flag was set, making every upload look identical

This version uses real regex + heuristic extraction on whatever text is passed.
"""
import re
import datetime
from typing import Any, List
from backend.models.schemas import (
    DocumentClassificationResult,
    EntityExtractionResult,
    ClauseItem,
    ClauseIntelligenceResult,
    RiskFlagItem,
    RiskIntelligenceResult,
    BusinessImpactItem,
    BusinessImpactResult,
    ComplianceItem,
    ComplianceResult,
    NegotiationItem,
    NegotiationResult,
    TimelineItem,
    ExecutiveSummaryResult,
    DecisionRecommendationResult,
    ChatResponse,
    Coordinate
)


# ---------------------------------------------------------------------------
# Heuristic helpers — these extract real information from document text
# ---------------------------------------------------------------------------

def _extract_doc_type(text: str) -> str:
    """Classify document type from keywords."""
    t = text.lower()
    if "master service agreement" in t or "msa" in t:
        return "Master Service Agreement"
    if "non-disclosure" in t or " nda " in t or "confidentiality agreement" in t:
        return "NDA"
    if "employment agreement" in t or "offer letter" in t or "employment contract" in t:
        return "Employment Agreement"
    if "lease agreement" in t or "rental agreement" in t or "tenancy" in t:
        return "Lease Agreement"
    if "purchase order" in t or "p.o. number" in t or "po number" in t:
        return "Purchase Order"
    if "invoice" in t and ("amount due" in t or "bill to" in t or "invoice number" in t):
        return "Invoice"
    if "receipt" in t and ("payment received" in t or "total paid" in t):
        return "Receipt"
    if "statement of work" in t or "sow" in t:
        return "Statement of Work"
    if "service agreement" in t or "services agreement" in t:
        return "Service Agreement"
    if "terms and conditions" in t or "terms of service" in t:
        return "Terms of Service"
    if "partnership agreement" in t:
        return "Partnership Agreement"
    if "amendment" in t and ("agreement" in t or "contract" in t):
        return "Contract Amendment"
    # Generic contract fallback
    if "agreement" in t or "contract" in t or "parties" in t:
        return "Contract"
    return "Business Document"


def _extract_companies(text: str) -> List[str]:
    """Extract company names using regex."""
    patterns = [
        r"([A-Z][A-Za-z0-9\s\,\.\-\&\']{2,60}\s(?:LLC|Pvt\.\s*Ltd\.|Ltd\.|Inc\.|Corp\.|Co\.|LLP|PLC|GmbH|S\.A\.))",
        r"(?:between|by and between|party[:\s]+)([A-Z][A-Za-z0-9\s\,\.\-\&\']{2,60}(?:LLC|Ltd|Inc|Corp|Co|LLP))",
    ]
    companies = []
    for pat in patterns:
        matches = re.findall(pat, text)
        for m in matches:
            name = m.strip().rstrip(",;.")
            if name and len(name) > 3 and name not in companies:
                companies.append(name)
    return companies[:5]


def _extract_date(text: str, pattern_hints: List[str]) -> str | None:
    """Try to extract a date matching pattern hints from text."""
    date_patterns = [
        r"\b(\d{4}-\d{2}-\d{2})\b",
        r"\b(\w+ \d{1,2},?\s+\d{4})\b",
        r"\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\b",
    ]
    for hint in pattern_hints:
        context_match = re.search(rf"(?:{hint})[\s:]*(.{{0,60}})", text, re.IGNORECASE)
        if context_match:
            context = context_match.group(1)
            for dp in date_patterns:
                dm = re.search(dp, context)
                if dm:
                    return dm.group(1)
    return None


def _extract_amount(text: str) -> str | None:
    """Extract a financial amount from text."""
    match = re.search(
        r"(\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?:\s*(?:USD|million|billion))?|\b\d{1,3}(?:,\d{3})*\s*(?:USD|INR|EUR|GBP)\b)",
        text
    )
    return match.group(1).strip() if match else None


def _extract_jurisdiction(text: str) -> str | None:
    """Extract governing jurisdiction from text."""
    match = re.search(
        r"governed by(?:\s+and\s+construed\s+in\s+accordance\s+with)?(?:\s+the)?\s+laws\s+of(?:\s+the\s+(?:State|Province|Country)\s+of)?\s+([A-Za-z\s]+?)[\.,\n]",
        text, re.IGNORECASE
    )
    if match:
        return match.group(1).strip()
    match = re.search(r"jurisdiction[:\s]+([A-Za-z\s]+?)[\.,\n]", text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def _extract_signatures(text: str) -> List[str]:
    """Extract signature block names from text."""
    sigs = []
    for match in re.finditer(r"(?:Authorized\s+(?:Signatory|Representative|By)|Signed\s+by)[:\s]+([A-Z][A-Za-z\s]{3,50})", text, re.IGNORECASE):
        name = match.group(1).strip()
        if name and name not in sigs:
            sigs.append(name)
    return sigs[:4]


def _extract_clauses_heuristic(text: str) -> List[ClauseItem]:
    """Extract clause sections by looking for numbered/titled sections."""
    clauses = []
    # Look for "Section N. Title" or "ARTICLE N. Title" patterns
    section_pattern = re.compile(
        r"(?:SECTION|ARTICLE|CLAUSE|SCHEDULE|EXHIBIT|SCHEDULE|§)\s*(\d+(?:\.\d+)?)[\.:\s]+([A-Z][^\n]{3,80})\n(.*?)(?=(?:SECTION|ARTICLE|CLAUSE|SCHEDULE|EXHIBIT|§)\s*\d|$)",
        re.IGNORECASE | re.DOTALL
    )
    for m in section_pattern.finditer(text):
        title = m.group(2).strip()
        body = m.group(3).strip()[:500]
        if len(body) > 30:
            clauses.append(ClauseItem(
                name=title[:60],
                verbatim_text=body,
                confidence=0.75,
                reasoning=f"Extracted from document section {m.group(1)}."
            ))
        if len(clauses) >= 10:
            break

    # Also detect key clause types by keyword
    keyword_clauses = {
        "Termination": ["terminat", "notice of terminat"],
        "Confidentiality": ["confidential", "non-disclosure"],
        "Payment Terms": ["payment", "invoice", "fee", "amount due"],
        "Limitation of Liability": ["limitation of liability", "liability cap", "in no event"],
        "Indemnification": ["indemnif", "hold harmless"],
        "Governing Law": ["governing law", "governed by", "jurisdiction"],
        "Force Majeure": ["force majeure", "act of god", "beyond reasonable control"],
        "Dispute Resolution": ["dispute", "arbitrat", "mediati"],
        "Auto-Renewal": ["auto.?renew", "automatic renewal", "automatically renew"],
        "Intellectual Property": ["intellectual property", "ip ownership", "work product"],
    }

    existing_names = {c.name.lower() for c in clauses}
    text_lower = text.lower()

    for clause_name, keywords in keyword_clauses.items():
        if clause_name.lower() in existing_names:
            continue
        for kw in keywords:
            idx = text_lower.find(kw)
            if idx != -1:
                snippet_start = max(0, idx - 20)
                snippet_end = min(len(text), idx + 600)
                snippet = text[snippet_start:snippet_end].strip()
                clauses.append(ClauseItem(
                    name=clause_name,
                    verbatim_text=snippet[:500],
                    confidence=0.70,
                    reasoning=f"Identified by keyword '{kw}' match in document."
                ))
                existing_names.add(clause_name.lower())
                break

    return clauses[:12]


def _extract_risks_heuristic(text: str, clauses: List[ClauseItem]) -> List[RiskFlagItem]:
    """Generate risk flags from clause content and document text."""
    risks = []
    text_lower = text.lower()

    risk_patterns = [
        {
            "keywords": ["in no event shall", "unlimited liability", "no cap", "fully liable for all"],
            "clause_name": "Limitation of Liability",
            "category": "Unlimited Liability",
            "severity": "Critical",
            "reasoning": "The liability clause does not cap damages, exposing the party to unlimited financial risk.",
            "suggested_action": "Negotiate a mutual liability cap (e.g., limited to fees paid in the preceding 12 months)."
        },
        {
            "keywords": ["100%", "all remaining fees", "entire remaining", "full remaining balance"],
            "clause_name": "Early Termination Penalty",
            "category": "Excessive Penalty",
            "severity": "High",
            "reasoning": "An early termination penalty of 100% of remaining fees is extremely punitive.",
            "suggested_action": "Negotiate to reduce early termination penalty to 2-3 months of service fees."
        },
        {
            "keywords": ["automatically renew", "auto-renew", "automatic renewal"],
            "clause_name": "Auto-Renewal",
            "category": "Lock-in Risk",
            "severity": "Medium",
            "reasoning": "Automatic renewal clauses create unintended lock-in if notice deadlines are missed.",
            "suggested_action": "Reduce the non-renewal notice period or add calendar reminders."
        },
        {
            "keywords": ["for any reason or no reason", "at any time", "sole discretion"],
            "clause_name": "Termination",
            "category": "One-sided Termination",
            "severity": "High",
            "reasoning": "One party has unrestricted termination rights while the other does not, creating an imbalanced agreement.",
            "suggested_action": "Add mutual termination for convenience with equal notice periods for both parties."
        },
        {
            "keywords": ["perpetual license", "irrevocable license", "worldwide license"],
            "clause_name": "Intellectual Property",
            "category": "IP Ownership Risk",
            "severity": "High",
            "reasoning": "Broad IP licensing terms may transfer critical intellectual property rights unintentionally.",
            "suggested_action": "Clarify IP ownership terms and limit license scope to agreed-upon use cases."
        },
        {
            "keywords": ["without limitation", "consequential damages", "indirect damages", "lost profits"],
            "clause_name": "Consequential Damages",
            "category": "Consequential Damages Exposure",
            "severity": "High",
            "reasoning": "Exposure to consequential or indirect damages (including lost profits) can lead to substantial financial liability.",
            "suggested_action": "Add mutual exclusion of consequential, indirect, and punitive damages."
        },
        {
            "keywords": ["unilateral", "sole right to modify", "amend at any time", "may change terms"],
            "clause_name": "Unilateral Modification",
            "category": "Unfair Contract Term",
            "severity": "Medium",
            "reasoning": "One-sided right to modify terms without consent undermines contractual certainty.",
            "suggested_action": "Require written mutual consent for any material changes to the agreement."
        },
        {
            "keywords": ["1.5%", "2% per month", "interest on late", "overdue interest"],
            "clause_name": "Late Payment Interest",
            "category": "High Interest Rate",
            "severity": "Low",
            "reasoning": "Monthly interest rates on late payments (e.g., 1.5%/month = 18%/year) increase financial risk for delayed payments.",
            "suggested_action": "Negotiate to a lower rate (e.g., 0.5%/month) or a fixed late fee."
        },
    ]

    for pattern in risk_patterns:
        for kw in pattern["keywords"]:
            if kw.lower() in text_lower:
                # Find verbatim text
                idx = text_lower.find(kw.lower())
                start = max(0, idx - 50)
                end = min(len(text), idx + 350)
                verbatim = text[start:end].strip()

                risks.append(RiskFlagItem(
                    clause_name=pattern["clause_name"],
                    category=pattern["category"],
                    severity=pattern["severity"],
                    text=verbatim,
                    reasoning=pattern["reasoning"],
                    suggested_action=pattern["suggested_action"],
                    confidence=0.78
                ))
                break  # Only one risk per pattern

    return risks


# ---------------------------------------------------------------------------
# Main dispatch function
# ---------------------------------------------------------------------------

def generate_smart_fallback(response_schema: Any, document_text: str, filename: str = "", force_sample: bool = False) -> Any:
    """
    Generates a document-AWARE heuristic response for the given schema
    based on actual document text analysis.

    IMPORTANT: The force_sample / IS_SAMPLE_RUN mechanism has been REMOVED.
    Every call now extracts real information from the provided document text,
    so different documents produce different outputs even without Gemini.
    """
    text = document_text or ""
    schema_name = getattr(response_schema, "__name__", str(response_schema))

    print(f"[FALLBACK] Generating heuristic fallback for schema: {schema_name} | Text length: {len(text)}")

    # ------------------------------------------------------------------
    if "DocumentClassificationResult" in schema_name:
        doc_type = _extract_doc_type(text)
        return DocumentClassificationResult(
            document_type=doc_type,
            confidence=0.82,
            reasoning=f"Heuristic classification as '{doc_type}' based on document structure and keyword analysis. Gemini API was unavailable for deep classification."
        )

    # ------------------------------------------------------------------
    elif "EntityExtractionResult" in schema_name:
        companies = _extract_companies(text)
        effective = _extract_date(text, ["effective as of", "effective date", "entered into as of", "dated", "commencing"])
        termination = _extract_date(text, ["terminat", "expir", "end date", "expires on"])
        renewal = _extract_date(text, ["renew", "renewal date", "auto.?renew"])
        amount = _extract_amount(text)
        jurisdiction = _extract_jurisdiction(text)
        signatures = _extract_signatures(text)

        # Duration
        duration_match = re.search(r"(?:initial\s+term|term\s+of)(?:\s+(?:this\s+agreement))?\s+(?:shall\s+be\s+|is\s+)?(\d+\s+(?:months?|years?))", text, re.IGNORECASE)
        duration = duration_match.group(1) if duration_match else None

        # Currency
        currency = None
        if "$" in text or "USD" in text:
            currency = "USD"
        elif "EUR" in text or "€" in text:
            currency = "EUR"
        elif "INR" in text or "₹" in text:
            currency = "INR"
        elif "GBP" in text or "£" in text:
            currency = "GBP"

        # Email / phone
        email_match = re.search(r"[\w\.\-]+@[\w\.\-]+\.\w+", text)
        phone_match = re.search(r"(?:\+\d{1,3}[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}", text)

        # Invoice / PO numbers
        inv_match = re.search(r"invoice\s*(?:no|number|#)[\.:\s]*([A-Z0-9\-]+)", text, re.IGNORECASE)
        po_match = re.search(r"(?:purchase\s+order|p\.?o\.?)\s*(?:no|number|#)[\.:\s]*([A-Z0-9\-]+)", text, re.IGNORECASE)

        return EntityExtractionResult(
            company_names=companies or ["Unknown Party A", "Unknown Party B"],
            person_names=[],
            addresses=[],
            effective_date=effective,
            termination_date=termination,
            renewal_date=renewal,
            contract_duration=duration,
            payment_amount=amount,
            currency=currency,
            tax_details=None,
            email=email_match.group(0) if email_match else None,
            phone=phone_match.group(0) if phone_match else None,
            jurisdiction=jurisdiction or "Not Specified",
            signatures_found=signatures,
            invoice_number=inv_match.group(1) if inv_match else None,
            purchase_order_number=po_match.group(1) if po_match else None,
            due_date=None,
            reasoning=f"Heuristic extraction from document text. Found {len(companies)} companies, dates, and jurisdiction. Gemini API was unavailable."
        )

    # ------------------------------------------------------------------
    elif "ClauseIntelligenceResult" in schema_name:
        clauses = _extract_clauses_heuristic(text)
        if not clauses:
            # Ultimate fallback: grab opening text as a single clause
            clauses = [ClauseItem(
                name="Document Header / Opening",
                verbatim_text=text[:400].strip(),
                confidence=0.60,
                reasoning="No structured clauses detected. Returned opening text."
            )]
        return ClauseIntelligenceResult(clauses=clauses)

    # ------------------------------------------------------------------
    elif "RiskIntelligenceResult" in schema_name:
        # Extract clauses first if not embedded in prompt context
        risks = _extract_risks_heuristic(text, [])
        return RiskIntelligenceResult(risk_flags=risks)

    # ------------------------------------------------------------------
    elif "BusinessImpactResult" in schema_name:
        # Build impact based on keywords found in prompt/text — include verbatim snippets
        impacts = []
        text_lower = text.lower()

        def _get_snippet(keyword: str, window: int = 150) -> str:
            idx = text_lower.find(keyword)
            if idx == -1:
                return ""
            start = max(0, idx - 30)
            end = min(len(text), idx + window)
            return f' Context: "...{text[start:end].strip()}..."'

        if "critical" in text_lower or "unlimited liability" in text_lower:
            snippet = _get_snippet("unlimited liability") or _get_snippet("critical")
            impacts.append(BusinessImpactItem(
                priority="Critical",
                exposure="High",
                explanation=f"Uncapped liability exposure puts the organization's entire asset base at risk for any service failure or breach claim.{snippet}"
            ))
        if "terminat" in text_lower and ("15 days" in text_lower or "for any reason" in text_lower):
            snippet = _get_snippet("for any reason") or _get_snippet("15 days")
            impacts.append(BusinessImpactItem(
                priority="High",
                exposure="High",
                explanation=f"Short or one-sided termination rights could cause sudden service disruption with minimal transition runway.{snippet}"
            ))
        if "penalty" in text_lower or "early termination" in text_lower:
            snippet = _get_snippet("early termination") or _get_snippet("penalty")
            impacts.append(BusinessImpactItem(
                priority="High",
                exposure="Medium",
                explanation=f"Early termination penalties restrict operational flexibility and increase switching costs significantly.{snippet}"
            ))
        if "auto" in text_lower and "renew" in text_lower:
            snippet = _get_snippet("auto") or _get_snippet("renew")
            impacts.append(BusinessImpactItem(
                priority="Medium",
                exposure="Low",
                explanation=f"Automatic renewal clauses can lock the organization into an agreement for an additional term if notice deadlines are missed.{snippet}"
            ))
        # Check for financial exposure
        amount = _extract_amount(text)
        if amount and not impacts:
            impacts.append(BusinessImpactItem(
                priority="Medium",
                exposure="Medium",
                explanation=f"Financial commitment of {amount} identified. Review payment obligations, late fees, and refund policy carefully before signing."
            ))
        if not impacts:
            impacts.append(BusinessImpactItem(
                priority="Low",
                exposure="Low",
                explanation="No severe risk clauses detected in heuristic scan. A full Gemini-powered analysis is recommended for a complete assessment."
            ))
        return BusinessImpactResult(business_impact=impacts)


    # ------------------------------------------------------------------
    elif "ComplianceResult" in schema_name:
        text_lower = text.lower()
        clauses_to_check = [
            ("Force Majeure", ["force majeure", "act of god", "beyond.*reasonable control"]),
            ("Termination Notice", ["terminat.*notice", "notice.*terminat"]),
            ("Confidentiality", ["confidential", "non-disclosure"]),
            ("Data Privacy", ["data privacy", "gdpr", "personal data", "data protection"]),
            ("Intellectual Property", ["intellectual property", "ip ownership", "work product", "proprietary"]),
            ("Payment Terms", ["payment", "invoice", "fee schedule", "amount due"]),
            ("Dispute Resolution", ["dispute resolution", "arbitrat", "mediati", "litigation"]),
            ("Governing Law", ["governing law", "governed by", "jurisdiction"]),
        ]

        missing = []
        for clause_name, keywords in clauses_to_check:
            found = any(re.search(kw, text_lower) for kw in keywords)
            missing.append(ComplianceItem(
                clause_name=clause_name,
                is_present=found,
                status="Compliant" if found else "Non-compliant",
                recommendation="" if found else f"Add a standard {clause_name} clause to ensure full contractual compliance."
            ))
        return ComplianceResult(missing_clauses=missing)

    # ------------------------------------------------------------------
    elif "NegotiationResult" in schema_name:
        # Extract risks from the prompt text (which contains risk context)
        suggestions = []
        text_lower = text.lower()

        if "unlimited liability" in text_lower or "in no event shall" in text_lower:
            suggestions.append(NegotiationItem(
                clause_name="Limitation of Liability",
                current_clause="[Detected: Unlimited or uncapped liability clause]",
                suggested_clause="EXCEPT FOR LIABILITY ARISING FROM A PARTY'S GROSS NEGLIGENCE OR WILLFUL MISCONDUCT, EACH PARTY'S TOTAL LIABILITY UNDER THIS AGREEMENT SHALL BE LIMITED TO THE TOTAL FEES PAID BY CLIENT TO VENDOR IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM.",
                reason="Introduces a standard mutual liability cap protecting both parties from existential financial risk.",
                risk_reduction="Critical → Low"
            ))

        if "for any reason or no reason" in text_lower or "at any time" in text_lower:
            suggestions.append(NegotiationItem(
                clause_name="Termination",
                current_clause="[Detected: One-sided or short-notice termination right]",
                suggested_clause="Either party may terminate this Agreement for convenience upon sixty (60) days prior written notice to the other party.",
                reason="Establishes mutual termination rights and extends notice time to ensure adequate transition runway.",
                risk_reduction="High → Low"
            ))

        if "100%" in text_lower and ("remaining" in text_lower or "penalty" in text_lower):
            suggestions.append(NegotiationItem(
                clause_name="Early Termination Penalty",
                current_clause="[Detected: 100% early termination penalty on remaining fees]",
                suggested_clause="Upon early termination for convenience, the terminating party shall pay a fee equal to three (3) months of the monthly service fee as the sole and exclusive remedy.",
                reason="Reduces the severe financial penalty and provides a predictable and proportional exit fee structure.",
                risk_reduction="High → Medium"
            ))

        return NegotiationResult(negotiation_suggestions=suggestions)

    # ------------------------------------------------------------------
    elif "ExecutiveSummaryResult" in schema_name:
        doc_type = _extract_doc_type(text)
        companies = _extract_companies(text)
        amount = _extract_amount(text)
        jurisdiction = _extract_jurisdiction(text)
        effective = _extract_date(text, ["effective as of", "effective date", "dated"])
        termination = _extract_date(text, ["terminat", "expir", "end date"])

        parties_str = " and ".join(companies[:2]) if companies else "the contracting parties"
        amount_str = f" with a financial obligation of {amount}" if amount else ""
        jurisdiction_str = f" Governed by the laws of {jurisdiction}." if jurisdiction else ""

        overview = (
            f"This {doc_type} establishes a formal relationship between {parties_str}{amount_str}."
            f"{jurisdiction_str} The document defines the rights, obligations, and operational terms "
            f"governing the arrangement between the parties."
        )

        key_findings = []
        if jurisdiction:
            key_findings.append(f"Governing law: {jurisdiction} — provides legal predictability.")
        if amount:
            key_findings.append(f"Financial obligation: {amount} — defined payment structure.")
        if re.search(r"confidential", text, re.IGNORECASE):
            key_findings.append("Confidentiality obligations are present in the agreement.")
        if not key_findings:
            key_findings.append("Document defines standard business terms between the parties.")

        major_risks = []
        if re.search(r"unlimited liability|in no event shall.*limited", text, re.IGNORECASE):
            major_risks.append("Potentially uncapped liability exposure detected.")
        if re.search(r"for any reason or no reason|at any time.*terminat", text, re.IGNORECASE):
            major_risks.append("One-sided termination rights may create operational disruption risk.")
        if re.search(r"auto.?renew|automatically renew", text, re.IGNORECASE):
            major_risks.append("Auto-renewal clause may lead to unintended contract extensions.")

        # Critical dates
        critical_dates = []
        if effective:
            critical_dates.append(TimelineItem(date=effective, event="Effective Date / Commencement"))
        if termination:
            critical_dates.append(TimelineItem(date=termination, event="Contract Expiry / Termination Date"))

        financial_summary = f"Financial obligation: {amount}." if amount else "Financial terms present in the document (exact amount parsing requires Gemini analysis)."

        recommended_actions = [
            "Conduct a full legal review of all liability and termination clauses.",
            "Verify all party names, dates, and payment amounts against source documents.",
        ]
        if major_risks:
            recommended_actions.insert(0, "Prioritize renegotiation of flagged high-risk clauses before signing.")

        return ExecutiveSummaryResult(
            business_overview=overview,
            key_findings=key_findings,
            major_risks=major_risks,
            critical_dates=critical_dates,
            financial_summary=financial_summary,
            recommended_actions=recommended_actions
        )

    # ------------------------------------------------------------------
    elif "DecisionRecommendationResult" in schema_name:
        text_lower = text.lower()

        critical_count = text_lower.count("critical")
        high_count = text_lower.count("[high]") + text_lower.count("severity: high")
        has_unlimited_liability = "unlimited liability" in text_lower or "in no event shall" in text_lower
        has_one_sided_termination = "for any reason or no reason" in text_lower

        # Calculate a document-aware risk score
        risk_score = 30  # baseline
        if has_unlimited_liability:
            risk_score += 30
        if has_one_sided_termination:
            risk_score += 15
        if "100%" in text and "penalty" in text_lower:
            risk_score += 15
        if critical_count > 0:
            risk_score += min(critical_count * 5, 20)
        risk_score = min(risk_score, 95)

        if risk_score >= 70:
            decision = "Proceed after Negotiation"
            reasoning = f"The document contains high-risk clauses (risk score: {risk_score}/100) that require renegotiation before signing. Key concerns include potential liability exposure and imbalanced termination terms."
        elif risk_score >= 45:
            decision = "Requires Legal Review"
            reasoning = f"The document contains moderate to high risk elements (risk score: {risk_score}/100) that require professional legal evaluation before execution."
        elif risk_score >= 20:
            decision = "Proceed after Negotiation"
            reasoning = f"The document is generally acceptable (risk score: {risk_score}/100) but contains some clauses that should be reviewed and potentially renegotiated."
        else:
            decision = "Proceed"
            reasoning = f"The document appears to contain standard, balanced terms (risk score: {risk_score}/100). Recommend a standard legal sign-off before execution."

        return DecisionRecommendationResult(
            decision=decision,
            reasoning=reasoning,
            overall_risk_score=risk_score
        )

    # ------------------------------------------------------------------
    elif "ChatResponse" in schema_name:
        # Context-aware chat fallback
        text_lower = text.lower()

        if "liability" in text_lower and "limit" in text_lower:
            idx = text_lower.find("liability")
            snippet = text[max(0, idx-20):idx+300].strip()
            return ChatResponse(
                answer=f"The document contains a liability clause. Based on heuristic analysis: {snippet[:200]}...",
                confidence=0.60,
                reasoning="Matched liability keyword in document text — Gemini API unavailable for deep analysis.",
                evidence=[snippet[:100]]
            )
        return ChatResponse(
            answer="I can see this document but full conversational AI analysis requires Gemini API access. Please ensure your API key is valid and has available quota.",
            confidence=0.40,
            reasoning="Gemini API unavailable — returning basic heuristic response.",
            evidence=[]
        )

    # ------------------------------------------------------------------
    # Generic unknown schema — return empty schema instance
    return response_schema()
