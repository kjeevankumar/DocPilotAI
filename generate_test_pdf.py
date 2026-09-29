"""
generate_test_pdf.py
Generates a realistic 25+ page Software Development & Services Agreement PDF
designed to exercise every feature of the DocPilot AI Intelligent Document Analyzer:
  - Classification / document type detection
  - Entity extraction (companies, persons, jurisdictions, dates, monetary amounts)
  - Clause inspection (indemnification, liability, IP, termination, NDA, etc.)
  - Risk register (Critical, High, Medium, Low risks)
  - Compliance & missing clauses audit
  - Negotiation suggestions
  - Business impact analysis
  - Executive summary
  - AI Q&A chat
  - Timeline / key dates
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors

OUTPUT_PATH = "DocPilot_Test_Agreement.pdf"

# ─── Colour palette ──────────────────────────────────────────────────────────
DARK_NAVY   = HexColor("#0D1B2A")
MID_BLUE    = HexColor("#1B3A5C")
ACCENT_BLUE = HexColor("#2E6DA4")
LIGHT_GREY  = HexColor("#F4F6F9")
MID_GREY    = HexColor("#C8D0DB")
TEXT_GREY   = HexColor("#4A5568")
RED_RISK    = HexColor("#C53030")
AMBER_RISK  = HexColor("#B7791F")
GREEN_OK    = HexColor("#276749")
WHITE       = white
BLACK       = black

# ─── Styles ──────────────────────────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()

    styles = {
        "cover_title": ParagraphStyle(
            "cover_title", fontSize=28, textColor=WHITE,
            fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=10
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", fontSize=13, textColor=MID_GREY,
            fontName="Helvetica", alignment=TA_CENTER, spaceAfter=6
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta", fontSize=10, textColor=MID_GREY,
            fontName="Helvetica-Oblique", alignment=TA_CENTER, spaceAfter=4
        ),
        "h1": ParagraphStyle(
            "h1", fontSize=15, textColor=DARK_NAVY,
            fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=6,
            borderPad=4
        ),
        "h2": ParagraphStyle(
            "h2", fontSize=12, textColor=ACCENT_BLUE,
            fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=4
        ),
        "h3": ParagraphStyle(
            "h3", fontSize=10.5, textColor=MID_BLUE,
            fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=3
        ),
        "body": ParagraphStyle(
            "body", fontSize=9.5, textColor=TEXT_GREY,
            fontName="Helvetica", leading=15, spaceBefore=3,
            spaceAfter=4, alignment=TA_JUSTIFY
        ),
        "body_bold": ParagraphStyle(
            "body_bold", fontSize=9.5, textColor=BLACK,
            fontName="Helvetica-Bold", leading=15, spaceBefore=2, spaceAfter=3
        ),
        "list_item": ParagraphStyle(
            "list_item", fontSize=9.5, textColor=TEXT_GREY,
            fontName="Helvetica", leading=14, leftIndent=18,
            bulletIndent=6, spaceBefore=2, spaceAfter=2
        ),
        "clause_num": ParagraphStyle(
            "clause_num", fontSize=9.5, textColor=ACCENT_BLUE,
            fontName="Helvetica-Bold", leading=14, leftIndent=0
        ),
        "sub_clause": ParagraphStyle(
            "sub_clause", fontSize=9.5, textColor=TEXT_GREY,
            fontName="Helvetica", leading=14, leftIndent=24,
            spaceBefore=2, spaceAfter=2, alignment=TA_JUSTIFY
        ),
        "footer_note": ParagraphStyle(
            "footer_note", fontSize=7.5, textColor=MID_GREY,
            fontName="Helvetica-Oblique", alignment=TA_CENTER
        ),
        "risk_critical": ParagraphStyle(
            "risk_critical", fontSize=9, textColor=RED_RISK,
            fontName="Helvetica-Bold", leading=13
        ),
        "risk_amber": ParagraphStyle(
            "risk_amber", fontSize=9, textColor=AMBER_RISK,
            fontName="Helvetica-Bold", leading=13
        ),
    }
    return styles

# ─── Helper builders ─────────────────────────────────────────────────────────
def section_rule(story):
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=MID_GREY, spaceAfter=6, spaceBefore=2))

def clause(story, styles, number, title, paras, sub=False):
    story.append(Paragraph(f"{number}  {title.upper()}", styles["h2"]))
    for p in paras:
        story.append(Paragraph(p, styles["body"]))
    story.append(Spacer(1, 4))

def sub_clause(story, styles, ref, text):
    story.append(Paragraph(f"<b>{ref}</b>  {text}", styles["sub_clause"]))


def risk_table(story, styles, rows):
    """rows = list of (Category, Severity, Description)"""
    data = [["#", "Category", "Severity", "Trigger / Description"]]
    for i, (cat, sev, desc) in enumerate(rows, 1):
        data.append([str(i), cat, sev, desc])

    sev_colors = {
        "Critical": RED_RISK, "High": HexColor("#C05621"),
        "Medium": AMBER_RISK, "Low": GREEN_OK
    }

    table = Table(data, colWidths=[0.5*cm, 3.5*cm, 2*cm, 11.5*cm])
    ts = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK_NAVY),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_GREY, WHITE]),
        ("FONTSIZE",   (0, 1), (-1, -1), 8),
        ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
        ("TEXTCOLOR",  (0, 1), (-1, -1), TEXT_GREY),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("GRID",       (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ])
    for i, (_, sev, _) in enumerate(rows, 1):
        c = sev_colors.get(sev, TEXT_GREY)
        ts.add("TEXTCOLOR", (2, i), (2, i), c)
        ts.add("FONTNAME",  (2, i), (2, i), "Helvetica-Bold")
    table.setStyle(ts)
    story.append(table)
    story.append(Spacer(1, 8))


def entity_table(story, styles, rows):
    """rows = list of (Type, Value)"""
    data = [["Entity Type", "Extracted Value"]]
    data += rows
    table = Table(data, colWidths=[4*cm, 13.5*cm])
    ts = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), MID_BLUE),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_GREY, WHITE]),
        ("FONTSIZE",   (0, 1), (-1, -1), 8.5),
        ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
        ("TEXTCOLOR",  (0, 1), (-1, -1), TEXT_GREY),
        ("GRID",       (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ])
    table.setStyle(ts)
    story.append(table)
    story.append(Spacer(1, 8))


def compliance_table(story, styles, rows):
    """rows = list of (Clause Name, Status, Notes)"""
    data = [["Standard Provision", "Status", "Notes / Gap Analysis"]]
    data += rows
    table = Table(data, colWidths=[4.5*cm, 2*cm, 11*cm])
    ts = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK_NAVY),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_GREY, WHITE]),
        ("FONTSIZE",   (0, 1), (-1, -1), 8),
        ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
        ("TEXTCOLOR",  (0, 1), (-1, -1), TEXT_GREY),
        ("GRID",       (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
    ])
    for i, (_, status, _) in enumerate(rows, 1):
        c = GREEN_OK if status == "Present" else RED_RISK
        ts.add("TEXTCOLOR", (1, i), (1, i), c)
        ts.add("FONTNAME",  (1, i), (1, i), "Helvetica-Bold")
    table.setStyle(ts)
    story.append(table)
    story.append(Spacer(1, 8))


# ─── Cover Page ──────────────────────────────────────────────────────────────
def build_cover(story, styles):
    # Full-width navy background simulation via a coloured table
    cover_data = [[""]]
    cover_table = Table(cover_data, colWidths=[17.5*cm], rowHeights=[5*cm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_NAVY),
    ]))

    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("SOFTWARE DEVELOPMENT &amp; SERVICES AGREEMENT", styles["cover_title"]))
    story.append(Paragraph("Enterprise Engagement — Version 3.2 (Final Draft)", styles["cover_sub"]))
    story.append(HRFlowable(width="60%", thickness=1.5, color=ACCENT_BLUE,
                             spaceAfter=10, spaceBefore=6))
    story.append(Paragraph("Between:", styles["cover_meta"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "<b>NovaTech Solutions Pvt. Ltd.</b>  (Service Provider)",
        ParagraphStyle("cp1", fontSize=13, textColor=DARK_NAVY,
                       fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
    ))
    story.append(Paragraph(
        "Registered Office: 42 Rajiv Gandhi IT Park, Pune, Maharashtra 411057, India",
        ParagraphStyle("cp2", fontSize=9.5, textColor=TEXT_GREY,
                       fontName="Helvetica", alignment=TA_CENTER, spaceAfter=12)
    ))
    story.append(Paragraph("—  AND  —",
        ParagraphStyle("and", fontSize=10, textColor=MID_GREY,
                       fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=12)
    ))
    story.append(Paragraph(
        "<b>GlobalEdge Corp.</b>  (Client)",
        ParagraphStyle("cp3", fontSize=13, textColor=DARK_NAVY,
                       fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
    ))
    story.append(Paragraph(
        "Principal Office: 1600 Amphitheatre Parkway, Mountain View, CA 94043, USA",
        ParagraphStyle("cp4", fontSize=9.5, textColor=TEXT_GREY,
                       fontName="Helvetica", alignment=TA_CENTER, spaceAfter=20)
    ))
    story.append(HRFlowable(width="40%", thickness=0.5, color=MID_GREY,
                             spaceAfter=10, spaceBefore=4))

    meta = [
        ["Effective Date", ":", "15 September 2025"],
        ["Contract No.",   ":", "GEC-NTS-2025-0917"],
        ["Version",        ":", "3.2 — Final Draft for Legal Approval"],
        ["Prepared By",    ":", "Ms. Priya Sharma, LLB (NovaTech Legal)"],
        ["Reviewed By",    ":", "Mr. David Chen, JD (GlobalEdge General Counsel)"],
        ["Governing Law",  ":", "State of California, United States of America"],
        ["Jurisdiction",   ":", "Superior Court of Santa Clara County, California"],
        ["Total Value",    ":", "USD 4,200,000  (Four Million Two Hundred Thousand)"],
        ["Contract Term",  ":", "36 months from Effective Date"],
    ]
    meta_table = Table(meta, colWidths=[3.5*cm, 0.5*cm, 12*cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",   (2, 0), (2, -1), "Helvetica"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR",  (0, 0), (-1, -1), TEXT_GREY),
        ("TEXTCOLOR",  (0, 0), (0, -1), DARK_NAVY),
        ("TOPPADDING",   (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 3),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph(
        "CONFIDENTIAL — ATTORNEY-CLIENT PRIVILEGE — NOT FOR DISTRIBUTION",
        ParagraphStyle("conf", fontSize=8, textColor=RED_RISK,
                       fontName="Helvetica-Bold", alignment=TA_CENTER)
    ))
    story.append(PageBreak())


# ─── Table of Contents ───────────────────────────────────────────────────────
def build_toc(story, styles):
    story.append(Paragraph("TABLE OF CONTENTS", styles["h1"]))
    section_rule(story)
    toc = [
        ("1.", "Definitions and Interpretation", "3"),
        ("2.", "Scope of Services and Deliverables", "4"),
        ("3.", "Project Timeline and Milestones", "5"),
        ("4.", "Fees, Payment Terms, and Invoicing", "6"),
        ("5.", "Intellectual Property Rights", "7"),
        ("6.", "Confidentiality and Non-Disclosure", "8"),
        ("7.", "Data Protection and Privacy", "9"),
        ("8.", "Warranties and Representations", "10"),
        ("9.", "Indemnification", "11"),
        ("10.", "Limitation of Liability", "12"),
        ("11.", "Force Majeure", "13"),
        ("12.", "Termination and Suspension", "14"),
        ("13.", "Dispute Resolution and Arbitration", "15"),
        ("14.", "Governing Law and Jurisdiction", "16"),
        ("15.", "Assignment and Subcontracting", "16"),
        ("16.", "Non-Solicitation and Non-Compete", "17"),
        ("17.", "Insurance and Compliance", "18"),
        ("18.", "Service Level Agreement (SLA)", "19"),
        ("19.", "Change Control Procedure", "20"),
        ("20.", "Audit Rights", "21"),
        ("21.", "Anti-Corruption and Ethics", "21"),
        ("22.", "Entire Agreement and Amendments", "22"),
        ("Exhibit A.", "Statement of Work (SOW)", "23"),
        ("Exhibit B.", "Risk & Compliance Summary", "24"),
        ("Exhibit C.", "Entity Reference Index", "25"),
        ("Exhibit D.", "Compliance Audit Checklist", "26"),
    ]
    data = [[f"  {num}", title, f"Page {pg}"] for num, title, pg in toc]
    toc_table = Table(data, colWidths=[1.5*cm, 13*cm, 3*cm])
    toc_table.setStyle(TableStyle([
        ("FONTNAME",   (0, 0), (1, -1), "Helvetica"),
        ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR",  (0, 0), (0, -1), ACCENT_BLUE),
        ("TEXTCOLOR",  (1, 0), (1, -1), TEXT_GREY),
        ("TEXTCOLOR",  (2, 0), (2, -1), MID_GREY),
        ("ALIGN",      (2, 0), (2, -1), "RIGHT"),
        ("TOPPADDING",   (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 3),
        ("LINEBELOW",  (0, -1), (-1, -1), 0.5, MID_GREY),
    ]))
    story.append(toc_table)
    story.append(PageBreak())


# ─── Section 1: Definitions ──────────────────────────────────────────────────
def sec_definitions(story, styles):
    story.append(Paragraph("1. DEFINITIONS AND INTERPRETATION", styles["h1"]))
    section_rule(story)
    defs = [
        ("\"Agreement\"", "means this Software Development & Services Agreement, together with all Exhibits, Schedules, and Statements of Work incorporated herein."),
        ("\"Service Provider\"", "means NovaTech Solutions Pvt. Ltd., a company incorporated under the Companies Act, 2013 (CIN: U72200MH2018PTC305741), with its registered office at 42 Rajiv Gandhi IT Park, Pune, Maharashtra 411057, India."),
        ("\"Client\"", "means GlobalEdge Corp., a Delaware corporation with its principal office at 1600 Amphitheatre Parkway, Mountain View, CA 94043, USA, and any of its affiliated entities, subsidiaries, or successors."),
        ("\"Deliverables\"", "means all software, source code, object code, documentation, designs, data models, APIs, configurations, and reports produced by the Service Provider under this Agreement."),
        ("\"Confidential Information\"", "means any non-public, proprietary information disclosed by either Party, including but not limited to business strategies, financial data, customer lists, source code, and technical specifications, whether disclosed in written, electronic, or oral form."),
        ("\"Intellectual Property Rights\"", "means all patents, copyrights, trademarks, trade secrets, database rights, moral rights, and all other intellectual property rights of every nature, whether registered or unregistered, throughout the world."),
        ("\"Personal Data\"", "has the meaning ascribed under the California Consumer Privacy Act (CCPA), GDPR (Regulation (EU) 2016/679), and the Indian Digital Personal Data Protection Act, 2023 (DPDPA)."),
        ("\"Force Majeure Event\"", "means any event beyond a Party's reasonable control, including acts of God, war, terrorism, pandemic, natural disaster, governmental action, or disruption of internet infrastructure."),
        ("\"SLA\"", "means the Service Level Agreement detailed in Section 18, defining uptime guarantees, response times, and escalation procedures."),
        ("\"Milestone\"", "means a defined, measurable project deliverable associated with a specific date and payment tranche as set out in Exhibit A."),
        ("\"Authorized Representative\"", "means, for the Service Provider: Mr. Arjun Mehta, CTO; and for the Client: Ms. Jennifer Walsh, VP Engineering."),
        ("\"Business Day\"", "means any day other than Saturday, Sunday, or a public holiday in either Pune, India, or Mountain View, California."),
    ]
    for term, defn in defs:
        story.append(Paragraph(
            f"<b>{term}</b>: {defn}",
            styles["body"]
        ))
    story.append(Paragraph(
        "1.13  In this Agreement, unless the context otherwise requires: (i) singular includes plural and vice versa; "
        "(ii) headings are for convenience only; (iii) references to 'include' or 'including' shall be construed as "
        "'without limitation'; (iv) references to statutes include amendments thereto; and (v) 'days' refers to "
        "calendar days unless specified as 'Business Days'.",
        styles["body"]
    ))
    story.append(PageBreak())


# ─── Section 2: Scope ────────────────────────────────────────────────────────
def sec_scope(story, styles):
    story.append(Paragraph("2. SCOPE OF SERVICES AND DELIVERABLES", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "2.1  The Service Provider agrees to design, develop, test, deploy, and maintain a cloud-native enterprise "
        "SaaS platform (the \"Platform\") for the Client in accordance with the specifications detailed in Exhibit A "
        "(Statement of Work). The Platform shall include the following core modules:",
        styles["body"]
    ))
    modules = [
        "AI-powered document intelligence engine (Gemini 2.5 API integration)",
        "Multi-tenant user authentication and role-based access control (RBAC)",
        "Real-time analytics dashboard with customisable reporting widgets",
        "Enterprise-grade RESTful API gateway with rate limiting and OAuth 2.0",
        "Automated CI/CD pipeline and Infrastructure-as-Code (Terraform on GCP)",
        "Data warehouse integration (BigQuery) for business intelligence workloads",
        "Mobile-responsive frontend application (Next.js 16 / React 19)",
        "24×7 monitoring, alerting, and on-call support (PagerDuty integration)",
    ]
    for m in modules:
        story.append(Paragraph(f"• {m}", styles["list_item"]))

    story.append(Paragraph(
        "2.2  The Service Provider shall assign a minimum of twelve (12) full-time equivalent engineers, comprising "
        "two (2) solution architects, four (4) senior backend engineers, two (2) frontend engineers, one (1) DevOps "
        "engineer, one (1) QA lead, one (1) security engineer, and one (1) project manager.",
        styles["body"]
    ))
    story.append(Paragraph(
        "2.3  All Deliverables must pass Client's acceptance testing protocol within fifteen (15) Business Days of "
        "delivery. Acceptance shall not be unreasonably withheld. If the Client fails to respond within the fifteen "
        "(15) Business Day window, the Deliverable shall be deemed accepted.",
        styles["body"]
    ))
    story.append(Paragraph(
        "2.4  The Service Provider warrants that all Deliverables will be original, free from third-party claims, "
        "and compliant with OWASP Top-10 security standards as of the delivery date.",
        styles["body"]
    ))
    story.append(Paragraph(
        "2.5  <b>Out-of-Scope:</b> The following are explicitly excluded from this Agreement unless agreed in a "
        "separate signed Change Order: hardware procurement, third-party software licence fees (except those "
        "itemised in Exhibit A), end-user training beyond two (2) sessions, and migration of legacy data older "
        "than five (5) years.",
        styles["body"]
    ))
    story.append(PageBreak())


# ─── Section 3: Timeline ─────────────────────────────────────────────────────
def sec_timeline(story, styles):
    story.append(Paragraph("3. PROJECT TIMELINE AND MILESTONES", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "3.1  The Project shall commence on the Effective Date of <b>15 September 2025</b> and shall be completed "
        "within thirty-six (36) calendar months, unless extended by mutual written agreement. The following "
        "milestone schedule is binding:",
        styles["body"]
    ))

    timeline_data = [
        ["Phase", "Milestone", "Due Date", "Payment Tranche"],
        ["Phase 0", "Project Kick-off & Environment Setup", "15 Oct 2025", "USD 420,000 (10%)"],
        ["Phase 1", "Architecture Design & Tech Stack Sign-off", "30 Nov 2025", "USD 630,000 (15%)"],
        ["Phase 2", "MVP Backend APIs & Database Schema", "28 Feb 2026", "USD 840,000 (20%)"],
        ["Phase 3", "Frontend Integration & Auth Module", "31 May 2026", "USD 630,000 (15%)"],
        ["Phase 4", "AI/ML Document Intelligence Engine", "31 Aug 2026", "USD 630,000 (15%)"],
        ["Phase 5", "Security Audit, Pen Testing & Hardening", "30 Nov 2026", "USD 420,000 (10%)"],
        ["Phase 6", "UAT, Performance Testing & Go-Live", "15 Sep 2027", "USD 420,000 (10%)"],
        ["Phase 7", "Hypercare & Stabilisation (6 months)", "15 Mar 2028", "USD 210,000 (5%)"],
    ]
    tbl = Table(timeline_data, colWidths=[2.5*cm, 6*cm, 3.5*cm, 5.5*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK_NAVY),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_GREY, WHITE]),
        ("FONTSIZE",   (0, 1), (-1, -1), 8.5),
        ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
        ("TEXTCOLOR",  (0, 1), (-1, -1), TEXT_GREY),
        ("GRID",       (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("ALIGN",      (3, 0), (3, -1), "RIGHT"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "3.2  <b>Delay Penalties:</b> In the event the Service Provider fails to deliver any Milestone within "
        "thirty (30) days of the stipulated due date due to reasons attributable solely to the Service Provider, "
        "a delay penalty of <b>0.5% of the applicable Milestone payment per week of delay</b> shall be levied, "
        "capped at <b>10% of the total contract value (USD 420,000)</b>.",
        styles["body"]
    ))
    story.append(Paragraph(
        "3.3  The Client shall provide written sign-off within ten (10) Business Days upon Milestone completion. "
        "Failure to do so without documented justification shall release the Service Provider from delay penalty "
        "obligations for the subsequent phase.",
        styles["body"]
    ))
    story.append(PageBreak())


# ─── Section 4: Fees ─────────────────────────────────────────────────────────
def sec_fees(story, styles):
    story.append(Paragraph("4. FEES, PAYMENT TERMS, AND INVOICING", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "4.1  <b>Total Contract Value:</b> USD 4,200,000 (Four Million Two Hundred Thousand United States Dollars), "
        "exclusive of applicable taxes (GST at 18% on India-origin services).",
        styles["body"]
    ))
    story.append(Paragraph(
        "4.2  Payments shall be made via wire transfer to the Service Provider's designated bank account within "
        "<b>thirty (30) days</b> of receipt of a valid invoice following Milestone acceptance.",
        styles["body"]
    ))
    story.append(Paragraph(
        "4.3  Invoices not disputed in writing within ten (10) Business Days of receipt shall be deemed accepted. "
        "Disputed amounts must be specifically identified; undisputed portions remain payable.",
        styles["body"]
    ))
    story.append(Paragraph(
        "4.4  <b>Late Payment Interest:</b> Any amounts outstanding beyond thirty (30) days from the due date "
        "shall accrue interest at the rate of <b>1.5% per month (18% per annum)</b>, compounded monthly.",
        styles["body"]
    ))
    story.append(Paragraph(
        "4.5  <b>Expense Reimbursement:</b> Pre-approved travel and accommodation expenses incurred by the Service "
        "Provider's personnel at Client's request shall be reimbursed at cost, subject to Client's travel policy. "
        "Expenses exceeding USD 5,000 per month require prior written approval from the Client's CFO, "
        "Ms. Rachel Kim.",
        styles["body"]
    ))
    story.append(Paragraph(
        "4.6  <b>Currency and Withholding:</b> All payments shall be made in United States Dollars. The Client "
        "shall not withhold or deduct any amounts from payments unless legally required, in which case the Client "
        "shall provide applicable withholding tax certificates within fifteen (15) days.",
        styles["body"]
    ))
    story.append(Paragraph(
        "4.7  <b>Price Escalation:</b> Contract rates shall remain fixed for the first twenty-four (24) months. "
        "Thereafter, the Service Provider may apply an annual escalation not exceeding <b>5% per year</b> or "
        "the CPI index (whichever is lower), with ninety (90) days' written notice.",
        styles["body"]
    ))
    story.append(PageBreak())


# ─── Section 5: IP ───────────────────────────────────────────────────────────
def sec_ip(story, styles):
    story.append(Paragraph("5. INTELLECTUAL PROPERTY RIGHTS", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "5.1  <b>Client Ownership:</b> Subject to full and final payment of all fees due hereunder, all "
        "Deliverables, including source code, object code, documentation, and any derivative works created "
        "exclusively for the Client under this Agreement, shall be deemed works-for-hire and shall vest in "
        "the Client upon creation. The Service Provider hereby assigns all such rights to the Client.",
        styles["body"]
    ))
    story.append(Paragraph(
        "5.2  <b>Service Provider Background IP:</b> Notwithstanding Section 5.1, the Service Provider retains "
        "all rights to its pre-existing intellectual property, including proprietary frameworks, libraries, "
        "toolkits, and methodologies ('Background IP'). The Service Provider grants the Client a perpetual, "
        "royalty-free, non-exclusive, non-transferable licence to use Background IP solely to the extent "
        "embedded within the Deliverables.",
        styles["body"]
    ))
    story.append(Paragraph(
        "5.3  <b>Prohibited Use:</b> The Client shall not sub-licence, transfer, or commercialise the "
        "Service Provider's Background IP without prior written consent. Breach of this provision shall "
        "entitle the Service Provider to seek injunctive relief without bond or surety.",
        styles["body"]
    ))
    story.append(Paragraph(
        "5.4  <b>Open-Source Components:</b> Any open-source software incorporated into the Deliverables "
        "must be disclosed in writing and licensed under permissive licences (MIT, Apache 2.0, or BSD). "
        "The use of copyleft (GPL/AGPL) licensed components requires prior written approval from GlobalEdge "
        "Corp.'s Chief Legal Officer.",
        styles["body"]
    ))
    story.append(Paragraph(
        "5.5  <b>IP Indemnity:</b> The Service Provider shall indemnify, defend, and hold harmless the "
        "Client against any third-party claim alleging that the Deliverables infringe any patent, "
        "copyright, or trade secret, provided that the Client notifies the Service Provider within "
        "fifteen (15) Business Days of any such claim.",
        styles["body"]
    ))
    story.append(PageBreak())


# ─── Section 6: NDA / Confidentiality ───────────────────────────────────────
def sec_nda(story, styles):
    story.append(Paragraph("6. CONFIDENTIALITY AND NON-DISCLOSURE", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "6.1  Each Party shall treat all Confidential Information of the other Party as strictly confidential "
        "and shall not disclose it to any third party without the prior written consent of the disclosing Party.",
        styles["body"]
    ))
    story.append(Paragraph(
        "6.2  <b>Permitted Disclosures:</b> A Party may disclose Confidential Information to its directors, "
        "officers, employees, advisors, or subcontractors on a strict need-to-know basis, provided such "
        "individuals are bound by confidentiality obligations no less stringent than those herein.",
        styles["body"]
    ))
    story.append(Paragraph(
        "6.3  <b>Duration:</b> Confidentiality obligations survive termination or expiry of this Agreement "
        "for a period of <b>five (5) years</b> from the date of termination.",
        styles["body"]
    ))
    story.append(Paragraph(
        "6.4  <b>Compelled Disclosure:</b> If either Party is required by law, regulation, or court order to "
        "disclose Confidential Information, it shall (to the extent permitted by law) provide the disclosing "
        "Party with prompt written notice sufficient to allow the disclosing Party to seek a protective order.",
        styles["body"]
    ))
    story.append(Paragraph(
        "6.5  <b>Trade Secrets:</b> The Service Provider acknowledges that GlobalEdge Corp.'s AI training "
        "datasets, proprietary algorithms, and customer behavioural models constitute trade secrets under the "
        "Defend Trade Secrets Act (DTSA), 18 U.S.C. § 1836, and California Uniform Trade Secrets Act (CUTSA). "
        "Unauthorised disclosure shall expose the Service Provider to civil and criminal liability.",
        styles["body"]
    ))
    story.append(PageBreak())


# ─── Section 7: Data Protection ──────────────────────────────────────────────
def sec_data(story, styles):
    story.append(Paragraph("7. DATA PROTECTION AND PRIVACY", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "7.1  The Service Provider shall act as a 'Data Processor' under GDPR and DPDPA, processing Personal "
        "Data only on documented instructions from the Client ('Data Controller'). A separate Data Processing "
        "Agreement (DPA) shall be executed within thirty (30) days of the Effective Date.",
        styles["body"]
    ))
    story.append(Paragraph(
        "7.2  <b>Security Measures:</b> The Service Provider shall implement appropriate technical and "
        "organisational security measures including: AES-256 encryption at rest and TLS 1.3 in transit; "
        "multi-factor authentication (MFA) for all system access; regular penetration testing (quarterly); "
        "and ISO/IEC 27001:2022 certified Information Security Management System (ISMS).",
        styles["body"]
    ))
    story.append(Paragraph(
        "7.3  <b>Data Breach Notification:</b> The Service Provider shall notify the Client of any confirmed "
        "or suspected data breach within <b>forty-eight (48) hours</b> of discovery, in compliance with "
        "GDPR Article 33 and CCPA § 1798.82.",
        styles["body"]
    ))
    story.append(Paragraph(
        "7.4  <b>Data Localisation:</b> All Personal Data of EU/EEA data subjects shall be stored and "
        "processed exclusively within the European Union or countries with an adequacy decision under "
        "GDPR Article 45. Cross-border transfers require execution of Standard Contractual Clauses (SCCs).",
        styles["body"]
    ))
    story.append(Paragraph(
        "7.5  <b>Data Retention and Deletion:</b> Upon termination of this Agreement, the Service Provider "
        "shall, within thirty (30) days, either return or securely destroy all Personal Data and provide "
        "written certification of deletion to the Client.",
        styles["body"]
    ))
    story.append(PageBreak())


# ─── Section 8: Warranties ───────────────────────────────────────────────────
def sec_warranties(story, styles):
    story.append(Paragraph("8. WARRANTIES AND REPRESENTATIONS", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "8.1  <b>Service Provider Warranties:</b> The Service Provider represents and warrants that:",
        styles["body"]
    ))
    warranties = [
        "It has full legal capacity, authority, and corporate power to enter into and perform under this Agreement;",
        "The Deliverables will conform to the specifications in Exhibit A for a period of twelve (12) months post-delivery (the 'Warranty Period');",
        "The Deliverables will not infringe any third-party intellectual property rights;",
        "It will comply with all applicable laws and regulations, including export control laws;",
        "Its personnel have the requisite skills, qualifications, and experience to perform the Services;",
        "It holds all necessary licences, permits, and certifications required to provide the Services.",
    ]
    for w in warranties:
        story.append(Paragraph(f"({chr(96+warranties.index(w)+1)}) {w}", styles["sub_clause"]))

    story.append(Paragraph(
        "8.2  <b>Client Warranties:</b> The Client represents and warrants that it has the authority to grant "
        "the Service Provider access to its systems and data necessary to perform the Services, and that such "
        "access will not violate any applicable laws or third-party agreements.",
        styles["body"]
    ))
    story.append(Paragraph(
        "8.3  <b>Disclaimer:</b> EXCEPT AS EXPRESSLY SET FORTH IN THIS AGREEMENT, NEITHER PARTY MAKES ANY "
        "WARRANTIES, EXPRESS OR IMPLIED, INCLUDING IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A "
        "PARTICULAR PURPOSE, OR NON-INFRINGEMENT. THE SERVICE PROVIDER DOES NOT WARRANT UNINTERRUPTED OR "
        "ERROR-FREE OPERATION OF THE PLATFORM.",
        styles["body"]
    ))
    story.append(PageBreak())


# ─── Section 9: Indemnification ──────────────────────────────────────────────
def sec_indemnification(story, styles):
    story.append(Paragraph("9. INDEMNIFICATION", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "9.1  <b>Service Provider Indemnification:</b> The Service Provider shall indemnify, defend, and hold "
        "harmless the Client and its officers, directors, employees, agents, and successors from and against "
        "any and all third-party claims, damages, losses, liabilities, costs, and expenses (including "
        "reasonable attorneys' fees) arising from or related to: (i) any material breach of this Agreement "
        "by the Service Provider; (ii) any infringement of third-party IP rights by the Deliverables; "
        "(iii) gross negligence or wilful misconduct of the Service Provider's personnel; or "
        "(iv) violation of applicable law by the Service Provider.",
        styles["body"]
    ))
    story.append(Paragraph(
        "9.2  <b>Client Indemnification:</b> The Client shall indemnify, defend, and hold harmless the "
        "Service Provider from and against any third-party claims arising from: (i) the Client's misuse of "
        "the Deliverables; (ii) any breach of the Client's warranties herein; or (iii) the Client's violation "
        "of any third-party rights.",
        styles["body"]
    ))
    story.append(Paragraph(
        "9.3  <b>Indemnification Procedure:</b> The indemnified Party shall: (a) promptly notify the "
        "indemnifying Party in writing of any claim; (b) grant the indemnifying Party sole control over "
        "the defence and settlement; and (c) provide reasonable cooperation at the indemnifying Party's "
        "expense. No settlement shall be made that imposes any obligation on the indemnified Party without "
        "its prior written consent.",
        styles["body"]
    ))
    story.append(PageBreak())


# ─── Section 10: Liability ───────────────────────────────────────────────────
def sec_liability(story, styles):
    story.append(Paragraph("10. LIMITATION OF LIABILITY", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "10.1  <b>⚠ CRITICAL PROVISION — Aggregate Cap:</b> IN NO EVENT SHALL EITHER PARTY'S TOTAL "
        "CUMULATIVE LIABILITY TO THE OTHER PARTY FOR ANY AND ALL CLAIMS ARISING UNDER OR RELATING TO "
        "THIS AGREEMENT EXCEED <b>USD 500,000 (FIVE HUNDRED THOUSAND UNITED STATES DOLLARS)</b>, "
        "REGARDLESS OF THE FORM OF ACTION, WHETHER IN CONTRACT, TORT, STRICT LIABILITY, OR OTHERWISE. "
        "NOTE: This cap represents approximately <b>11.9% of the total contract value</b>.",
        styles["body"]
    ))
    story.append(Paragraph(
        "10.2  <b>Exclusion of Consequential Damages:</b> IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR "
        "ANY INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE, OR CONSEQUENTIAL DAMAGES, INCLUDING "
        "LOSS OF PROFITS, LOSS OF REVENUE, LOSS OF DATA, OR BUSINESS INTERRUPTION, EVEN IF ADVISED OF "
        "THE POSSIBILITY OF SUCH DAMAGES.",
        styles["body"]
    ))
    story.append(Paragraph(
        "10.3  <b>Exceptions:</b> The limitations in Sections 10.1 and 10.2 shall NOT apply to: "
        "(i) death or personal injury caused by negligence; (ii) fraudulent misrepresentation; "
        "(iii) indemnification obligations under Section 9; (iv) breaches of confidentiality obligations "
        "under Section 6; or (v) IP infringement by the Service Provider.",
        styles["body"]
    ))
    story.append(Paragraph(
        "10.4  The Parties acknowledge and agree that the limitations of liability set forth in this "
        "Section reflect a reasonable allocation of risk and form an essential basis of the bargain "
        "between the Parties.",
        styles["body"]
    ))
    story.append(PageBreak())


# ─── Section 11: Force Majeure ───────────────────────────────────────────────
def sec_force_majeure(story, styles):
    story.append(Paragraph("11. FORCE MAJEURE", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "11.1  Neither Party shall be liable for any delay or failure to perform its obligations under "
        "this Agreement to the extent that such failure is caused by a Force Majeure Event, provided "
        "that the affected Party: (a) provides written notice within five (5) Business Days of the "
        "occurrence of such event; (b) uses commercially reasonable efforts to mitigate the effects; "
        "and (c) resumes performance as soon as reasonably practicable.",
        styles["body"]
    ))
    story.append(Paragraph(
        "11.2  If a Force Majeure Event continues for more than ninety (90) consecutive days, either "
        "Party may terminate this Agreement upon thirty (30) days' written notice without liability "
        "(except for amounts already due and payable).",
        styles["body"]
    ))
    story.append(Paragraph(
        "11.3  <b>Financial hardship, currency fluctuation, or increased cost of performance shall NOT "
        "constitute a Force Majeure Event</b> for the purposes of this Agreement.",
        styles["body"]
    ))


# ─── Section 12: Termination ─────────────────────────────────────────────────
def sec_termination(story, styles):
    story.append(Paragraph("12. TERMINATION AND SUSPENSION", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "12.1  <b>Termination for Convenience:</b> The Client may terminate this Agreement at any time "
        "upon <b>ninety (90) days'</b> written notice. In such event, the Client shall pay for all "
        "Services rendered and reasonable, pre-approved, non-cancellable expenses incurred up to the "
        "effective date of termination.",
        styles["body"]
    ))
    story.append(Paragraph(
        "12.2  <b>Termination for Cause:</b> Either Party may terminate this Agreement with immediate "
        "effect upon written notice if the other Party: (a) commits a material breach and fails to "
        "cure such breach within thirty (30) days of written notice; (b) becomes insolvent or makes "
        "an assignment for the benefit of creditors; or (c) has a receiver or liquidator appointed "
        "over its assets.",
        styles["body"]
    ))
    story.append(Paragraph(
        "12.3  <b>Suspension:</b> The Client may suspend the Services upon fourteen (14) days' written "
        "notice. During suspension, the Client shall pay a monthly retainer of USD 75,000 for up to "
        "three (3) months. Suspension exceeding three (3) months entitles the Service Provider to "
        "terminate for convenience.",
        styles["body"]
    ))
    story.append(Paragraph(
        "12.4  <b>Effect of Termination:</b> Upon termination: (a) all licences granted hereunder shall "
        "cease; (b) each Party shall return or destroy the other's Confidential Information; (c) the "
        "Service Provider shall deliver all work-in-progress to the Client within fifteen (15) days; "
        "and (d) provisions intended to survive (Sections 5, 6, 7, 9, 10, 13, 14) shall remain in full force.",
        styles["body"]
    ))
    story.append(PageBreak())


# ─── Section 13: Disputes ────────────────────────────────────────────────────
def sec_disputes(story, styles):
    story.append(Paragraph("13. DISPUTE RESOLUTION AND ARBITRATION", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "13.1  <b>Escalation:</b> The Parties shall first attempt to resolve any dispute through good-faith "
        "negotiations between senior management representatives (VP-level or above) for a period of thirty "
        "(30) calendar days from the date of written notice of the dispute.",
        styles["body"]
    ))
    story.append(Paragraph(
        "13.2  <b>Binding Arbitration:</b> If negotiations fail, any dispute shall be finally resolved by "
        "binding arbitration under the Rules of the American Arbitration Association (AAA) Commercial "
        "Arbitration Rules. The arbitration shall be conducted by three (3) arbitrators. The seat of "
        "arbitration shall be San Francisco, California. The language shall be English. The arbitral "
        "award shall be final and binding on both Parties.",
        styles["body"]
    ))
    story.append(Paragraph(
        "13.3  <b>Emergency Relief:</b> Nothing in this Section shall prevent either Party from seeking "
        "emergency injunctive or other equitable relief from a court of competent jurisdiction to prevent "
        "irreparable harm, including but not limited to the misappropriation of confidential information "
        "or intellectual property.",
        styles["body"]
    ))
    story.append(Paragraph(
        "13.4  <b>Costs:</b> Each Party shall bear its own legal costs. Arbitration fees shall be shared "
        "equally, unless the arbitrators determine that one Party acted in bad faith, in which case "
        "that Party shall bear all costs.",
        styles["body"]
    ))


# ─── Section 14-17: Short combined sections ──────────────────────────────────
def sec_misc(story, styles):
    story.append(Paragraph("14. GOVERNING LAW AND JURISDICTION", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "14.1  This Agreement shall be governed by and construed in accordance with the laws of the "
        "<b>State of California, United States of America</b>, without regard to its conflict of law provisions. "
        "For interim or emergency relief, the Parties consent to the exclusive jurisdiction of the "
        "Superior Court of Santa Clara County, California.",
        styles["body"]
    ))

    story.append(Paragraph("15. ASSIGNMENT AND SUBCONTRACTING", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "15.1  Neither Party may assign or transfer this Agreement or any rights or obligations hereunder "
        "without the prior written consent of the other Party, except that either Party may assign this "
        "Agreement to a successor entity in connection with a merger, acquisition, or sale of all or "
        "substantially all of its assets, provided the successor assumes all obligations hereunder.",
        styles["body"]
    ))
    story.append(Paragraph(
        "15.2  The Service Provider may subcontract portions of the Services with the Client's prior written "
        "approval. Approved subcontractors include: <b>DataMatrix Technologies Ltd. (Hyderabad)</b> for "
        "QA automation and <b>CloudArch Systems Inc. (Bengaluru)</b> for DevOps infrastructure. "
        "The Service Provider remains fully responsible for all subcontractor performance.",
        styles["body"]
    ))

    story.append(Paragraph("16. NON-SOLICITATION AND NON-COMPETE", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "16.1  <b>Non-Solicitation:</b> During the term of this Agreement and for a period of twenty-four "
        "(24) months thereafter, neither Party shall directly or indirectly solicit, recruit, or hire "
        "any employee or contractor of the other Party who was involved in the performance of this Agreement, "
        "without the prior written consent of the other Party.",
        styles["body"]
    ))
    story.append(Paragraph(
        "16.2  <b>Non-Compete:</b> The Service Provider agrees that for a period of twelve (12) months "
        "following the completion of the Project, it shall not undertake development of a directly competing "
        "AI-powered document intelligence platform for any of the Client's named competitors listed in "
        "Schedule 1 of this Agreement.",
        styles["body"]
    ))
    story.append(PageBreak())


# ─── Section 17-22 ──────────────────────────────────────────────────────────
def sec_insurance(story, styles):
    story.append(Paragraph("17. INSURANCE AND COMPLIANCE", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "17.1  The Service Provider shall maintain at its own expense the following minimum insurance "
        "coverages throughout the term of this Agreement:",
        styles["body"]
    ))
    insurance = [
        ("Commercial General Liability", "USD 2,000,000 per occurrence / USD 5,000,000 aggregate"),
        ("Professional Indemnity (E&O)", "USD 5,000,000 per claim"),
        ("Cyber Liability Insurance", "USD 3,000,000 per occurrence"),
        ("Workers' Compensation", "As required by applicable law"),
        ("Directors & Officers (D&O)", "USD 1,000,000"),
    ]
    ins_data = [["Coverage Type", "Minimum Limit"]] + [[t, l] for t, l in insurance]
    ins_tbl = Table(ins_data, colWidths=[8*cm, 9.5*cm])
    ins_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), MID_BLUE),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_GREY, WHITE]),
        ("FONTSIZE",   (0, 1), (-1, -1), 9),
        ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
        ("TEXTCOLOR",  (0, 1), (-1, -1), TEXT_GREY),
        ("GRID",       (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ]))
    story.append(ins_tbl)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "17.2  The Service Provider shall name GlobalEdge Corp. as an additional insured on all relevant "
        "policies and provide certificates of insurance within ten (10) days of execution.",
        styles["body"]
    ))

    story.append(Paragraph("18. SERVICE LEVEL AGREEMENT (SLA)", styles["h1"]))
    section_rule(story)
    sla_data = [
        ["SLA Metric", "Target", "Penalty for Breach"],
        ["Platform Uptime", "99.9% monthly", "1% monthly fee credit per 0.1% shortfall"],
        ["Critical Bug Fix", "4 hours response / 24 hrs resolution", "USD 5,000 per incident"],
        ["High Bug Fix", "8 hours response / 72 hrs resolution", "USD 2,000 per incident"],
        ["API Response Time", "< 200ms (p95)", "Service credit up to 5% monthly fee"],
        ["Security Incident", "Notify within 48 hours", "USD 10,000 per breach of notification SLA"],
        ["Disaster Recovery", "RTO 4 hrs / RPO 1 hr", "USD 25,000 per incident breach"],
    ]
    sla_tbl = Table(sla_data, colWidths=[4.5*cm, 5*cm, 8*cm])
    sla_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK_NAVY),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_GREY, WHITE]),
        ("FONTSIZE",   (0, 1), (-1, -1), 8),
        ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
        ("TEXTCOLOR",  (0, 1), (-1, -1), TEXT_GREY),
        ("GRID",       (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5),
        ("TOPPADDING",   (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 3),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(sla_tbl)

    story.append(Paragraph("19. CHANGE CONTROL PROCEDURE", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "19.1  Any modification to the Scope of Services, Timeline, or Budget shall be handled through a "
        "formal Change Control process. The requesting Party shall submit a Change Request Form (CRF). "
        "The Service Provider shall provide a written impact assessment within ten (10) Business Days. "
        "No work on a Change Request shall commence until both Parties have executed a written Change Order.",
        styles["body"]
    ))

    story.append(Paragraph("20. AUDIT RIGHTS", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "20.1  The Client shall have the right, upon thirty (30) days' written notice, to audit the "
        "Service Provider's records, systems, and facilities relevant to this Agreement, no more than "
        "once per calendar year, to verify compliance with the terms hereof, applicable laws, and data "
        "protection requirements. Audit costs shall be borne by the Client unless material non-compliance "
        "is discovered.",
        styles["body"]
    ))

    story.append(Paragraph("21. ANTI-CORRUPTION AND ETHICS", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "21.1  Each Party represents that it has not made, offered, or authorised, and will not make, "
        "offer, or authorise, any payment or transfer of value to any government official, political "
        "party, or any other person for the purpose of influencing any official act in violation of "
        "the U.S. Foreign Corrupt Practices Act (FCPA), the UK Bribery Act 2010, or the Indian "
        "Prevention of Corruption Act, 1988.",
        styles["body"]
    ))

    story.append(Paragraph("22. ENTIRE AGREEMENT AND AMENDMENTS", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "22.1  This Agreement, together with all Exhibits attached hereto, constitutes the entire agreement "
        "between the Parties with respect to its subject matter and supersedes all prior discussions, "
        "representations, warranties, and understandings, whether written or oral.",
        styles["body"]
    ))
    story.append(Paragraph(
        "22.2  No amendment or modification of this Agreement shall be valid or binding unless made in "
        "writing and duly executed by the authorised representatives of both Parties.",
        styles["body"]
    ))
    story.append(PageBreak())


# ─── Signatures ──────────────────────────────────────────────────────────────
def sec_signatures(story, styles):
    story.append(Paragraph("SIGNATURE PAGE", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "IN WITNESS WHEREOF, the Parties have executed this Software Development & Services Agreement "
        "as of the Effective Date first written above.",
        styles["body"]
    ))
    story.append(Spacer(1, 1*cm))

    sig_data = [
        ["FOR AND ON BEHALF OF", "", "FOR AND ON BEHALF OF"],
        ["NovaTech Solutions Pvt. Ltd.", "", "GlobalEdge Corp."],
        ["", "", ""],
        ["Signature: ______________________", "", "Signature: ______________________"],
        ["Name: Mr. Arjun Mehta", "", "Name: Ms. Jennifer Walsh"],
        ["Title: Chief Technology Officer", "", "Title: Vice President, Engineering"],
        ["Date: ___________________________", "", "Date: ___________________________"],
        ["Place: Pune, Maharashtra, India", "", "Place: Mountain View, CA, USA"],
    ]
    sig_tbl = Table(sig_data, colWidths=[7.5*cm, 2.5*cm, 7.5*cm])
    sig_tbl.setStyle(TableStyle([
        ("FONTNAME",   (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME",   (0, 0), (0, 1), "Helvetica-Bold"),
        ("FONTNAME",   (2, 0), (2, 1), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR",  (0, 0), (0, 1), DARK_NAVY),
        ("TEXTCOLOR",  (2, 0), (2, 1), DARK_NAVY),
        ("TEXTCOLOR",  (0, 2), (-1, -1), TEXT_GREY),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ]))
    story.append(sig_tbl)
    story.append(PageBreak())


# ─── Exhibit A: SOW ──────────────────────────────────────────────────────────
def exhibit_a(story, styles):
    story.append(Paragraph("EXHIBIT A — STATEMENT OF WORK (SOW)", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "This Statement of Work ('SOW') forms an integral part of the Agreement and describes the detailed "
        "technical specifications, deliverable acceptance criteria, and resource allocation for the "
        "DocPilot AI Enterprise Platform development engagement.",
        styles["body"]
    ))
    story.append(Paragraph("A.1  Technology Stack", styles["h2"]))
    tech = [
        ("Backend Framework", "FastAPI 0.111 (Python 3.12) with asyncio"),
        ("Frontend Framework", "Next.js 16 / React 19 / TypeScript 5"),
        ("AI/ML Engine", "Google Gemini 2.5 Flash & Pro via Vertex AI"),
        ("Cloud Platform", "Google Cloud Platform (GCP) — us-central1 primary, eu-west1 DR"),
        ("Database", "PostgreSQL 16 (primary), Redis 7 (cache), BigQuery (analytics)"),
        ("Message Queue", "Google Pub/Sub (event streaming), Apache Kafka 3.6"),
        ("Infrastructure", "Terraform 1.8, Docker, Kubernetes (GKE Autopilot)"),
        ("Monitoring", "Google Cloud Monitoring, Grafana, PagerDuty"),
        ("Security", "Google Cloud Armor, Secret Manager, VPC Service Controls"),
    ]
    for k, v in tech:
        story.append(Paragraph(f"<b>{k}:</b>  {v}", styles["body"]))

    story.append(Paragraph("A.2  Acceptance Criteria", styles["h2"]))
    criteria = [
        "All unit tests pass with ≥ 85% code coverage (measured by pytest-cov);",
        "Integration tests pass across all defined test scenarios in the QA plan;",
        "Performance benchmarks: API < 200ms p95, page load < 2.5 seconds;",
        "Security scan: zero Critical or High vulnerabilities in SAST/DAST reports;",
        "Accessibility: WCAG 2.1 Level AA compliance verified by automated audit;",
        "Documentation: API docs (OpenAPI 3.1), architecture diagrams (C4 model), runbooks complete.",
    ]
    for c in criteria:
        story.append(Paragraph(f"• {c}", styles["list_item"]))
    story.append(PageBreak())


# ─── Exhibit B: Risk Summary ──────────────────────────────────────────────────
def exhibit_b(story, styles):
    story.append(Paragraph("EXHIBIT B — RISK & COMPLIANCE SUMMARY (FOR DOCPILOT AI DEMONSTRATION)", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "The following risk register has been pre-identified by legal counsel for reference. This exhibit is "
        "designed to be detected, analysed, and scored by the DocPilot AI Document Intelligence Platform.",
        styles["body"]
    ))

    story.append(Paragraph("B.1  Risk Register", styles["h2"]))
    risk_rows = [
        ("Liability Cap", "Critical", "Section 10.1 caps liability at USD 500,000 (11.9% of contract value), creating severe financial exposure for the Client on a USD 4.2M engagement."),
        ("IP Ownership", "Critical", "Section 5.2 retains Service Provider Background IP with only a non-exclusive licence, risking Client's ability to modify or transfer the Platform."),
        ("Indemnification Asymmetry", "High", "Section 9 indemnification obligations are not fully mutual. Client exposure to third-party IP claims from Service Provider's code is inadequately addressed."),
        ("Data Breach Notification", "High", "48-hour breach notification (Section 7.3) is insufficient for GDPR Article 33's 72-hour regulator notification requirement to be met with buffer time."),
        ("Non-Compete Enforceability", "High", "Section 16.2 non-compete provisions may be unenforceable under California Business & Professions Code § 16600, which broadly invalidates non-competes."),
        ("Payment Late Interest", "Medium", "Section 4.4's 1.5% per month (18% p.a.) late interest rate may exceed usury limits in certain jurisdictions and creates significant financial risk."),
        ("Subcontractor Liability", "Medium", "Section 15.2 pre-approves subcontractors (DataMatrix Technologies, CloudArch Systems) without adequate background check or security certification requirements."),
        ("SLA Penalties Cap", "Medium", "Service credits under Section 18 are the Client's sole remedy for SLA breaches. No right to terminate for persistent SLA failures is provided."),
        ("Force Majeure Scope", "Medium", "Section 11 force majeure definition is broad and includes 'disruption of internet infrastructure,' which could be misused to excuse performance failures."),
        ("Non-Solicitation Duration", "Low", "Section 16.1's 24-month non-solicitation period is longer than industry standard (12 months) and may create talent acquisition challenges for the Client."),
        ("Price Escalation", "Low", "Section 4.7 allows 5% annual price escalation after 24 months, which should be reviewed against projected budget for the final 12 months."),
    ]
    risk_table(story, styles, risk_rows)
    story.append(PageBreak())


# ─── Exhibit C: Entity Index ──────────────────────────────────────────────────
def exhibit_c(story, styles):
    story.append(Paragraph("EXHIBIT C — ENTITY REFERENCE INDEX", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "All named entities extracted from this Agreement for reference and verification:",
        styles["body"]
    ))
    entity_rows = [
        ["Company", "NovaTech Solutions Pvt. Ltd. (Service Provider)"],
        ["Company", "GlobalEdge Corp. (Client)"],
        ["Company", "DataMatrix Technologies Ltd."],
        ["Company", "CloudArch Systems Inc."],
        ["Person", "Mr. Arjun Mehta — CTO, NovaTech Solutions"],
        ["Person", "Ms. Jennifer Walsh — VP Engineering, GlobalEdge Corp."],
        ["Person", "Ms. Priya Sharma — Legal Counsel, NovaTech"],
        ["Person", "Mr. David Chen — General Counsel, GlobalEdge Corp."],
        ["Person", "Ms. Rachel Kim — CFO, GlobalEdge Corp."],
        ["Date", "Effective Date: 15 September 2025"],
        ["Date", "Phase 0 Completion: 15 October 2025"],
        ["Date", "Phase 1 Completion: 30 November 2025"],
        ["Date", "Phase 2 Completion: 28 February 2026"],
        ["Date", "Project Go-Live: 15 September 2027"],
        ["Date", "Hypercare End: 15 March 2028"],
        ["Monetary Amount", "Total Contract Value: USD 4,200,000"],
        ["Monetary Amount", "Liability Cap: USD 500,000"],
        ["Monetary Amount", "Monthly Retainer (Suspension): USD 75,000"],
        ["Monetary Amount", "Delay Penalty Cap: USD 420,000 (10% of TCV)"],
        ["Monetary Amount", "Expense Pre-approval Threshold: USD 5,000/month"],
        ["Jurisdiction", "State of California, USA (Governing Law)"],
        ["Jurisdiction", "Superior Court of Santa Clara County, CA"],
        ["Jurisdiction", "American Arbitration Association (AAA) — San Francisco"],
        ["Regulation", "GDPR (Regulation EU 2016/679)"],
        ["Regulation", "California Consumer Privacy Act (CCPA)"],
        ["Regulation", "DPDPA 2023 (India Digital Personal Data Protection Act)"],
        ["Regulation", "U.S. FCPA (Foreign Corrupt Practices Act)"],
        ["Regulation", "UK Bribery Act 2010"],
        ["Standard", "ISO/IEC 27001:2022 (Information Security)"],
        ["Standard", "OWASP Top-10 (Application Security)"],
        ["Standard", "WCAG 2.1 Level AA (Accessibility)"],
        ["Contract ID", "GEC-NTS-2025-0917"],
    ]
    entity_table(story, styles, entity_rows)
    story.append(PageBreak())


# ─── Exhibit D: Compliance Checklist ─────────────────────────────────────────
def exhibit_d(story, styles):
    story.append(Paragraph("EXHIBIT D — COMPLIANCE AUDIT CHECKLIST", styles["h1"]))
    section_rule(story)
    story.append(Paragraph(
        "Standard provisions checklist assessed against best practices for an enterprise software services agreement:",
        styles["body"]
    ))
    compliance_rows = [
        ["Indemnification Clause",             "Present", "Mutual indemnification provided in Section 9. Asymmetry noted — see Risk Register."],
        ["Limitation of Liability",            "Present", "Section 10.1 — cap is critically low at USD 500K (11.9% TCV). Recommend USD 4.2M minimum."],
        ["IP Ownership Clause",                "Present", "Section 5 — Client ownership conditional on full payment. Background IP retained by SP."],
        ["Confidentiality / NDA",              "Present", "Section 6 — 5-year post-termination duration. Meets industry standard."],
        ["Data Protection / DPA",              "Present", "Section 7 — GDPR/CCPA/DPDPA addressed. Separate DPA execution required within 30 days."],
        ["Dispute Resolution",                 "Present", "Section 13 — 3-arbitrator AAA panel in San Francisco. Appropriate for USD 4.2M contract."],
        ["Governing Law",                      "Present", "Section 14 — California law. Note: Indian law may be more favourable for SP."],
        ["Force Majeure",                      "Present", "Section 11 — standard provisions. Note: broad internet disruption exclusion."],
        ["Termination Rights",                 "Present", "Section 12 — 90-day convenience termination. Missing: termination for persistent SLA breach."],
        ["Service Level Agreement",            "Present", "Section 18 — comprehensive SLA table. Missing: right to terminate for repeated SLA failures."],
        ["Insurance Requirements",             "Present", "Section 17 — USD 5M E&O, USD 3M Cyber Liability. Meets enterprise standard."],
        ["Anti-Corruption / Ethics",           "Present", "Section 21 — FCPA, UK Bribery Act, Indian PCA covered."],
        ["Audit Rights",                       "Present", "Section 20 — annual audit rights with 30-day notice. Standard provision."],
        ["Non-Solicitation",                   "Present", "Section 16.1 — 24-month duration. Longer than industry standard of 12 months."],
        ["Non-Compete",                        "Present", "Section 16.2 — LIKELY UNENFORCEABLE under Cal. B&P Code § 16600."],
        ["Price Escalation Clause",            "Present", "Section 4.7 — 5% cap after 24 months. Acceptable but should be CPI-linked only."],
        ["Warranty Clause",                    "Present", "Section 8 — 12-month post-delivery warranty. Industry standard."],
        ["Change Control Procedure",           "Present", "Section 19 — formal CRF process. Appropriate."],
        ["Entire Agreement / Merger Clause",   "Present", "Section 22 — standard provision."],
        ["Assignment Restrictions",            "Present", "Section 15 — mutual consent required except M&A. Standard."],
        ["MISSING: Source Code Escrow",        "Missing",  "No source code escrow arrangement provided. Critical for USD 4.2M dependency on a single vendor."],
        ["MISSING: Step-in Rights",            "Missing",  "No step-in rights for Client in case of SP insolvency. High risk given platform dependency."],
        ["MISSING: Business Continuity Plan",  "Missing",  "No BCP/DR plan requirement beyond SLA metrics. Should require documented BCP with annual testing."],
        ["MISSING: Liquidated Damages",        "Missing",  "Delay penalties (Section 3.2) are the only quantified remedy. No liquidated damages for material breach."],
    ]
    compliance_table(story, styles, compliance_rows)

    story.append(Paragraph("D.1  Overall Compliance Assessment", styles["h2"]))
    story.append(Paragraph(
        "This Agreement contains most standard provisions expected for an enterprise software services contract. "
        "However, four (4) critical provisions are absent: Source Code Escrow, Step-in Rights, Business "
        "Continuity Plan, and Liquidated Damages. Additionally, the liability cap (Section 10.1) is critically "
        "low, and the non-compete clause (Section 16.2) is likely unenforceable under California law. The "
        "overall risk score is assessed as <b>HIGH (72/100)</b> and the recommended decision is "
        "<b>'Proceed after Negotiation'</b> subject to resolution of Critical and High severity risk items.",
        styles["body"]
    ))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "— END OF AGREEMENT — CONTRACT REF: GEC-NTS-2025-0917 — CONFIDENTIAL —",
        ParagraphStyle("end", fontSize=9, textColor=MID_GREY,
                       fontName="Helvetica-Bold", alignment=TA_CENTER)
    ))


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="Software Development & Services Agreement — DocPilot AI Test Document",
        author="NovaTech Solutions Pvt. Ltd. / GlobalEdge Corp.",
        subject="Enterprise SaaS Platform Development — Contract GEC-NTS-2025-0917",
        creator="DocPilot AI Test Document Generator",
    )

    styles = build_styles()
    story = []

    build_cover(story, styles)
    build_toc(story, styles)
    sec_definitions(story, styles)
    sec_scope(story, styles)
    sec_timeline(story, styles)
    sec_fees(story, styles)
    sec_ip(story, styles)
    sec_nda(story, styles)
    sec_data(story, styles)
    sec_warranties(story, styles)
    sec_indemnification(story, styles)
    sec_liability(story, styles)
    sec_force_majeure(story, styles)
    sec_termination(story, styles)
    sec_disputes(story, styles)
    sec_misc(story, styles)
    sec_insurance(story, styles)
    sec_signatures(story, styles)
    exhibit_a(story, styles)
    exhibit_b(story, styles)
    exhibit_c(story, styles)
    exhibit_d(story, styles)

    doc.build(story)
    print(f"[OK] PDF generated successfully: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
