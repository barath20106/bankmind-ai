from typing import List
from fastapi import APIRouter
from app.schemas.schemas import AgentSpec
from app.agents.supervisor import supervisor_agent

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("", response_model=List[AgentSpec])
def list_registered_agents():
    """Retrieve specifications and operational capabilities of all registered specialized AI agents."""
    agents_list = [
        AgentSpec(
            name=supervisor_agent.name,
            role=supervisor_agent.role,
            description=supervisor_agent.description,
            capabilities=[
                "Natural language intent decomposition",
                "Specialist routing & parallel dispatch",
                "Cross-agent context aggregation",
                "Grounded response synthesis",
                "Execution trace logging"
            ],
            tools=["classify_intent", "synthesize_grounded_response"]
        ),
        AgentSpec(
            name=supervisor_agent.specialists["BankingAgent"].name,
            role=supervisor_agent.specialists["BankingAgent"].role,
            description=supervisor_agent.specialists["BankingAgent"].description,
            capabilities=[
                "Customer profile lookup",
                "Account balances & liquidity checks",
                "Transaction filtering by category & date",
                "Aggregated spending analytics"
            ],
            tools=["get_customer", "search_customers", "get_accounts", "get_account_balance", "get_transactions", "calculate_spending_summary"]
        ),
        AgentSpec(
            name=supervisor_agent.specialists["RiskFraudAgent"].name,
            role=supervisor_agent.specialists["RiskFraudAgent"].role,
            description=supervisor_agent.specialists["RiskFraudAgent"].description,
            capabilities=[
                "Deterministic rule-based fraud detection",
                "Anomalous high-value wire surveillance",
                "Geographic & offshore IP mismatch alerts",
                "Transaction velocity & structuring checks"
            ],
            tools=["analyze_transaction_risk", "list_fraud_alerts"]
        ),
        AgentSpec(
            name=supervisor_agent.specialists["CreditLoanAgent"].name,
            role=supervisor_agent.specialists["CreditLoanAgent"].role,
            description=supervisor_agent.specialists["CreditLoanAgent"].description,
            capabilities=[
                "Loan underwriting qualification",
                "Debt-to-Income (DTI) ratio computation",
                "Standard amortization EMI calculation",
                "Credit score threshold evaluation"
            ],
            tools=["get_loan_application", "calculate_loan_eligibility", "calculate_emi"]
        ),
        AgentSpec(
            name=supervisor_agent.specialists["ComplianceAgent"].name,
            role=supervisor_agent.specialists["ComplianceAgent"].role,
            description=supervisor_agent.specialists["ComplianceAgent"].description,
            capabilities=[
                "Simulated regulatory policy validation",
                "AML/CFT rule threshold enforcement",
                "KYC status verification",
                "Immutable compliance audit logging"
            ],
            tools=["get_compliance_policy", "write_audit_event"]
        )
    ]
    return agents_list
