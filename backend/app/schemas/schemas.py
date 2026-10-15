from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# --- Customer Schemas ---
class CustomerBase(BaseModel):
    id: str
    full_name: str
    email: str
    phone: str
    city: str
    kyc_status: str
    credit_score: int
    monthly_income: float

class CustomerResponse(CustomerBase):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Account Schemas ---
class AccountResponse(BaseModel):
    id: str
    customer_id: str
    account_number: str
    account_type: str
    balance: float
    currency: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Transaction Schemas ---
class TransactionResponse(BaseModel):
    id: str
    account_id: str
    customer_id: str
    amount: float
    txn_type: str
    category: str
    merchant: str
    location: str
    timestamp: datetime
    status: str
    is_flagged: bool
    flag_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SpendingSummaryResponse(BaseModel):
    customer_id: str
    total_debits: float
    total_credits: float
    net_flow: float
    transaction_count: int
    category_breakdown: Dict[str, float]
    top_merchant: Optional[str] = None
    currency: str = "INR"


# --- Loan & Credit Schemas ---
class LoanApplicationResponse(BaseModel):
    id: str
    customer_id: str
    requested_amount: float
    tenure_months: int
    purpose: str
    monthly_income: float
    existing_obligations: float
    status: str
    interest_rate: float
    estimated_emi: float
    dti_ratio: float
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EMICalculationRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Principal loan amount in INR")
    annual_interest_rate: float = Field(default=10.5, gt=0, description="Annual interest rate percentage")
    tenure_months: int = Field(..., gt=0, description="Tenure in months")


class EMICalculationResponse(BaseModel):
    principal: float
    annual_interest_rate: float
    tenure_months: int
    monthly_emi: float
    total_interest: float
    total_payable: float
    currency: str = "INR"
    disclaimer: str = "Simulated calculation for educational purposes only. Non-binding."


class LoanEligibilityRequest(BaseModel):
    customer_id: str
    requested_amount: float = Field(..., gt=0)
    tenure_months: int = Field(..., gt=0)
    annual_interest_rate: float = Field(default=10.5)


class LoanEligibilityResponse(BaseModel):
    customer_id: str
    customer_name: str
    requested_amount: float
    tenure_months: int
    monthly_income: float
    existing_obligations: float
    estimated_emi: float
    proposed_total_obligations: float
    debt_to_income_ratio: float
    max_permissible_dti: float
    credit_score: int
    min_required_credit_score: int
    is_eligible: bool
    status: str
    reasons: List[str]
    disclaimer: str = "Simulated credit eligibility result for testing purposes. Non-binding."


# --- Fraud & Risk Schemas ---
class FraudAlertResponse(BaseModel):
    id: str
    transaction_id: str
    customer_id: str
    risk_score: int
    severity: str
    rule_triggered: str
    status: str
    review_notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FraudAnalysisRequest(BaseModel):
    transaction_id: str


class FraudAnalysisResponse(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    merchant: str
    location: str
    risk_score: int
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    triggered_rules: List[str]
    recommended_action: str
    is_flagged: bool
    details: Dict[str, Any]
    disclaimer: str = "Simulated fraud detection logic. Educational rule assessment."


# --- Compliance & Audit Schemas ---
class CompliancePolicyResponse(BaseModel):
    id: str
    code: str
    name: str
    description: str
    max_unverified_limit: float
    aml_flag_threshold: float
    rules_json: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class AuditEventResponse(BaseModel):
    id: str
    timestamp: datetime
    actor: str
    event_type: str
    request_id: str
    details: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


# --- Execution Traces Schemas ---
class ExecutionTraceItem(BaseModel):
    step_index: int
    agent_name: str
    tool_name: str
    status: str
    latency_ms: float
    input_payload: Dict[str, Any]
    output_payload: Dict[str, Any]
    summary: str
    warning: Optional[str] = None


class ExecutionTraceResponse(BaseModel):
    id: str
    request_id: str
    step_index: int
    timestamp: datetime
    agent_name: str
    tool_name: str
    status: str
    latency_ms: float
    input_payload: str
    output_payload: str
    warning: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- Chat & Multi-Agent Schemas ---
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    customer_id: Optional[str] = None


class ChatResponse(BaseModel):
    request_id: str
    answer: str
    selected_agents: List[str]
    tools_invoked: List[str]
    traces: List[ExecutionTraceItem]
    provider: str  # "gemini" or "deterministic-demo"
    model: str
    latency_ms: float
    warnings: List[str] = []


# --- Dashboard Summary Schemas ---
class MetricCard(BaseModel):
    label: str
    value: Any
    subtext: str
    change: Optional[str] = None
    trend: Optional[str] = "neutral"  # positive, negative, neutral


class ChartPoint(BaseModel):
    name: str
    volume: float
    count: int


class DashboardSummaryResponse(BaseModel):
    total_customers: int
    total_accounts: int
    total_deposits: float
    total_transactions: int
    flagged_transactions_count: int
    active_fraud_alerts: int
    total_loan_applications: int
    system_status: str
    currency: str = "INR"
    activity_chart: List[ChartPoint]
    recent_transactions: List[TransactionResponse]
    recent_alerts: List[FraudAlertResponse]


# --- Agent Schemas ---
class AgentSpec(BaseModel):
    name: str
    role: str
    description: str
    capabilities: List[str]
    tools: List[str]
