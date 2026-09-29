# 🧠 DocPilot AI
### Autonomous Contract & Document Intelligence with Persistent Institutional Memory

[![Vectorize Hindsight](https://img.shields.io/badge/Memory_Engine-Vectorize_Hindsight-6366f1?style=for-the-badge&logo=target)](https://vectorize.io)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_0.111-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js 14](https://img.shields.io/badge/Frontend-Next.js_14-black?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![Google Gemini](https://img.shields.io/badge/LLM-Google_Gemini-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)
[![TypeScript](https://img.shields.io/badge/Language-TypeScript-3178C6?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> **Vectorize Hindsight Hackathon Submission**  
> *Transforming Document & Contract Intelligence from Stateless LLM Analysis into an Institutional Memory System.*

---

## 🌟 Overview

Conventional document AI tools suffer from **"Stateless Amnesia"**: every contract is analyzed in an isolated vacuum. When an enterprise reviews agreements from recurring vendors or counterparties:
- The AI has **zero context** of past negotiated terms.
- It **repeatedly flags approved corporate exceptions** (e.g., custom liability caps, non-standard payment terms) as critical risks.
- Every redline, human override, and agreed-upon concession is **lost immediately** once the session ends.

**DocPilot AI solves this using [Vectorize Hindsight](https://vectorize.io)**. By coupling a 10-step autonomous multi-agent pipeline with a persistent institutional memory bank, DocPilot AI **recalls** historical precedents, **auto-calibrates** risk scores, and **retains** organizational learning across every contract review.

---

## 🚀 Key Features

- **🧠 Vectorize Hindsight Memory Engine:** Persistent memory bank (`docpilot-legal-bank`) that stores corporate policies, counterparty agreements, and past negotiated concessions.
- **⚡ Precedent Recall & Risk Calibration:** Analyzes extracted counterparties and clauses, fetches precedents from Hindsight, and calibrates risk severities while badging clauses with `🧠 Hindsight Precedent`.
- **🛠️ Interactive "Teach Agent" Human-in-the-Loop:** Legal and procurement teams can teach the agent new policies and exceptions directly from the UI, immediately writing to persistent memory.
- **🤖 Autonomous Multi-Agent Pipeline:**
  1. Intake & Validation
  2. OCR & Text Processing
  3. Document Classification (MSA, NDA, SOW, SLA, etc.)
  4. Entity & Counterparty Extraction (NER)
  5. Clause Intelligence & Segmentation
  6. Obligation & Metric Extraction
  7. Risk Assessment & Severity Scoring
  8. Executive Summary Generation
  9. **Hindsight Memory Agent (Precedent Recall & Calibration)**
  10. Auto-Learning Retain Step
- **💬 Memory-Augmented Conversational Chat:** Context-aware assistant that references past contracts and recalled memory items to answer deep cross-contract queries.
- **📊 Interactive Legal Dashboard:** Risk Register with severity filters, Clause Intelligence viewer, Executive Brief, and a dedicated **Hindsight Memory Inspector** with Before/After comparison toggles.
- **📄 Export & Audit Trail:** Download analysis reports in PDF, JSON, and Markdown formats.

---

## 🔄 Before Memory vs. After Memory

| Dimension | ❌ Without Memory (Stateless AI) | ✅ With DocPilot AI (Hindsight Memory) |
| :--- | :--- | :--- |
| **Vendor Liability Review** | Flags 1x liability cap as **Critical Risk**. Demands standard 2x cap. | Recalls **Precedent #mem_seed_001**: Legal already approved 1x cap for Acme Corp due to cyber insurance. Auto-calibrates risk. |
| **Payment Terms** | Evaluates Net-45 in isolation with generic warning comments. | Validates against **Corporate Policy #mem_seed_002** (Net-30/45 standard) and confirms compliance. |
| **Human Feedback** | Forgets lawyer redlines immediately after the session. | **Retains** approvals and exceptions in Hindsight; subsequent contracts automatically respect the decision. |
| **Cross-Document Q&A** | Answers: *"I can only see the text in the currently uploaded document."* | Answers: *"Across your last 3 reviews with this vendor, you compromised on termination notice but held firm on mutual indemnification."* |

---

## 🏗️ Architecture

```
                               ┌────────────────────────────────────────────────────────┐
                               │           HINDSIGHT PERSISTENT MEMORY BANK             │
                               │      (Corporate Policies, Precedents, Vendor History)   │
                               └───────────────▲────────────────────────▲───────────────┘
                                               │ RECALL                 │ RETAIN
                                               │ (Fetch Precedents)     │ (Store Learnings)
                                               │                        │
[ Upload Document ] ──► [ Multi-Agent Pipeline ] ─┴──► [ Hindsight Memory Agent ] ──► [ Dashboard & AI Chat ]
                        • Classification               • Cross-Contract Insights      • Memory Inspector Tab
                        • Entity Extraction            • Risk Severity Calibration     • Precedent Citations
                        • Clause & Risk Analysis       • Auto-Learning Retain         • "Teach Agent" Live Form
```

---

## 💻 Tech Stack

### Frontend
- **Framework:** Next.js 14 (App Router) + React 18
- **Styling:** Tailwind CSS + Framer Motion animations
- **Icons:** Lucide React
- **State Management:** Reactive component hooks with real-time SSE progress

### Backend
- **Framework:** FastAPI (Python 3.11+) + Uvicorn
- **AI / LLM:** Google Gemini API (`gemini-1.5-pro` / `gemini-1.5-flash`)
- **Memory Engine:** Vectorize Hindsight Python SDK (`hindsight-client`) with resilient hybrid local bank fallback
- **Document Processing:** PyMuPDF, pdfminer, Pillow, Tesseract OCR fallback

---

## 🛠️ Getting Started

### Prerequisites
- **Python:** 3.11 or higher
- **Node.js:** 18.x or higher
- **Google Gemini API Key:** [Get an API key](https://aistudio.google.com/)
- **Vectorize Hindsight API Key:** [Vectorize Console](https://vectorize.io)

---

### 1. Clone the Repository
```bash
git clone https://github.com/kjeevankumar/DocPilotAI.git
cd DocPilotAI
```

---

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:
```env
# Server
PORT=8000
HOST=0.0.0.0

# LLM
GEMINI_API_KEY=your_gemini_api_key_here

# Vectorize Hindsight Memory
HINDSIGHT_API_KEY=your_hindsight_api_key_here
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_BANK_ID=docpilot-legal-bank
```

Start the backend server:
```bash
uvicorn main:app --reload --port 8000
```
Backend API will be running at: `http://localhost:8000`  
Interactive Swagger docs: `http://localhost:8000/docs`

---

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
Frontend application will be accessible at: `http://localhost:3000`

---

## 📂 Project Structure

```text
DocPilotAI/
├── HINDSIGHT_INTEGRATION.md     # In-depth architectural whitepaper & demo script
├── HINDSIGHT_INTEGRATION.pdf    # Publication-ready PDF submission report
├── DocPilot_Test_Agreement.pdf  # Sample contract for quick testing
├── README.md                    # Project documentation & overview
├── backend/
│   ├── agents/
│   │   ├── orchestrator.py      # Multi-agent workflow pipeline coordinator
│   │   ├── hindsight_memory_agent.py # Memory recall, precedent match & risk calibration
│   │   ├── context.py           # Shared analysis pipeline state
│   │   └── ...                  # Classification, Extraction, Risk Agents
│   ├── services/
│   │   ├── hindsight_service.py # Vectorize Hindsight SDK integration & bank manager
│   │   ├── gemini_service.py    # Google Gemini LLM reasoning service
│   │   └── document_parser.py   # Multi-format document text extraction
│   ├── data/
│   │   └── hindsight_local_bank.json # Seed corporate policies & precedent memories
│   ├── routers/
│   │   └── api.py               # REST API & SSE streaming endpoints
│   ├── config.py                # App configuration & environment loader
│   ├── requirements.txt         # Python dependencies
│   └── main.py                  # FastAPI application entry point
└── frontend/
    ├── src/
    │   ├── app/
    │   │   └── page.tsx         # Main entry point & upload workflow
    │   ├── components/
    │   │   ├── HindsightMemoryInspector.tsx # Memory Engine UI & "Teach Agent"
    │   │   ├── DashboardWorkspace.tsx       # Primary analysis dashboard
    │   │   ├── RiskRegister.tsx             # Risk view with precedent badging
    │   │   ├── ChatInterface.tsx            # Memory-augmented Q&A assistant
    │   │   └── ProcessingScreen.tsx         # Real-time multi-agent pipeline visualizer
    │   └── types/
    │       └── index.ts         # TypeScript interfaces & memory schemas
    ├── package.json
    └── tailwind.config.ts
```

---

## 🎬 Demo Walkthrough

We've included a ready-to-test agreement: `DocPilot_Test_Agreement.pdf`.

1. **Upload:** Drop `DocPilot_Test_Agreement.pdf` into the upload zone.
2. **Observe Pipeline:** Watch the 10-step multi-agent visualizer execute in real-time through OCR, classification, risk detection, and Hindsight Memory Recall.
3. **Inspect Memories:** Click the **🧠 Hindsight Memory Engine** tab to see recalled precedents for *Acme Corp* and corporate baseline comparisons.
4. **Calibrated Risks:** Open the **Risk Register** to see how the 1x liability cap was auto-calibrated from Critical to Low/Medium, citing precedent `#mem_seed_001`.
5. **Teach the Agent:** Click **"Teach Agent Policy"** to submit a new exception rule; watch it save directly into the memory bank.
6. **Cross-Contract Q&A:** Open the **AI Q&A Chat** and ask:
   > *"What liability terms did we agree on with Acme Corp in our previous negotiations?"*

---

## 📄 Documentation & Links

- 📖 **Architecture Guide & Demo Script:** [HINDSIGHT_INTEGRATION.md](HINDSIGHT_INTEGRATION.md)
- 📑 **Publication-Grade PDF Report:** [HINDSIGHT_INTEGRATION.pdf](HINDSIGHT_INTEGRATION.pdf)
- 🌐 **Vectorize Hindsight:** [vectorize.io](https://vectorize.io)

---

## 📜 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
