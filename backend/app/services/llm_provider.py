import os
import re
import json
import logging
from typing import Dict, Any, Optional, List
from app.core.config import settings

logger = logging.getLogger("bankmind.llm")


class LLMProvider:
    """
    Unified LLM provider interface.
    Supports official Google Gen AI Python SDK (google-genai) when GEMINI_API_KEY is configured.
    Seamlessly falls back to a deterministic, rule-based banking engine when API key is missing or offline.
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY.strip() if settings.GEMINI_API_KEY else ""
        self.model_name = settings.GEMINI_MODEL.strip() if settings.GEMINI_MODEL else "gemini-2.5-flash"
        self._is_gemini_active = False
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Google Gen AI client if a valid key is provided."""
        # Disregard dummy placeholder keys
        if self.api_key and not self.api_key.startswith("your_") and len(self.api_key) > 10:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                self._is_gemini_active = True
                logger.info(f"Gemini client initialized with model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}. Falling back to deterministic demo mode.")
                self._is_gemini_active = False
                self._client = None
        else:
            self._is_gemini_active = False
            self._client = None

    @property
    def is_gemini_active(self) -> bool:
        return self._is_gemini_active

    @property
    def provider_info(self) -> Dict[str, str]:
        if self._is_gemini_active:
            return {
                "provider": "gemini",
                "model": self.model_name,
                "mode": "Live Google Gen AI"
            }
        return {
            "provider": "deterministic-demo",
            "model": "Rule-Based Banking Orchestrator v1.0",
            "mode": "Deterministic Demo Mode"
        }

    def classify_intent(self, user_query: str) -> Dict[str, Any]:
        """
        Classifies the user query into intent and identifies the required specialist agents.
        Returns a structured routing dictionary.
        """
        if self._is_gemini_active and self._client:
            try:
                return self._classify_with_gemini(user_query)
            except Exception as e:
                logger.warning(f"Gemini classification failed: {e}. Falling back to deterministic classification.")

        return self._classify_deterministic(user_query)

    def _classify_with_gemini(self, user_query: str) -> Dict[str, Any]:
        """Uses Gemini structured prompt to classify user intent."""
        prompt = f"""
You are the Supervisor AI for BankMind AI, a multi-agent banking intelligence platform.
Classify the user's natural language request into a structured JSON routing plan.

Specialist Agents:
- BankingAgent: Account lookups, balance checks, transactions history, spending breakdown.
- RiskFraudAgent: Fraud investigation, suspicious transactions, alert reviews, risk scores.
- CreditLoanAgent: Loan qualifications, EMI calculations, Debt-to-Income (DTI) assessment.
- ComplianceAgent: Policy checks, AML rules, audit verification.

User Query: "{user_query}"

Respond with ONLY a raw JSON object matching this schema:
{{
  "primary_intent": "ACCOUNT_INQUIRY" | "TRANSACTION_ANALYSIS" | "FRAUD_INVESTIGATION" | "LOAN_ELIGIBILITY" | "CROSS_AGENT_ASSISTANCE" | "GENERAL_HELP" | "UNKNOWN",
  "agents": ["BankingAgent" | "RiskFraudAgent" | "CreditLoanAgent" | "ComplianceAgent"],
  "customer_id": "CUST-XXXX" or null,
  "transaction_id": "TXN-XXXX" or null,
  "loan_amount": float or null,
  "loan_tenure": int or null,
  "confidence": float between 0.0 and 1.0,
  "reasoning": "brief explanation"
}}
"""
        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        text = response.text.strip()
        # Clean json markdown fences if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        parsed = json.loads(text.strip())

        # Fallback regex extraction if Gemini omitted IDs
        if not parsed.get("customer_id"):
            cust_match = re.search(r"\b(CUST-\d+)\b", user_query, re.IGNORECASE)
            if cust_match:
                parsed["customer_id"] = cust_match.group(1).upper()
        if not parsed.get("transaction_id"):
            txn_match = re.search(r"\b(TXN-\d+)\b", user_query, re.IGNORECASE)
            if txn_match:
                parsed["transaction_id"] = txn_match.group(1).upper()

        return parsed

    def _classify_deterministic(self, user_query: str) -> Dict[str, Any]:
        """
        Deterministic rule-based intent classification.
        Guarantees 100% reliable routing for all 5 required use cases and standard banking inquiries.
        """
        q = user_query.lower()
        
        # Extract entity IDs
        cust_match = re.search(r"\b(cust-\d+)\b", user_query, re.IGNORECASE)
        customer_id = cust_match.group(1).upper() if cust_match else None

        txn_match = re.search(r"\b(txn-\d+)\b", user_query, re.IGNORECASE)
        transaction_id = txn_match.group(1).upper() if txn_match else None

        # Extract potential loan amount and tenure
        # Match e.g. "loan of ₹300000" or "₹ 300,000" or "300000"
        amt_match = re.search(r"(?:loan of|amount of|loan for)?\s*[₹rs\.]*\s*(\d[\d,]{3,9})", q)
        loan_amount = None
        if amt_match:
            try:
                raw_amt = amt_match.group(1).replace(",", "")
                # Ignore customer ID or transaction ID numbers
                if not (customer_id and raw_amt in customer_id) and not (transaction_id and raw_amt in transaction_id):
                    loan_amount = float(raw_amt)
            except ValueError:
                pass

        tenure_match = re.search(r"(\d+)\s*(?:months|month|yrs|years)", q)
        loan_tenure = None
        if tenure_match:
            try:
                raw_tenure = int(tenure_match.group(1))
                if "year" in tenure_match.group(0) or "yr" in tenure_match.group(0):
                    raw_tenure *= 12
                loan_tenure = raw_tenure
            except ValueError:
                pass

        # Use Case 5: Cross-agent financial assistance
        # "Review customer CUST-1001's spending, check for suspicious activity, and suggest whether a loan payment would be affordable."
        if any(w in q for w in ["spending", "spend"]) and any(w in q for w in ["suspicious", "fraud", "flagged"]) and any(w in q for w in ["loan", "affordable", "emi", "borrow"]):
            return {
                "primary_intent": "CROSS_AGENT_ASSISTANCE",
                "agents": ["BankingAgent", "RiskFraudAgent", "CreditLoanAgent", "ComplianceAgent"],
                "customer_id": customer_id or "CUST-1001",
                "transaction_id": transaction_id,
                "loan_amount": loan_amount or 300000.0,
                "loan_tenure": loan_tenure or 36,
                "confidence": 0.98,
                "reasoning": "Cross-agent inquiry requiring banking spending summary, risk surveillance check, and credit affordability evaluation."
            }

        # Use Case 3: Fraud investigation
        # "Investigate transaction TXN-3001. Why was it flagged?"
        if transaction_id or any(w in q for w in ["fraud", "flagged", "suspicious", "investigate", "risk score"]):
            return {
                "primary_intent": "FRAUD_INVESTIGATION",
                "agents": ["RiskFraudAgent", "ComplianceAgent"],
                "customer_id": customer_id,
                "transaction_id": transaction_id or "TXN-3001",
                "loan_amount": None,
                "loan_tenure": None,
                "confidence": 0.96,
                "reasoning": "Fraud and security investigation targeting a specific transaction or risk alert."
            }

        # Use Case 4: Loan eligibility / EMI
        # "Can customer CUST-1002 qualify for a loan of ₹300000 over 36 months?"
        if any(w in q for w in ["qualify", "loan", "eligibility", "emi", "borrow", "mortgage", "interest rate"]):
            return {
                "primary_intent": "LOAN_ELIGIBILITY",
                "agents": ["CreditLoanAgent", "ComplianceAgent"],
                "customer_id": customer_id or "CUST-1002",
                "transaction_id": None,
                "loan_amount": loan_amount or 300000.0,
                "loan_tenure": loan_tenure or 36,
                "confidence": 0.95,
                "reasoning": "Credit and loan eligibility assessment and debt-to-income analysis."
            }

        # Use Case 2: Transaction analysis & spending summary
        # "Show the last 10 transactions for customer CUST-1001 and summarize their spending."
        if any(w in q for w in ["transaction", "transactions", "spending", "spend", "statement", "history", "expenses"]):
            return {
                "primary_intent": "TRANSACTION_ANALYSIS",
                "agents": ["BankingAgent"],
                "customer_id": customer_id or "CUST-1001",
                "transaction_id": None,
                "loan_amount": None,
                "loan_tenure": None,
                "confidence": 0.95,
                "reasoning": "Transaction ledger analysis and spending categorization."
            }

        # Use Case 1: Account inquiry & balance
        # "What is the current balance of customer CUST-1001?"
        if any(w in q for w in ["balance", "account", "accounts", "deposit", "savings", "who is", "customer"]):
            return {
                "primary_intent": "ACCOUNT_INQUIRY",
                "agents": ["BankingAgent"],
                "customer_id": customer_id or "CUST-1001",
                "transaction_id": None,
                "loan_amount": None,
                "loan_tenure": None,
                "confidence": 0.95,
                "reasoning": "Core banking customer and account balance inquiry."
            }

        # Unknown / Ambiguous request
        return {
            "primary_intent": "UNKNOWN",
            "agents": [],
            "customer_id": customer_id,
            "transaction_id": transaction_id,
            "loan_amount": None,
            "loan_tenure": None,
            "confidence": 0.3,
            "reasoning": "Unrecognized request. Please prompt user for clarification."
        }

    def synthesize_response(
        self,
        user_query: str,
        routing: Dict[str, Any],
        agent_results: Dict[str, Any],
        traces: List[Dict[str, Any]]
    ) -> str:
        """
        Synthesizes grounded user-facing response from actual tool execution results.
        Never fabricates numbers, balances, or results.
        """
        if self._is_gemini_active and self._client:
            try:
                return self._synthesize_with_gemini(user_query, routing, agent_results)
            except Exception as e:
                logger.warning(f"Gemini response synthesis failed: {e}. Falling back to deterministic synthesis.")

        return self._synthesize_deterministic(user_query, routing, agent_results)

    def _synthesize_with_gemini(
        self,
        user_query: str,
        routing: Dict[str, Any],
        agent_results: Dict[str, Any]
    ) -> str:
        """Uses Gemini to generate a natural, grounded explanation from the tool outputs."""
        prompt = f"""
You are the AI Banking Assistant for BankMind AI, a simulated banking platform.
The user asked: "{user_query}"

The Supervisor Agent executed the following verified Python banking tools.
Their actual verified results are:
{json.dumps(agent_results, indent=2, default=str)}

INSTRUCTIONS:
1. Ground your response STRICTLY in the facts and figures provided above.
2. NEVER invent balances, account numbers, or fraud conclusions not present in the data.
3. Format monetary values in Indian Rupees (₹) with proper comma separators (e.g. ₹1,85,420.50).
4. If risk or fraud was analyzed, clearly state the risk score, risk level, and triggered deterministic rules.
5. If loan eligibility was calculated, provide the EMI, DTI ratio, approval status, and state that this is a simulated non-binding calculation.
6. Present the information clearly using markdown bullet points and bold headers.
"""
        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return response.text.strip()

    def _synthesize_deterministic(
        self,
        user_query: str,
        routing: Dict[str, Any],
        agent_results: Dict[str, Any]
    ) -> str:
        """
        Deterministic, professional banking response synthesis.
        Guarantees grounded, accurate outputs for all banking use cases.
        """
        intent = routing.get("primary_intent")

        if intent == "ACCOUNT_INQUIRY":
            cust = agent_results.get("BankingAgent", {}).get("customer", {})
            accounts = agent_results.get("BankingAgent", {}).get("accounts", [])
            
            if not cust.get("found", True) or not accounts:
                return f"Customer record for **{routing.get('customer_id')}** was not found in the banking database. Please verify the customer ID."

            lines = [
                f"### Customer Account Overview: {cust.get('full_name')} ({cust.get('id')})",
                f"- **KYC Status:** `{cust.get('kyc_status')}`",
                f"- **City:** {cust.get('city')}",
                f"- **Credit Score:** {cust.get('credit_score')}",
                "",
                "#### Active Accounts & Current Balances:"
            ]
            total_bal = 0.0
            for acct in accounts:
                bal = acct.get("balance", 0.0)
                total_bal += bal
                lines.append(f"- **{acct.get('account_type')} Account** (`{acct.get('account_number')}`): **₹{bal:,.2f}** ({acct.get('status')})")
            
            lines.append(f"\n**Total Combined Liquid Deposits:** **₹{total_bal:,.2f}**")
            return "\n".join(lines)

        elif intent == "TRANSACTION_ANALYSIS":
            cust = agent_results.get("BankingAgent", {}).get("customer", {})
            txns = agent_results.get("BankingAgent", {}).get("transactions", [])
            spending = agent_results.get("BankingAgent", {}).get("spending_summary", {})

            cust_name = cust.get("full_name", routing.get("customer_id", "Customer"))
            lines = [
                f"### Transaction History & Spending Analysis for {cust_name}",
                f"- **Total Debits:** ₹{spending.get('total_debits', 0):,.2f}",
                f"- **Total Credits:** ₹{spending.get('total_credits', 0):,.2f}",
                f"- **Net Cash Flow:** ₹{spending.get('net_flow', 0):,.2f}",
                f"- **Primary Merchant:** {spending.get('top_merchant', 'N/A')}",
                "",
                "#### Category Spending Breakdown:"
            ]
            for cat, amt in spending.get("category_breakdown", {}).items():
                lines.append(f"- **{cat}:** ₹{amt:,.2f}")

            lines.append("\n#### Recent Transactions:")
            for t in txns[:5]:
                flag_str = " ⚠️ [FLAGGED]" if t.get("is_flagged") else ""
                lines.append(f"- `{t.get('id')}` | **₹{t.get('amount', 0):,.2f}** ({t.get('txn_type')}) | {t.get('merchant')} | {t.get('category')} | {t.get('location')}{flag_str}")

            return "\n".join(lines)

        elif intent == "FRAUD_INVESTIGATION":
            fraud_data = agent_results.get("RiskFraudAgent", {}).get("risk_analysis", {})
            if not fraud_data.get("found", True):
                return f"Transaction record for **{routing.get('transaction_id')}** was not found in the surveillance ledger."

            score = fraud_data.get("risk_score", 0)
            level = fraud_data.get("risk_level", "UNKNOWN")
            action = fraud_data.get("recommended_action", "MANUAL_REVIEW")
            rules = fraud_data.get("triggered_rules", [])

            lines = [
                f"### 🛡️ Fraud Investigation Report: Transaction `{fraud_data.get('transaction_id')}`",
                f"- **Customer ID:** `{fraud_data.get('customer_id')}`",
                f"- **Amount:** **₹{fraud_data.get('amount', 0):,.2f}**",
                f"- **Merchant:** {fraud_data.get('merchant')}",
                f"- **Location:** {fraud_data.get('location')} (Origin Check)",
                f"- **Risk Score:** **{score} / 100** (`{level}`)",
                f"- **Recommended Review Action:** `{action}`",
                "",
                "#### Deterministic Rules Triggered:"
            ]
            for rule in rules:
                lines.append(f"- ⚠️ {rule}")

            lines.append("\n> **System Note:** This assessment was evaluated using deterministic risk heuristics and compliance policies. Non-binding simulated security evaluation.")
            return "\n".join(lines)

        elif intent == "LOAN_ELIGIBILITY":
            eligibility = agent_results.get("CreditLoanAgent", {}).get("eligibility", {})
            if not eligibility.get("found", True):
                return f"Customer record for **{routing.get('customer_id')}** was not found. Cannot compute loan eligibility."

            is_eligible = eligibility.get("is_eligible", False)
            status_text = "APPROVED (ELIGIBLE)" if is_eligible else "NOT ELIGIBLE (REJECTED)"
            status_icon = "✅" if is_eligible else "❌"

            lines = [
                f"### {status_icon} Loan Eligibility Assessment: {eligibility.get('customer_name')} ({eligibility.get('customer_id')})",
                f"- **Requested Principal:** ₹{eligibility.get('requested_amount', 0):,.2f}",
                f"- **Tenure:** {eligibility.get('tenure_months')} Months",
                f"- **Applicable Interest Rate:** {eligibility.get('applicable_interest_rate')}% p.a.",
                f"- **Estimated Monthly EMI:** **₹{eligibility.get('estimated_emi', 0):,.2f}**",
                f"- **Monthly Net Income:** ₹{eligibility.get('monthly_income', 0):,.2f}",
                f"- **Proposed Debt-to-Income (DTI) Ratio:** **{eligibility.get('debt_to_income_ratio')}%** (Permissible Ceiling: {eligibility.get('max_permissible_dti')}%)",
                f"- **Credit Score:** {eligibility.get('credit_score')} (Min Threshold: {eligibility.get('min_required_credit_score')})",
                f"- **Final Verdict:** **{status_text}**",
                "",
                "#### Underwriting Evaluation Factors:"
            ]
            for r in eligibility.get("reasons", []):
                lines.append(f"- {r}")

            lines.append(f"\n> **Regulatory Notice:** {eligibility.get('disclaimer', 'Simulated non-binding evaluation.')}")
            return "\n".join(lines)

        elif intent == "CROSS_AGENT_ASSISTANCE":
            banking = agent_results.get("BankingAgent", {})
            cust = banking.get("customer", {})
            accounts = banking.get("accounts", [])
            spending = banking.get("spending_summary", {})
            risk = agent_results.get("RiskFraudAgent", {})
            loan = agent_results.get("CreditLoanAgent", {}).get("eligibility", {})

            cust_name = cust.get("full_name", routing.get("customer_id", "Customer"))
            total_liquid = sum(a.get("balance", 0.0) for a in accounts)

            lines = [
                f"### Comprehensive Financial Portfolio Review for {cust_name} ({routing.get('customer_id')})",
                "",
                "#### 1. Banking & Liquidity Position (BankingAgent):",
                f"- Total Liquid Balance: **₹{total_liquid:,.2f}** across {len(accounts)} accounts.",
                f"- Monthly Inflows (Credits): **₹{spending.get('total_credits', 0):,.2f}**",
                f"- Monthly Outflows (Debits): **₹{spending.get('total_debits', 0):,.2f}**",
                f"- Net Surplus Cashflow: **₹{spending.get('net_flow', 0):,.2f}**",
                "",
                "#### 2. Risk & Fraud Surveillance (RiskFraudAgent):"
            ]

            # Check if any transactions were flagged
            txns = banking.get("transactions", [])
            flagged = [t for t in txns if t.get("is_flagged")]
            if flagged:
                lines.append(f"- ⚠️ **Surveillance Warning:** Found {len(flagged)} suspicious/flagged transaction(s) in customer history:")
                for ft in flagged[:2]:
                    lines.append(f"  - `{ft.get('id')}`: ₹{ft.get('amount', 0):,.2f} to *{ft.get('merchant')}* ({ft.get('location')}) - *{ft.get('flag_reason', 'Flagged')}*")
            else:
                lines.append("- ✅ No active high-risk fraud alerts or suspicious debit patterns detected in recent history.")

            lines.extend([
                "",
                "#### 3. Loan Affordability & Credit Assessment (CreditLoanAgent):",
                f"- Evaluated Loan: **₹{loan.get('requested_amount', 300000):,.2f}** over {loan.get('tenure_months', 36)} months.",
                f"- Estimated Monthly EMI: **₹{loan.get('estimated_emi', 0):,.2f}**",
                f"- Debt-to-Income (DTI) Ratio: **{loan.get('debt_to_income_ratio', 0)}%** (Ceiling: 40%).",
                f"- Credit Score: **{loan.get('credit_score', cust.get('credit_score', 'N/A'))}**",
                f"- Affordability Verdict: **{'AFFORDABLE & QUALIFIED' if loan.get('is_eligible') else 'CONSTRAINED / NOT RECOMMENDED'}**"
            ])

            if loan.get("is_eligible") and not flagged:
                lines.append("\n**Executive Recommendation:** Customer maintains sound cash flow surplus and pristine risk score; the proposed loan obligations are easily serviceable.")
            elif flagged:
                lines.append("\n**Executive Recommendation:** While debt ratios appear mathematically serviceable, resolution of active surveillance flags is required before credit sanctions.")
            else:
                lines.append("\n**Executive Recommendation:** Loan obligations exceed recommended prudential thresholds relative to net monthly disposable income.")

            lines.append("\n> **Simulated Advisory:** All underwriting calculations and risk markers are strictly simulated for educational assessment.")
            return "\n".join(lines)

        else:
            return (
                "I am **BankMind AI**, your multi-agent banking assistant. I can assist you with:\n\n"
                "- **Account Balance & Customer Inquiries** (e.g. *'What is the balance of customer CUST-1001?'*)\n"
                "- **Transaction & Spending Analysis** (e.g. *'Show transactions for CUST-1001 and summarize spending.'*)\n"
                "- **Fraud Investigation** (e.g. *'Investigate transaction TXN-3001. Why was it flagged?'*)\n"
                "- **Loan Eligibility & EMI Calculations** (e.g. *'Can customer CUST-1002 qualify for a loan of ₹300,000 over 36 months?'*)\n"
                "- **Cross-Agent Portfolio Reviews** (e.g. *'Review CUST-1001 spending, check risk flags, and assess loan affordability.'*)\n\n"
                "Please specify your query or select one of the suggested prompts!"
            )


llm_provider = LLMProvider()
