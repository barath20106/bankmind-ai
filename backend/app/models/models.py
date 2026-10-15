import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(50), primary_key=True, index=True)  # e.g., CUST-1001
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(30), nullable=False)
    city = Column(String(50), nullable=False)
    kyc_status = Column(String(30), default="VERIFIED")  # VERIFIED, PENDING, REJECTED
    credit_score = Column(Integer, default=720)
    monthly_income = Column(Float, default=75000.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    accounts = relationship("Account", back_populates="customer", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="customer")
    loan_applications = relationship("LoanApplication", back_populates="customer")
    fraud_alerts = relationship("FraudAlert", back_populates="customer")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String(50), primary_key=True, index=True)  # e.g., ACCT-2001
    customer_id = Column(String(50), ForeignKey("customers.id"), nullable=False, index=True)
    account_number = Column(String(30), unique=True, nullable=False)
    account_type = Column(String(30), default="Savings")  # Savings, Current, Salary, Premium Savings
    balance = Column(Float, default=0.0)
    currency = Column(String(10), default="INR")
    status = Column(String(30), default="ACTIVE")  # ACTIVE, DORMANT, FROZEN
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(50), primary_key=True, index=True)  # e.g., TXN-3001
    account_id = Column(String(50), ForeignKey("accounts.id"), nullable=False, index=True)
    customer_id = Column(String(50), ForeignKey("customers.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    txn_type = Column(String(20), nullable=False)  # DEBIT, CREDIT
    category = Column(String(50), nullable=False)   # Grocery, Dining, Travel, Electronics, Salary, Crypto, Wire Transfer
    merchant = Column(String(100), nullable=False)
    location = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    status = Column(String(30), default="COMPLETED")  # COMPLETED, PENDING, FLAGGED, REVERSED
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(Text, nullable=True)

    # Relationships
    account = relationship("Account", back_populates="transactions")
    customer = relationship("Customer", back_populates="transactions")
    fraud_alert = relationship("FraudAlert", back_populates="transaction", uselist=False)


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(String(50), primary_key=True, index=True)  # e.g., LOAN-4001
    customer_id = Column(String(50), ForeignKey("customers.id"), nullable=False, index=True)
    requested_amount = Column(Float, nullable=False)
    tenure_months = Column(Integer, nullable=False)
    purpose = Column(String(100), nullable=False)
    monthly_income = Column(Float, nullable=False)
    existing_obligations = Column(Float, default=0.0)
    status = Column(String(30), default="UNDER_REVIEW")  # PENDING, APPROVED, REJECTED, UNDER_REVIEW
    interest_rate = Column(Float, default=10.5)
    estimated_emi = Column(Float, default=0.0)
    dti_ratio = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    customer = relationship("Customer", back_populates="loan_applications")


class FraudAlert(Base):
    __tablename__ = "fraud_alerts"

    id = Column(String(50), primary_key=True, index=True)  # e.g., FA-5001
    transaction_id = Column(String(50), ForeignKey("transactions.id"), nullable=False, index=True)
    customer_id = Column(String(50), ForeignKey("customers.id"), nullable=False, index=True)
    risk_score = Column(Integer, nullable=False)  # 0 to 100
    severity = Column(String(30), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    rule_triggered = Column(Text, nullable=False)
    status = Column(String(30), default="NEW")  # NEW, INVESTIGATING, RESOLVED, DISMISSED
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    transaction = relationship("Transaction", back_populates="fraud_alert")
    customer = relationship("Customer", back_populates="fraud_alerts")


class CompliancePolicy(Base):
    __tablename__ = "compliance_policies"

    id = Column(String(50), primary_key=True, index=True)  # e.g., POL-6001
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    max_unverified_limit = Column(Float, default=25000.0)
    aml_flag_threshold = Column(Float, default=200000.0)
    rules_json = Column(Text, nullable=False)  # Serialized rules
    is_active = Column(Boolean, default=True)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(50), primary_key=True, index=True)  # e.g., AUD-7001
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    actor = Column(String(100), nullable=False)
    event_type = Column(String(100), nullable=False)
    request_id = Column(String(100), nullable=False, index=True)
    details_json = Column(Text, nullable=False)


class ExecutionTrace(Base):
    __tablename__ = "execution_traces"

    id = Column(String(50), primary_key=True, index=True)  # e.g., TRC-8001
    request_id = Column(String(100), nullable=False, index=True)
    step_index = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    agent_name = Column(String(100), nullable=False)
    tool_name = Column(String(100), nullable=False)
    status = Column(String(30), default="SUCCESS")  # SUCCESS, FAILED, WARNING
    input_payload = Column(Text, nullable=False)
    output_payload = Column(Text, nullable=False)
    latency_ms = Column(Float, default=0.0)
    warning = Column(Text, nullable=True)
