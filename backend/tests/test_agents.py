import pytest
from app.agents.banking import BankingAgent
from app.agents.risk_fraud import RiskFraudAgent
from app.agents.credit_loan import CreditLoanAgent
from app.agents.compliance import ComplianceAgent
from app.agents.supervisor import supervisor_agent
from app.services.llm_provider import llm_provider


def test_banking_agent_execution(db_session):
    agent = BankingAgent()
    res = agent.execute({"customer_id": "CUST-1001"}, db=db_session)
    assert res["agent"] == "BankingAgent"
    assert "customer" in res["data"]
    assert "accounts" in res["data"]
    assert "transactions" in res["data"]
    assert "spending_summary" in res["data"]
    assert len(res["traces"]) >= 4


def test_risk_fraud_agent_execution(db_session):
    agent = RiskFraudAgent()
    res = agent.execute({"transaction_id": "TXN-3001", "customer_id": "CUST-1001"}, db=db_session)
    assert res["agent"] == "RiskFraudAgent"
    assert "risk_analysis" in res["data"]
    assert res["data"]["risk_analysis"]["risk_score"] >= 80
    assert len(res["traces"]) >= 2


def test_credit_loan_agent_execution(db_session):
    agent = CreditLoanAgent()
    res = agent.execute({"customer_id": "CUST-1002", "loan_amount": 300000.0, "loan_tenure": 36}, db=db_session)
    assert res["agent"] == "CreditLoanAgent"
    assert "eligibility" in res["data"]
    assert "emi_schedule" in res["data"]
    assert "Simulated" in res["disclaimer"]


def test_compliance_agent_execution(db_session):
    agent = ComplianceAgent()
    res = agent.execute({"policy_code": "AML-CFT-01", "request_id": "REQ-COMP-01"}, db=db_session)
    assert res["agent"] == "ComplianceAgent"
    assert "policy" in res["data"]
    assert "audit_event" in res["data"]


def test_use_case_1_account_inquiry(db_session):
    """Use Case 1: What is the current balance of customer CUST-1001?"""
    query = "What is the current balance of customer CUST-1001?"
    res = supervisor_agent.process_request(query, db=db_session)
    assert "BankingAgent" in res["selected_agents"]
    assert "CUST-1001" in res["answer"]
    assert "₹" in res["answer"]
    assert len(res["traces"]) > 0
    assert res["request_id"].startswith("REQ-")


def test_use_case_2_transaction_analysis(db_session):
    """Use Case 2: Show the last 10 transactions for customer CUST-1001 and summarize their spending."""
    query = "Show the last 10 transactions for customer CUST-1001 and summarize their spending."
    res = supervisor_agent.process_request(query, db=db_session)
    assert "BankingAgent" in res["selected_agents"]
    assert "Debits" in res["answer"] or "debits" in res["answer"].lower()
    assert len(res["traces"]) >= 3


def test_use_case_3_fraud_investigation(db_session):
    """Use Case 3: Investigate transaction TXN-3001. Why was it flagged?"""
    query = "Investigate transaction TXN-3001. Why was it flagged?"
    res = supervisor_agent.process_request(query, db=db_session)
    assert "RiskFraudAgent" in res["selected_agents"]
    assert "TXN-3001" in res["answer"]
    assert "Dubai" in res["answer"] or "Forex" in res["answer"] or "Risk Score" in res["answer"]


def test_use_case_4_loan_eligibility(db_session):
    """Use Case 4: Can customer CUST-1002 qualify for a loan of ₹300000 over 36 months?"""
    query = "Can customer CUST-1002 qualify for a loan of ₹300000 over 36 months?"
    res = supervisor_agent.process_request(query, db=db_session)
    assert "CreditLoanAgent" in res["selected_agents"]
    assert "EMI" in res["answer"] or "emi" in res["answer"].lower()
    assert "Priya" in res["answer"] or "CUST-1002" in res["answer"]
    assert "non-binding" in res["answer"].lower() or "simulated" in res["answer"].lower()


def test_use_case_5_cross_agent_assistance(db_session):
    """
    Use Case 5: Review customer CUST-1001's spending, check for suspicious activity,
    and suggest whether a loan payment would be affordable.
    """
    query = "Review customer CUST-1001's spending, check for suspicious activity, and suggest whether a loan payment would be affordable."
    res = supervisor_agent.process_request(query, db=db_session)
    assert "BankingAgent" in res["selected_agents"]
    assert "RiskFraudAgent" in res["selected_agents"]
    assert "CreditLoanAgent" in res["selected_agents"]
    assert len(res["traces"]) >= 5


def test_unknown_inquiry_clarification(db_session):
    """Ambiguous or unrecognized request handling."""
    query = "Hello, can you sing a song for me?"
    res = supervisor_agent.process_request(query, db=db_session)
    assert "BankMind AI" in res["answer"]
    assert len(res["warnings"]) >= 1


def test_deterministic_demo_mode_fallback():
    """Verify demo mode metadata when API key is missing or simulated."""
    info = llm_provider.provider_info
    assert "provider" in info
    assert "model" in info
    assert "mode" in info
