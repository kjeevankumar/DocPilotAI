import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PDF = BASE_DIR / "DocPilot_AI_Hindsight_Integration_Submission.pdf"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        self.saveState()
        indigo = colors.HexColor("#4f46e5")
        slate = colors.HexColor("#64748b")
        border = colors.HexColor("#cbd5e1")
        
        # Header line
        self.setStrokeColor(indigo)
        self.setLineWidth(1)
        self.line(40, 750, 572, 750)
        
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(indigo)
        self.drawString(40, 756, "DOCPILOT AI  |  HINDSIGHT PERSISTENT AGENT MEMORY")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(slate)
        self.drawRightString(572, 756, "Vectorize Hackathon Submission Guide")
        
        # Footer line
        self.setStrokeColor(border)
        self.setLineWidth(0.5)
        self.line(40, 45, 572, 45)
        
        self.setFont("Helvetica", 8)
        self.drawString(40, 32, "Built with Vectorize Hindsight & FastAPI • Hackathon Edition")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 32, page_text)
        
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=55,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    indigo = colors.HexColor("#4f46e5")
    dark = colors.HexColor("#0f172a")
    slate = colors.HexColor("#334155")
    light_slate = colors.HexColor("#64748b")
    bg_card = colors.HexColor("#f8fafc")
    border_card = colors.HexColor("#e2e8f0")
    emerald = colors.HexColor("#059669")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=dark,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=indigo,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=indigo,
        spaceBefore=12,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'Heading2',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=dark,
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=slate,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=slate,
        leftIndent=12,
        spaceAfter=3
    )

    table_header = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    table_cell = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=indigo
    )

    story = []

    # Title & Header
    story.append(Paragraph("DocPilot AI: Hindsight Persistent Memory Integration", title_style))
    story.append(Paragraph("<b>Hackathon Submission Reference & Architecture Guide</b> — Vectorize Hindsight Memory Challenge", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=indigo, spaceAfter=10))

    # Executive Summary Card
    exec_summary_text = (
        "<b>Executive Summary:</b> DocPilot AI is an autonomous document intelligence platform that solves "
        "the <i>'Stateless Amnesia'</i> flaw in traditional document analysis. By integrating <b>Vectorize Hindsight</b>, "
        "the agent maintains a multi-document <b>Institutional Memory Bank</b> (<code>docpilot-legal-bank</code>), "
        "allowing it to recall historical contract precedents, validate company risk policies, calibrate liability caps, "
        "and continuously learn from human feedback."
    )
    exec_card = Table(
        [[Paragraph(exec_summary_text, body_style)]],
        colWidths=[532]
    )
    exec_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#eef2ff")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#c7d2fe")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(exec_card)
    story.append(Spacer(1, 10))

    # SECTION 1
    story.append(Paragraph("1. What Problem We Are Solving", h1_style))
    story.append(Paragraph("<b>The 'Amnesia Flaw' in Traditional Document AI:</b>", h2_style))
    story.append(Paragraph(
        "In enterprise legal, compliance, and procurement operations, teams review hundreds of agreements (MSAs, NDAs, SOWs) monthly. "
        "Conventional LLM document tools analyze each file in a complete vacuum. Every time a contract is uploaded, the AI:",
        body_style
    ))
    story.append(Paragraph("• <b>Has Zero Counterparty Context:</b> Doesn't know what terms your company previously approved or rejected for recurring partners (e.g. <i>Acme Corp</i>).", bullet_style))
    story.append(Paragraph("• <b>Flags Recurring False Positives:</b> Re-flags previously vetted exceptions (such as an approved 1x annual liability cap) as critical violations every single time.", bullet_style))
    story.append(Paragraph("• <b>Fails to Learn:</b> When a user approves an exception or redline, the decision is lost the moment the browser tab closes.", bullet_style))
    story.append(Paragraph(
        "<b>The Business Case:</b> Legal and procurement teams spend 40%+ of their time re-checking past contracts and email threads. "
        "DocPilot AI eliminates redundant reviews by acting as an institutional memory partner, delivering immediate $100+/seat enterprise value.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # SECTION 2
    story.append(Paragraph("2. How Hindsight Memory is Architected & Used", h1_style))
    story.append(Paragraph(
        "DocPilot AI leverages the official <b>Hindsight Python SDK</b> (<code>hindsight-client</code>) alongside a resilient hybrid bank:",
        body_style
    ))
    
    arch_items = [
        [Paragraph("<b>Operation</b>", table_header), Paragraph("<b>Agent Implementation</b>", table_header), Paragraph("<b>Business Value</b>", table_header)],
        [
            Paragraph("<b>RECALL</b>", table_cell_bold),
            Paragraph("<code>hindsight_service.recall()</code> queries active bank (<code>docpilot-legal-bank</code>) during Step 10 for counterparty history and clause rules.", table_cell),
            Paragraph("Validates incoming clauses against established baselines (e.g. Acme Corp liability cap, Net-30 payment standard).", table_cell)
        ],
        [
            Paragraph("<b>RETAIN</b>", table_cell_bold),
            Paragraph("<code>hindsight_service.retain()</code> autonomously saves contract analysis summaries, risk scores, and entity milestones.", table_cell),
            Paragraph("Ensures the AI continuously learns from every agreement processed without manual training loops.", table_cell)
        ],
        [
            Paragraph("<b>TEACH AGENT</b>", table_cell_bold),
            Paragraph("Interactive UI modal in the <i>Hindsight Memory Engine</i> tab allows users to teach new policies and approved exceptions in real time.", table_cell),
            Paragraph("Human-in-the-loop governance: legal teams retain approved exceptions that instantly influence future reviews.", table_cell)
        ],
        [
            Paragraph("<b>MEMORY CHAT</b>", table_cell_bold),
            Paragraph("Chat agent queries Hindsight memory for relevant precedents before responding to user questions.", table_cell),
            Paragraph("Allows natural queries like <i>'What did we negotiate with Acme Corp previously?'</i> with exact memory citations.", table_cell)
        ],
    ]
    arch_table = Table(arch_items, colWidths=[80, 240, 212])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), indigo),
        ('GRID', (0,0), (-1,-1), 0.5, border_card),
        ('BACKGROUND', (0,1), (-1,1), colors.white),
        ('BACKGROUND', (0,2), (-1,2), bg_card),
        ('BACKGROUND', (0,3), (-1,3), colors.white),
        ('BACKGROUND', (0,4), (-1,4), bg_card),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 10))

    # SECTION 3 - COMPARISON TABLE
    story.append(Paragraph("3. 'Before Memory vs. After Memory' Comparison", h1_style))
    comp_items = [
        [Paragraph("<b>Scenario</b>", table_header), Paragraph("<b>Without Memory (Stateless AI)</b>", table_header), Paragraph("<b>With Hindsight Memory (DocPilot AI)</b>", table_header)],
        [
            Paragraph("<b>Vendor Liability Cap</b>", table_cell_bold),
            Paragraph("Flags 1x annual cap as a Critical Risk violation. Demands rigid 2x cap boilerplate.", table_cell),
            Paragraph("Recalls <b>Precedent #mem_seed_001</b>: Approved 1x cap for Acme Corp due to $5M cyber insurance. Calibrates risk badge.", table_cell)
        ],
        [
            Paragraph("<b>Payment Terms</b>", table_cell_bold),
            Paragraph("Evaluates Net-45 in isolation with generic, non-binding comments.", table_cell),
            Paragraph("Validates against <b>Policy #mem_seed_002</b> (Procurement standard Net-30/45) and confirms full compliance.", table_cell)
        ],
        [
            Paragraph("<b>Human Overrides</b>", table_cell_bold),
            Paragraph("Forgets lawyer redlines immediately after the session.", table_cell),
            Paragraph("<b>Retains</b> approvals in Hindsight; next contract with vendor automatically respects past decision.", table_cell)
        ],
        [
            Paragraph("<b>Cross-Doc Q&A</b>", table_cell_bold),
            Paragraph("<i>'I can only see text in the currently uploaded file.'</i>", table_cell),
            Paragraph("<i>'Across past reviews with this vendor, you compromised on notice period but held firm on mutual IP indemnification.'</i>", table_cell)
        ],
    ]
    comp_table = Table(comp_items, colWidths=[100, 216, 216])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e1b4b")),
        ('GRID', (0,0), (-1,-1), 0.5, border_card),
        ('BACKGROUND', (0,1), (-1,1), colors.white),
        ('BACKGROUND', (0,2), (-1,2), bg_card),
        ('BACKGROUND', (0,3), (-1,3), colors.white),
        ('BACKGROUND', (0,4), (-1,4), bg_card),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 10))

    # SECTION 4 - DEMO SCRIPT
    story.append(Paragraph("4. 3-Minute Hackathon Demo Script (Cue Sheet)", h1_style))
    script_items = [
        [Paragraph("<b>Time</b>", table_header), Paragraph("<b>Screen Action</b>", table_header), Paragraph("<b>Narration Script</b>", table_header)],
        [
            Paragraph("0:00 - 0:40", table_cell_bold),
            Paragraph("Open <code>http://localhost:3000</code>. Point to pulsing <i>'Hindsight Memory Active'</i> badge.", table_cell),
            Paragraph("<i>'Today's document AI has amnesia. Reviewing contracts from recurring vendors wastes hours because the AI forgets past deals. DocPilot AI solves this using Vectorize Hindsight persistent memory.'</i>", table_cell)
        ],
        [
            Paragraph("0:40 - 1:20", table_cell_bold),
            Paragraph("Upload <code>DocPilot_Test_Agreement.pdf</code>. Watch autonomous agent logs.", table_cell),
            Paragraph("<i>'Our multi-agent pipeline extracts entities, parses clauses, and detects risks. In Step 10, the Hindsight Memory Agent queries our corporate memory bank for organizational precedents.'</i>", table_cell)
        ],
        [
            Paragraph("1:20 - 2:00", table_cell_bold),
            Paragraph("Switch to <b>Hindsight Memory Engine</b> tab. Show recalled Acme Corp card.", table_cell),
            Paragraph("<i>'Notice the Recalled Precedents: for Acme Corp, the agent recalled our historical approved exception. In the Risk Register, it flags the clause with a Hindsight Precedent badge instead of a false alarm.'</i>", table_cell)
        ],
        [
            Paragraph("2:00 - 2:30", table_cell_bold),
            Paragraph("Click <b>Teach Agent Policy</b>. Add a new rule live and click Retain.", table_cell),
            Paragraph("<i>'We can teach the agent new policies live. When we retain this rule, it is saved into Hindsight and immediately influences future reviews for this vendor.'</i>", table_cell)
        ],
        [
            Paragraph("2:30 - 3:00", table_cell_bold),
            Paragraph("Switch to <b>AI Q&A Chat</b>. Ask about Acme Corp liability cap.", table_cell),
            Paragraph("<i>'Our conversational chat agent queries Hindsight memory directly. DocPilot AI turns static PDFs into continuous organizational learning. Thank you!'</i>", table_cell)
        ],
    ]
    script_table = Table(script_items, colWidths=[65, 187, 280])
    script_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), indigo),
        ('GRID', (0,0), (-1,-1), 0.5, border_card),
        ('BACKGROUND', (0,1), (-1,1), colors.white),
        ('BACKGROUND', (0,2), (-1,2), bg_card),
        ('BACKGROUND', (0,3), (-1,3), colors.white),
        ('BACKGROUND', (0,4), (-1,4), bg_card),
        ('BACKGROUND', (0,5), (-1,5), colors.white),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(script_table)
    story.append(Spacer(1, 10))

    # SECTION 5 - SUBMISSION DELIVERABLES & CHECKLIST
    story.append(Paragraph("5. Official Hackathon Submission Deliverables", h1_style))
    
    deliv_text = (
        "<b>1. Social Media Post (LinkedIn / X):</b><br/>"
        "<i>'🚀 Excited to unveil DocPilot AI for the Vectorize Hindsight Hackathon! The biggest flaw in today's document AI "
        "is Stateless Amnesia: when reviewing contracts from recurring partners, standard LLMs have zero memory of past deals. "
        "With Hindsight by Vectorize, DocPilot AI introduces persistent memory to contract intelligence with Precedent Recall, "
        "Autonomous Retain, and a live Memory Engine Inspector! #AI #AIAgents #Vectorize #Hindsight #LegalTech #Hackathon'</i><br/><br/>"
        "<b>2. Article / Blog Post Title:</b> <i>Building an Autonomous Contract Intelligence Agent with Persistent Memory using Vectorize Hindsight</i><br/>"
        "<b>3. Technical Architecture Checklist:</b><br/>"
        "&nbsp;&nbsp;[✓] Official <code>hindsight-client</code> Python SDK integrated<br/>"
        "&nbsp;&nbsp;[✓] Core operations implemented: <code>recall</code>, <code>retain</code>, <code>list_memories</code>, <code>status</code><br/>"
        "&nbsp;&nbsp;[✓] Multi-agent orchestration with Step 10 Hindsight Memory Agent<br/>"
        "&nbsp;&nbsp;[✓] Frontend Hindsight Memory Engine tab with interactive Before/After comparison toggle<br/>"
        "&nbsp;&nbsp;[✓] Offline-resilient hybrid memory bank (100% demo reliability without external network failures)"
    )
    deliv_card = Table([[Paragraph(deliv_text, body_style)]], colWidths=[532])
    deliv_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(deliv_card)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"SUCCESS: Generated PDF at {OUTPUT_PDF}")

if __name__ == "__main__":
    build_pdf()
