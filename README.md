# BankMind AI — Multi-Agent Banking Intelligence Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4+-38bdf8.svg)](https://tailwindcss.com)
[![Tests Passing](https://img.shields.io/badge/tests-35%20passed-emerald.svg)]()
[![License](https://img.shields.io/badge/license-MIT-gray.svg)]()

> **Technical Assessment Submission**: *Build an Application for Simulated Real-Time Banking Architecture with Multi-Agent Automation using Experimental Models.*

---

## 1. Project Overview

**BankMind AI** is a simulated real-time banking operations and intelligence platform. It features an autonomous **Supervisor Agent** that orchestrates specialized domain agents (**Banking**, **Risk & Fraud**, **Credit & Loan**, **Compliance**). 

Instead of relying on ungrounded LLM narratives, BankMind AI routes user inquiries to specialized agents that invoke actual, typed Python banking tools backed by an ACID-compliant **SQLite** database.

### Key Highlights
- **Grounded Multi-Agent System**: Supervisor classifies intent, coordinates specialist agents, calls real Python banking tools, and formats grounded responses.
- **Dual-Mode AI Engine**: Seamless integration with **Google Gemini** (`gemini-2.5-flash`) via the official `google-genai` SDK, with an automated fallback to **Deterministic Demo Mode** when an API key is not configured.
- **9 Professional Operations Screens**:
  1. Executive Dashboard (KPIs & Volume Charts)
  2. AI Banking Assistant (Interactive Chat & Real-Time Telemetry Timeline)
  3. Customer Directory & Account Profile
  4. Accounts & Transaction Ledger
  5. Fraud & Risk Surveillance Center (Deterministic Rule Investigator)
  6. Credit Underwriting & Loan Eligibility (Interactive EMI & DTI Simulator)
  7. Multi-Agent Execution Traces (Step-by-step Telemetry & JSON Payloads)
  8. Regulatory & Compliance Audit Trail (Immutable Security Logs)
  9. Settings & Model Status (Gemini Provider Status & Health)
- **Comprehensive Test Suite**: 35 automated tests covering banking tools, fraud heuristics, amortization math, supervisor routing, API routes, and edge cases.

---

## 2. Architecture & Data Flow

`````````mermaid
flowchart TD
    User["Bank Operator / Customer"] --> UI["BankMind AI Web UI (React + Vite + Tailwind)"]
    UI -->|REST and Chat Endpoints| API["FastAPI Application Gateway"]

    subgraph MultiAgentEngine["Multi-Agent Orchestration Layer"]
        API --> Orchestrator["Orchestration Engine"]
        Orchestrator --> Supervisor["Supervisor Agent"]
        Supervisor -->|Classify and Route| Provider["Google Gemini / Deterministic Fallback Router"]

        Supervisor -->|Account and Balances| BA["Banking Agent"]
        Supervisor -->|Fraud and Risk Rules| RA["Risk and Fraud Agent"]
        Supervisor -->|EMI and DTI Underwriting| CA["Credit and Loan Agent"]
        Supervisor -->|Policy and Governance| COMP["Compliance Agent"]
    end

    subgraph ToolsStorage["Deterministic Python Tools and SQLite"]
        BA --> Tools["Simulated Banking Tools Layer"]
        RA --> Tools
        CA --> Tools
        COMP --> Tools

        Tools --> DB[("SQLite Database - Seeded Demo Records")]
        COMP --> AuditLog[("Audit Trail")]
        Supervisor --> TracesLog[("Execution Traces Store")]
    end

    Tools -->|Typed Result Dictionaries| Supervisor
    Supervisor -->|Grounded Answer and Traces| API
    API -->|JSON with Telemetry| UI
```

---

## 3. Technology Stack

- **Backend**:
  - Python 3.11+
  - FastAPI (REST API with Pydantic v2 schemas)
  - SQLAlchemy 2.0 (ORM)
  - SQLite (Local ACID database with WAL mode)
  - Google Gen AI Python SDK (`google-genai`)
  - Pytest & HTTPX (Automated test suite)
- **Frontend**:
  - React 19 (TypeScript)
  - Vite (Build tool & HMR)
  - Tailwind CSS (Dark navy sidebar, light-gray content panels, blue/teal accents)
  - Lucide React (Icons)
  - Recharts (Interactive telemetry and clearing volume charts)

---

## 4. Prerequisites

- **Python 3.11 or higher**
- **Node.js 18 or higher** (LTS recommended)
- **npm 9+**

---

## 5. Installation & Setup

### Clone and Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-username/bankmind-ai.git
cd bankmind-ai
```

### Backend Setup

#### Windows PowerShell:
```powershell
# 1. Create Python virtual environment
python -m venv .venv

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Install backend dependencies
pip install -r backend\requirements.txt

# 4. (Optional) Configure environment variables
# Copy template
Copy-Item backend\.env.example backend\.env
```

#### macOS / Linux:
```bash
# 1. Create Python virtual environment
python3 -m venv .venv

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Install backend dependencies
pip install -r backend/requirements.txt

# 4. (Optional) Configure environment variables
cp backend/.env.example backend/.env
```

> **Note on GEMINI_API_KEY**:
> If you have a Google Gemini API key, add it to `backend/.env`:
> ```env
> GEMINI_API_KEY=your_actual_api_key_here
> GEMINI_MODEL=gemini-2.5-flash
> ```
> **If no API key is provided**, BankMind AI automatically activates **Deterministic Demo Mode**. All 5 required use cases and dashboard functions run with 100% functionality without requiring an external API key!

---

### Frontend Setup

```bash
cd frontend
npm install
cd ..
```

---

## 6. Running the Application

### 1. Start the FastAPI Backend
Open a terminal in the project root:

**Windows PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH="backend"
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**macOS / Linux:**
```bash
source .venv/bin/activate
export PYTHONPATH="backend"
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*The database automatically creates and seeds demo records on first startup.*
- API documentation: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/health`

### 2. Start the React Frontend
Open a second terminal in the project root:

```bash
cd frontend
npm run dev
```
Open your browser to: **`http://localhost:5173`**

---

## 7. Running Automated Tests & Verification

### Run Pytest Backend Test Suite (35 Tests)
```powershell
# Windows
$env:PYTHONPATH="backend"
.\.venv\Scripts\pytest -v backend\tests

# macOS / Linux
export PYTHONPATH="backend"
pytest -v backend/tests
```

### Run End-to-End Use Case Verification Script
```powershell
# Runs all 5 required use cases through supervisor agent
python backend/verify_e2e.py
```

### Run Frontend Typecheck & Production Build
```bash
cd frontend
npm run build
```

---

## 8. Five Core Assessment Use Cases

| Use Case | Natural-Language Prompt | Specialist Agent(s) | Expected Grounded Tool Execution |
| :--- | :--- | :--- | :--- |
| **UC 1: Account Inquiry** | *"What is the current balance of customer CUST-1001?"* | `BankingAgent` | Invokes `get_customer` & `get_accounts`. Returns ₹185,420.50 (Savings) + ₹42,300.00 (Salary). Combined: ₹227,720.50. |
| **UC 2: Transaction Analysis** | *"Show the last 10 transactions for customer CUST-1001 and summarize their spending."* | `BankingAgent` | Invokes `get_transactions` & `calculate_spending_summary`. Calculates Debits (₹354,350), Credits (₹95,000), Net Cashflow, and category distribution. |
| **UC 3: Fraud Investigation** | *"Investigate transaction TXN-3001. Why was it flagged?"* | `RiskFraudAgent`, `ComplianceAgent` | Invokes `analyze_transaction_risk`. Returns **Risk Score: 100/100 (CRITICAL)**. Reasons: Offshore Dubai wire exceeding ₹200k threshold. Recommended action: `BLOCK_AND_VERIFY`. |
| **UC 4: Loan Underwriting** | *"Can customer CUST-1002 qualify for a loan of ₹300000 over 36 months?"* | `CreditLoanAgent`, `ComplianceAgent` | Invokes `calculate_loan_eligibility`. Evaluates Priya Patel (Score: 780). Computes monthly EMI ₹9,609.88, DTI 13.26% (ceiling 40%). Result: **APPROVED (ELIGIBLE)**. |
| **UC 5: Cross-Agent Review** | *"Review customer CUST-1001's spending, check for suspicious activity, and suggest whether a loan payment would be affordable."* | `BankingAgent`, `RiskFraudAgent`, `CreditLoanAgent`, `ComplianceAgent` | **11-step execution**: Aggregates liquidity surplus, detects critical flag on TXN-3001, calculates hypothetical EMI, and synthesizes unified recommendation. |

---

## 9. API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check, DB status, active LLM provider/model metadata |
| `GET` | `/api/dashboard/summary` | Summary cards, clearing volume chart series, recent activity |
| `GET` | `/api/customers` | Searchable customer list with pagination |
| `GET` | `/api/customers/{id}` | Customer profile details |
| `GET` | `/api/customers/{id}/accounts` | Linked accounts and balances for customer |
| `GET` | `/api/customers/{id}/transactions` | Filtered transaction history for customer |
| `GET` | `/api/accounts` | All simulated bank accounts |
| `GET` | `/api/transactions` | Full ledger with category and flag filters |
| `GET` | `/api/fraud/alerts` | Active surveillance alerts queue |
| `POST` | `/api/fraud/analyze` | Deterministic fraud risk analysis for any transaction ID |
| `GET` | `/api/loans` | Historical and active loan applications |
| `POST` | `/api/loans/eligibility` | Automated underwriting calculator (DTI, EMI, score) |
| `POST` | `/api/loans/emi` | Standard loan amortization calculation |
| `POST` | `/api/chat` | AI Banking Assistant endpoint returning answer + execution traces |
| `GET` | `/api/agents` | Agent registry with capabilities and registered tools |
| `GET` | `/api/traces` | Multi-agent execution telemetry and payloads |
| `GET` | `/api/audit` | Immutable compliance and governance events log |

---

## 10. Troubleshooting

- **Port 8000 or 5173 in use**:
  - FastAPI: change `--port 8001` and update `vite.config.ts` target.
  - Vite: Vite automatically selects the next available port (e.g. 5174).
- **Missing or corrupted database**:
  - Run `python backend/app/seed.py` to recreate and seed `bankmind.db`.
- **Node.js path issues on Windows**:
  - Ensure Node.js is in your environment PATH: `Get-Command node`.

---

## 11. Security & Compliance Disclaimer

> **IMPORTANT**: BankMind AI is an educational simulation built for technical assessment and demonstration purposes. All customer identities, accounts, transaction amounts, credit scores, and fraud alerts are fictional. No actual financial transactions or binding credit sanctions are performed. Real banking credentials should never be input into this application.
