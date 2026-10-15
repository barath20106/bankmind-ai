# 🏦 BankMind AI

### Multi-Agent Banking Intelligence Platform

**Intelligent banking workflows powered by specialized agents, deterministic tools, and explainable execution traces.**

BankMind AI is a full-stack banking intelligence application that demonstrates how a coordinated multi-agent system can support simulated banking operations, transaction analysis, fraud investigation, loan assessment, and compliance monitoring through a unified interface.

<p align="center">
  <img src="https://img.shields.io/badge/Python-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="Python and FastAPI"/>
  <img src="https://img.shields.io/badge/React-TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="React and TypeScript"/>
  <img src="https://img.shields.io/badge/AI-Google%20Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white" alt="Google Gemini"/>
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite"/>
</p>

---

## ✨ Overview

Traditional banking workflows involve multiple responsibilities, from retrieving account information to examining suspicious transactions and assessing loan affordability. BankMind AI demonstrates how these responsibilities can be organized into specialized agents coordinated by a central Supervisor Agent.

The platform combines:

- A modern React and TypeScript frontend.
- A Python FastAPI backend.
- A supervisor-led multi-agent architecture.
- Deterministic banking tools and simulated financial data.
- Optional Google Gemini integration.
- Execution traces and application audit events.

The result is a unified environment for exploring AI-assisted banking workflows while keeping data retrieval and financial calculations grounded in application logic.

> **Important:** BankMind AI is an educational simulation. It is not connected to real banking infrastructure and must not be used for actual financial, lending, fraud, or regulatory decisions.

## 🚀 Key Features

### 🧠 Multi-Agent Orchestration

A central Supervisor Agent coordinates specialized agents according to the user's request. This separates responsibilities and makes supported workflows easier to understand and inspect.

### 🏦 Banking Intelligence

- Explore seeded customer and account records.
- Inspect simulated account balances and transactions.
- Analyze spending activity and cash-flow patterns.
- Retrieve banking information through application tools.

### 🛡️ Fraud and Risk Analysis

- Investigate suspicious transactions in the demo dataset.
- Evaluate risk indicators using application-defined rules.
- Review risk scores and severity classifications.
- Inspect recommended actions and related execution records where supported.

### 💳 Credit and Loan Assessment

- Calculate estimated monthly installments (EMIs).
- Examine debt-to-income (DTI) ratios.
- Explore simulated loan assessment results.
- Review the parameters behind affordability calculations.

### 📜 Compliance and Auditability

- Record relevant application events.
- Inspect the audit trail.
- Review execution traces from supported agent workflows.
- Understand how traceability can support banking-oriented applications.

### 💬 Interactive Banking Assistant

A unified conversational interface accepts supported banking requests and coordinates the relevant backend workflow.

### ⚙️ Flexible AI Integration

Google Gemini is supported through the `google-genai` SDK. Deterministic fallback behavior allows supported workflows to remain available when live AI integration is not configured or cannot be used.

---

## 🏗️ Architecture

BankMind AI follows a layered architecture that separates the user interface, API handling, agent orchestration, deterministic tools, and data storage.

### 1. Frontend Layer

**React · TypeScript · Vite · Tailwind CSS · Recharts**

The frontend provides an interactive dashboard and dedicated screens for banking operations, customer information, fraud investigation, credit assessment, audit events, execution traces, and model settings.

### 2. API Layer

**Python · FastAPI · Pydantic**

FastAPI exposes backend endpoints to the frontend. Pydantic supports structured input and output validation, while API routes connect incoming requests to the relevant application logic.

### 3. Agent Orchestration Layer

The Supervisor Agent acts as the coordination point for supported workflows.

| Agent | Responsibility |
|---|---|
| **Supervisor Agent** | Classifies requests, coordinates specialist workflows, and synthesizes responses |
| **Banking Agent** | Handles account, balance, transaction, and spending-related operations |
| **Risk & Fraud Agent** | Evaluates suspicious transactions and risk indicators using application rules |
| **Credit & Loan Agent** | Supports EMI calculations, DTI analysis, and simulated loan assessment |
| **Compliance Agent** | Supports policy-related checks and audit logging |

### 4. Deterministic Tools Layer

Specialized agents use Python tools to retrieve simulated banking data or perform supported calculations.

Examples include:

- Account and balance retrieval.
- Transaction lookup and spending analysis.
- Rule-based fraud risk evaluation.
- Loan installment and affordability calculations.
- Audit event operations.

These tools return structured results that can be used by the surrounding agent workflow.

### 5. Data and Observability Layer

**SQLite · SQLAlchemy · Execution Traces · Audit Events**

SQLite stores the application's simulated records, with SQLAlchemy providing database access. Execution traces help expose workflow activity, while audit events record relevant application operations.

### Request lifecycle

1. A user submits a question or initiates a banking operation.
2. FastAPI receives and validates the request.
3. The Supervisor Agent classifies and coordinates the supported workflow.
4. A specialist agent invokes the appropriate application tools.
5. Tools retrieve data or perform deterministic calculations.
6. Structured results return to the orchestration layer.
7. The application synthesizes a response and records relevant execution or audit information.

This separation makes the application easier to navigate, maintain, and extend.

---

## 🤖 AI Integration and Fallback

BankMind AI supports Google Gemini through the official `google-genai` SDK.

### Google Gemini mode

When a valid API key is configured and the provider is available, supported AI operations can use the configured Gemini model.

### Deterministic demo mode

When the AI provider is not configured or cannot be used, supported workflows can fall back to deterministic behavior.

### Why combine AI with deterministic tools?

| AI-assisted operations | Deterministic operations |
|---|---|
| Supported natural-language processing | Account and transaction retrieval |
| Request classification and orchestration support | Financial formula calculations |
| Response synthesis | Application-defined risk rules |
| Conversational interaction | Structured data and tool results |

The exact responsibilities depend on the implemented workflow. AI-generated text should not replace verified application data or deterministic calculations.

---

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| React | Component-based user interface |
| TypeScript | Frontend type safety |
| Vite | Frontend development and build tooling |
| Tailwind CSS | Interface styling |
| Recharts | Charts and data visualization |
| Python | Backend implementation |
| FastAPI | API gateway and request handling |
| Pydantic | Data validation |
| SQLAlchemy | Database access |
| SQLite | Local simulated banking database |
| Google Gemini | Optional AI integration |
| `google-genai` | Google Gen AI SDK |
| pytest | Backend automated testing |

---

## 📁 Project Structure

```text
bankmind-ai/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── banking.py
│   │   │   ├── compliance.py
│   │   │   ├── credit_loan.py
│   │   │   ├── risk_fraud.py
│   │   │   └── supervisor.py
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── tools/
│   │   ├── main.py
│   │   └── seed.py
│   ├── tests/
│   ├── .env.example
│   ├── requirements.txt
│   └── verify_e2e.py
├── frontend/
│   ├── public/
│   └── src/
│       ├── assets/
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── types/
│       ├── App.tsx
│       └── main.tsx
├── ARCHITECTURE.md
├── DEMO_SCRIPT.md
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚡ Getting Started

### Prerequisites

Install the following:

- Git
- Python 3.11 or a compatible version supported by the project dependencies
- Node.js and npm

### 1. Clone the repository

```bash
git clone https://github.com/barath20106/bankmind-ai.git
cd bankmind-ai
```

### 2. Set up the backend

From the project root, open PowerShell:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Open `backend/.env` and configure the Gemini settings if you want live AI integration:

```dotenv
GEMINI_API_KEY=your_actual_api_key
GEMINI_MODEL=gemini-2.5-flash
```

Replace the placeholder locally with your own API key. **Never commit a real API key to GitHub.**

If no key is configured, use the supported deterministic demo mode.

Start the backend from the `backend` directory:

```powershell
uvicorn app.main:app --reload
```

The default local endpoints are:

- Backend API: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

### 3. Set up the frontend

Open a second terminal in the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite. The default development URL is:

`http://localhost:5173`

Keep both development servers running while using the application.

> If your environment uses a different Python launcher, port, or configuration, follow the existing project settings and terminal output.

---

## 🧪 Testing

Automated backend tests are located in `backend/tests`.

After installing the backend dependencies, run the test suite from the project root:

```bash
python -m pytest backend/tests -v
```

Use the Python executable from your project's virtual environment if necessary.

An end-to-end verification script is also included at `backend/verify_e2e.py`.

---

## 🔐 Security and Responsible Use

BankMind AI is an educational prototype, not a production banking system.

- It uses simulated or seeded banking records.
- It is not connected to real bank accounts or payment networks.
- Fraud indicators are application-generated results, not proof of criminal activity.
- Loan eligibility results are simulations, not lending decisions.
- Compliance workflows demonstrate application-level checks and logging; they do not establish regulatory certification.
- Audit events and execution traces support inspection but should not be considered tamper-proof without additional integrity protections.
- AI provider availability and output quality depend on configuration and provider behavior.
- Production use would require appropriate authentication, authorization, data protection, security reviews, monitoring, and human oversight.

### API key safety

- Store credentials in local `.env` files.
- Keep real environment files excluded from version control.
- Commit only placeholder configuration in `.env.example`.
- Rotate any credential that has been exposed.

---

## 📚 Related Documentation

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — detailed system architecture and design.
- [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md) — application walkthrough and demonstration flow.

---

<p align="center">
  <strong>BankMind AI</strong><br/>
  Specialized agents. Grounded tools. Traceable workflows.
</p>
