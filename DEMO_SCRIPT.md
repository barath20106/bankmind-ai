# BankMind AI — 5–10 Minute Technical Demonstration Script

## Demonstration Overview

- **Audience**: Technical Assessment Evaluators, Engineering Leadership, Pair Programmers.
- **Estimated Duration**: 7–10 minutes.
- **Core Narrative**: Demonstrate how BankMind AI solves the challenge of autonomous banking automation by replacing opaque LLM hallucinations with a deterministic multi-agent supervisor that invokes typed Python banking tools backed by a SQLite source of truth.

---

## Pre-Demo Checklist

1. Backend running on `http://127.0.0.1:8000`:
   ```powershell
   # Windows PowerShell
   .\.venv\Scripts\uvicorn app.main:app --port 8000 --reload
   ```
2. Frontend running on `http://localhost:5173`:
   ```powershell
   # In frontend/ directory
   npm run dev
   ```
3. Open browser to `http://localhost:5173`.
4. Ensure the database is seeded (seeded automatically on startup).

---

## Act 1: Executive Dashboard & Operational Telemetry (1 min)

### Screen: Overview Dashboard (`/overview`)
- **Talking Point**: 
  > *"Welcome to BankMind AI. This is a multi-agent banking operations intelligence platform. Notice the executive dashboard displaying real-time telemetry from our simulated SQLite database: 8 seeded fictional customers, 11 active accounts with over ₹2.4 Million in liquid deposits, and 45 realistic transactions."*
- **UI Highlights**:
  - Point to the **Surveillance Flags** card (highlighting active fraud alerts).
  - Point to the **Weekly Clearing Volume** chart rendered with Recharts.
  - Point to the **Recent Transactions** stream showing real-time ledger entries.
  - Notice the **Active Engine Badge** in the top header (`Deterministic Demo Mode` or `Live Gemini 2.5 Flash`).

---

## Act 2: Use Case 1 — Customer Account Inquiry (1 min)

### Screen: AI Assistant (`/assistant`)
- **Action**: Click the suggested prompt chip or type:
  ```text
  What is the current balance of customer CUST-1001?
  ```
- **Talking Point**:
  > *"Here, the Supervisor Agent accepts the user's natural-language inquiry. Instead of making up an answer, it decomposes the intent into an `ACCOUNT_INQUIRY` and delegates execution to the `BankingAgent`."*
- **Observed Behavior**:
  - The BankingAgent calls `get_customer('CUST-1001')` and `get_accounts('CUST-1001')`.
  - The assistant returns Rajesh Sharma's active accounts:
    - **Savings Account (`SBIN004819201`)**: ₹1,85,420.50
    - **Salary Account (`SBIN004819202`)**: ₹42,300.00
    - Combined Total Liquid Deposits: ₹2,27,720.50.
- **Telemetry Inspection**:
  - Click on the message to inspect the right-hand **Agent Execution Telemetry** drawer.
  - Point to the step sequence (`classify_intent`, `get_customer`, `get_accounts`, `synthesize_grounded_response`) and latency (~5ms).

---

## Act 3: Use Case 2 — Transaction Analysis & Spending (1.5 min)

### Screen: AI Assistant (`/assistant`)
- **Action**: Click the prompt chip or type:
  ```text
  Show the last 10 transactions for customer CUST-1001 and summarize their spending.
  ```
- **Talking Point**:
  > *"In this use case, the BankingAgent retrieves transaction records and computes mathematical spending aggregates directly in Python before presenting them."*
- **Observed Behavior**:
  - Returns total debits (₹3,54,350.00) vs credits (₹95,000.00).
  - Outlines category spending: Grocery, Electronics, Travel, Utilities, and Overseas Forex Desk.
  - Displays individual transaction ledger entries with date, merchant, location, and amounts formatted in INR (₹).

---

## Act 4: Use Case 3 — Fraud Investigation & Surveillance (2 min)

### Screen: AI Assistant (`/assistant`) & Fraud Center (`/fraud`)
- **Action 1 (in Chat)**: Type:
  ```text
  Investigate transaction TXN-3001. Why was it flagged?
  ```
- **Talking Point**:
  > *"When an inquiry involves security or fraud, the Supervisor routes to the `RiskFraudAgent`. The agent runs deterministic AML rules rather than generic LLM guesses."*
- **Observed Behavior**:
  - The RiskFraudAgent calls `analyze_transaction_risk('TXN-3001')`.
  - Returns **Risk Score: 100/100 (CRITICAL)**.
  - Outlines the exact deterministic rules triggered:
    1. High-risk merchant category: *Overseas Forex Desk*.
    2. AML statutory threshold: ₹275,000 exceeds ₹200,000 ceiling.
    3. Geographic anomaly: Dubai IP origin differs from customer domicile (Mumbai).
  - Action recommended: `BLOCK_AND_VERIFY`.
- **Action 2 (Navigate to `/fraud`)**:
  - Switch to the **Fraud & Risk** tab in the sidebar.
  - Show the **Interactive Deterministic Risk Investigator**.
  - Click on the test preset `TXN-3017` (Crypto P2P in Zurich) or `TXN-3019` (Velocity Structuring).
  - Demonstrate instant re-evaluation with visual score meters.

---

## Act 5: Use Case 4 — Credit Underwriting & Loan Eligibility (1.5 min)

### Screen: Credit & Loans (`/credit`)
- **Action 1 (in Chat or Credit screen)**:
  ```text
  Can customer CUST-1002 qualify for a loan of ₹300000 over 36 months?
  ```
- **Talking Point**:
  > *"Credit underwriting requires strict mathematical precision. The `CreditLoanAgent` calls real financial amortization tools for EMI and checks Debt-to-Income (DTI) caps."*
- **Observed Behavior**:
  - Evaluates Priya Patel (`CUST-1002`, income ₹1,45,000/mo, credit score 780).
  - Computes monthly EMI: ₹9,609.88 at 9.5% p.a.
  - Calculates DTI ratio: 13.26% (well below the 40% prudential ceiling).
  - Result: **APPROVED (ELIGIBLE)** with simulated non-binding label.
- **Action 2 (Negative Test)**:
  - On the `/credit` interactive simulator, switch the target customer to `CUST-1007` (Rohan Mehra).
  - Notice the instant rejection: KYC status is `PENDING`, triggering mandatory compliance rejection under policy `KYC-VERIF-02`.

---

## Act 6: Use Case 5 — Cross-Agent Financial Assistance (2 min)

### Screen: AI Assistant (`/assistant`)
- **Action**: Type the cross-agent prompt:
  ```text
  Review customer CUST-1001's spending, check for suspicious activity, and suggest whether a loan payment would be affordable.
  ```
- **Talking Point**:
  > *"This is the benchmark multi-agent scenario. The Supervisor must coordinate multiple specialists in a single workflow: BankingAgent for liquidity, RiskFraudAgent for active surveillance flags, CreditLoanAgent for debt affordability, and ComplianceAgent for policy audit."*
- **Observed Behavior**:
  - **11 discrete execution steps** recorded in telemetry.
  - BankingAgent reports liquidity: ₹2,27,720.50 balance across 2 accounts.
  - RiskFraudAgent warns: Active critical flag on `TXN-3001` (₹2,75,000 offshore wire).
  - CreditLoanAgent reports: Mathematical EMI of ₹9,609.88 is within income ratios.
  - **Supervisor Executive Synthesis**: While mathematically serviceable, sanction is put on hold until active fraud surveillance flags are resolved.

---

## Act 7: Execution Traces, Audit Log & Settings (1 min)

### Screen: Agent Traces (`/traces`) & Audit Log (`/audit`)
- **Talking Point**:
  > *"For compliance and debugging, every single multi-agent tool execution is immutably recorded."*
- **UI Highlights**:
  - Show the **Agent Traces** table: Click *Inspect* to view the raw JSON inputs and outputs of any tool invocation.
  - Show the **Audit Log**: Point to immutable events logged by the `ComplianceAgent`.
  - Show the **Settings & Model Status** page: Verify the active Gemini model or Deterministic Demo Mode status.

---

## Conclusion & Wrap-Up

> *"In summary, BankMind AI demonstrates a complete, reliable, end-to-end multi-agent banking system. It combines user-friendly conversational AI with deterministic mathematical guardrails, robust test coverage (35 automated tests), and a high-performance modern UI. Thank you."*
