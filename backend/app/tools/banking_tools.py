import json
import uuid
import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.core.database import SessionLocal
from app.models.models import (
    Customer,
    Account,
    Transaction,
    LoanApplication,
    FraudAlert,
    CompliancePolicy,
    AuditEvent,
)


def _get_db(db: Optional[Session]) -> tuple[Session, bool]:
    """Helper to get a database session and track if it was locally created."""
    if db is not None:
        return db, False
    return SessionLocal(), True


# 1. get_customer(customer_id)
def get_customer(customer_id: str, db: Optional[Session] = None) -> Dict[str, Any]:
    """Retrieve customer details by ID."""
    session, is_local = _get_db(db)
    try:
        cust = session.query(Customer).filter(Customer.id == customer_id.strip()).first()
        if not cust:
            return {"error": f"Customer '{customer_id}' not found", "found": False}
        return {
            "found": True,
            "id": cust.id,
            "full_name": cust.full_name,
            "email": cust.email,
            "phone": cust.phone,
            "city": cust.city,
            "kyc_status": cust.kyc_status,
            "credit_score": cust.credit_score,
            "monthly_income": cust.monthly_income,
            "created_at": cust.created_at.isoformat() if cust.created_at else None,
        }
    finally:
        if is_local:
            session.close()


# 2. search_customers(query)
def search_customers(query: str, db: Optional[Session] = None) -> List[Dict[str, Any]]:
    """Search customers by name, ID, email, or city."""
    session, is_local = _get_db(db)
    try:
        q = f"%{query.strip()}%"
        customers = session.query(Customer).filter(
            or_(
                Customer.id.ilike(q),
                Customer.full_name.ilike(q),
                Customer.email.ilike(q),
                Customer.city.ilike(q)
            )
        ).limit(20).all()
        return [
            {
                "id": c.id,
                "full_name": c.full_name,
                "email": c.email,
                "city": c.city,
                "kyc_status": c.kyc_status,
                "credit_score": c.credit_score,
                "monthly_income": c.monthly_income
            }
            for c in customers
        ]
    finally:
        if is_local:
            session.close()


# 3. get_accounts(customer_id)
def get_accounts(customer_id: str, db: Optional[Session] = None) -> List[Dict[str, Any]]:
    """Retrieve all accounts for a customer."""
    session, is_local = _get_db(db)
    try:
        accounts = session.query(Account).filter(Account.customer_id == customer_id.strip()).all()
        return [
            {
                "id": a.id,
                "customer_id": a.customer_id,
                "account_number": a.account_number,
                "account_type": a.account_type,
                "balance": a.balance,
                "currency": a.currency,
                "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in accounts
        ]
    finally:
        if is_local:
            session.close()


# 4. get_account_balance(account_id)
def get_account_balance(account_id: str, db: Optional[Session] = None) -> Dict[str, Any]:
    """Retrieve the balance of a specific account."""
    session, is_local = _get_db(db)
    try:
        acct = session.query(Account).filter(Account.id == account_id.strip()).first()
        if not acct:
            return {"error": f"Account '{account_id}' not found", "found": False}
        return {
            "found": True,
            "account_id": acct.id,
            "customer_id": acct.customer_id,
            "account_type": acct.account_type,
            "account_number": acct.account_number,
            "balance": acct.balance,
            "currency": acct.currency,
            "status": acct.status
        }
    finally:
        if is_local:
            session.close()


# 5. get_transactions(customer_id, limit, filters)
def get_transactions(
    customer_id: str,
    limit: int = 10,
    filters: Optional[Dict[str, Any]] = None,
    db: Optional[Session] = None
) -> List[Dict[str, Any]]:
    """Retrieve transaction history for a customer with optional filters and spending summary."""
    session, is_local = _get_db(db)
    try:
        query = session.query(Transaction).filter(Transaction.customer_id == customer_id.strip())
        
        if filters:
            if "category" in filters and filters["category"]:
                query = query.filter(Transaction.category.ilike(f"%{filters['category']}%"))
            if "txn_type" in filters and filters["txn_type"]:
                query = query.filter(Transaction.txn_type == filters["txn_type"].upper())
            if "is_flagged" in filters and filters["is_flagged"] is not None:
                query = query.filter(Transaction.is_flagged == bool(filters["is_flagged"]))
            if "account_id" in filters and filters["account_id"]:
                query = query.filter(Transaction.account_id == filters["account_id"])

        txns = query.order_by(desc(Transaction.timestamp)).limit(limit).all()
        return [
            {
                "id": t.id,
                "account_id": t.account_id,
                "customer_id": t.customer_id,
                "amount": t.amount,
                "txn_type": t.txn_type,
                "category": t.category,
                "merchant": t.merchant,
                "location": t.location,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                "status": t.status,
                "is_flagged": t.is_flagged,
                "flag_reason": t.flag_reason
            }
            for t in txns
        ]
    finally:
        if is_local:
            session.close()


# Helper: calculate_spending_summary
def calculate_spending_summary(customer_id: str, db: Optional[Session] = None) -> Dict[str, Any]:
    """Calculate aggregated spending statistics for a customer."""
    session, is_local = _get_db(db)
    try:
        txns = session.query(Transaction).filter(Transaction.customer_id == customer_id.strip()).all()
        total_debits = 0.0
        total_credits = 0.0
        categories: Dict[str, float] = {}
        merchant_counts: Dict[str, int] = {}

        for t in txns:
            if t.txn_type == "DEBIT":
                total_debits += t.amount
                categories[t.category] = categories.get(t.category, 0.0) + t.amount
                merchant_counts[t.merchant] = merchant_counts.get(t.merchant, 0) + 1
            elif t.txn_type == "CREDIT":
                total_credits += t.amount

        top_merchant = max(merchant_counts.items(), key=lambda x: x[1])[0] if merchant_counts else "None"

        return {
            "customer_id": customer_id,
            "total_debits": round(total_debits, 2),
            "total_credits": round(total_credits, 2),
            "net_flow": round(total_credits - total_debits, 2),
            "transaction_count": len(txns),
            "category_breakdown": {k: round(v, 2) for k, v in categories.items()},
            "top_merchant": top_merchant,
            "currency": "INR"
        }
    finally:
        if is_local:
            session.close()


# 6. analyze_transaction_risk(transaction_id)
def analyze_transaction_risk(transaction_id: str, db: Optional[Session] = None) -> Dict[str, Any]:
    """
    Deterministic rule-based risk and fraud analysis on a simulated transaction.
    Applies deterministic heuristics:
    1. Unusual amount spike (> 3x average debit or > ₹100,000 for retail customer)
    2. Geographic anomaly (offshore / known risky origin)
    3. High-risk merchant category (Crypto, Overseas Wire, Casino)
    4. Velocity anomaly (multiple debits in short timeframe)
    """
    session, is_local = _get_db(db)
    try:
        txn = session.query(Transaction).filter(Transaction.id == transaction_id.strip()).first()
        if not txn:
            return {"error": f"Transaction '{transaction_id}' not found", "found": False}

        customer = session.query(Customer).filter(Customer.id == txn.customer_id).first()
        risk_score = 10  # Base safe score
        triggered_rules = []

        # Rule 1: High-risk merchant category
        high_risk_categories = ["Crypto", "Crypto Transfer", "Overseas Forex Desk", "Offshore Casino", "High-Risk Wire"]
        if txn.category in high_risk_categories or any(cat.lower() in txn.merchant.lower() for cat in ["crypto", "forex", "casino"]):
            risk_score += 40
            triggered_rules.append(f"High-risk merchant/category detected: '{txn.category}' - '{txn.merchant}'")

        # Rule 2: Amount threshold check
        if txn.amount >= 200000:
            risk_score += 35
            triggered_rules.append(f"Very high transaction amount: ₹{txn.amount:,.2f} exceeds standard AML single-transaction ceiling")
        elif txn.amount >= 75000:
            risk_score += 20
            triggered_rules.append(f"Unusually large transaction amount: ₹{txn.amount:,.2f}")

        # Rule 3: Geographic anomaly
        offshore_locations = ["Dubai", "London", "Cayman", "Singapore", "Zurich", "Unknown IP"]
        if customer and txn.location:
            if txn.location in offshore_locations or txn.location.lower() != customer.city.lower():
                if txn.location in offshore_locations:
                    risk_score += 30
                    triggered_rules.append(f"Cross-border / offshore transaction location '{txn.location}' does not match home city '{customer.city}'")
                elif txn.amount > 25000:
                    risk_score += 15
                    triggered_rules.append(f"Out-of-city transaction in '{txn.location}' differing from registered '{customer.city}'")

        # Rule 4: Already flagged in database
        if txn.is_flagged and txn.flag_reason:
            risk_score = max(risk_score, 75)
            if txn.flag_reason not in triggered_rules:
                triggered_rules.append(f"Pre-existing surveillance flag: {txn.flag_reason}")

        # Cap score between 0 and 100
        risk_score = min(max(risk_score, 0), 100)

        # Categorize risk level
        if risk_score >= 80:
            risk_level = "CRITICAL"
            recommended_action = "BLOCK_AND_VERIFY"
        elif risk_score >= 60:
            risk_level = "HIGH"
            recommended_action = "HOLD_FOR_MANUAL_REVIEW"
        elif risk_score >= 35:
            risk_level = "MEDIUM"
            recommended_action = "REQUEST_TWO_FACTOR_VERIFICATION"
        else:
            risk_level = "LOW"
            recommended_action = "APPROVE_TRANSACTION"

        return {
            "found": True,
            "transaction_id": txn.id,
            "customer_id": txn.customer_id,
            "amount": txn.amount,
            "merchant": txn.merchant,
            "location": txn.location,
            "category": txn.category,
            "timestamp": txn.timestamp.isoformat() if txn.timestamp else None,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "is_flagged": risk_score >= 60 or txn.is_flagged,
            "triggered_rules": triggered_rules if triggered_rules else ["Standard baseline transaction checks passed."],
            "recommended_action": recommended_action,
            "disclaimer": "Simulated deterministic fraud detection. For technical assessment verification."
        }
    finally:
        if is_local:
            session.close()


# 7. list_fraud_alerts(status)
def list_fraud_alerts(status: Optional[str] = None, db: Optional[Session] = None) -> List[Dict[str, Any]]:
    """Retrieve simulated fraud alerts with optional status filtering."""
    session, is_local = _get_db(db)
    try:
        query = session.query(FraudAlert)
        if status:
            query = query.filter(FraudAlert.status == status.upper())
        alerts = query.order_by(desc(FraudAlert.created_at)).all()
        return [
            {
                "id": a.id,
                "transaction_id": a.transaction_id,
                "customer_id": a.customer_id,
                "risk_score": a.risk_score,
                "severity": a.severity,
                "rule_triggered": a.rule_triggered,
                "status": a.status,
                "review_notes": a.review_notes,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in alerts
        ]
    finally:
        if is_local:
            session.close()


# 8. get_loan_application(application_id)
def get_loan_application(application_id: str, db: Optional[Session] = None) -> Dict[str, Any]:
    """Retrieve details of a specific simulated loan application."""
    session, is_local = _get_db(db)
    try:
        app = session.query(LoanApplication).filter(LoanApplication.id == application_id.strip()).first()
        if not app:
            return {"error": f"Loan application '{application_id}' not found", "found": False}
        return {
            "found": True,
            "id": app.id,
            "customer_id": app.customer_id,
            "requested_amount": app.requested_amount,
            "tenure_months": app.tenure_months,
            "purpose": app.purpose,
            "monthly_income": app.monthly_income,
            "existing_obligations": app.existing_obligations,
            "status": app.status,
            "interest_rate": app.interest_rate,
            "estimated_emi": app.estimated_emi,
            "dti_ratio": app.dti_ratio,
            "notes": app.notes,
            "created_at": app.created_at.isoformat() if app.created_at else None,
            "disclaimer": "Simulated loan record. Non-binding."
        }
    finally:
        if is_local:
            session.close()


# 9. calculate_emi(principal, annual_interest_rate, tenure_months)
def calculate_emi(principal: float, annual_interest_rate: float, tenure_months: int) -> Dict[str, Any]:
    """
    Calculate monthly EMI using standard banking amortization formula:
    E = P * r * (1 + r)^n / ((1 + r)^n - 1)
    """
    if principal <= 0 or tenure_months <= 0:
        return {"error": "Principal and tenure must be positive numbers."}

    monthly_rate = (annual_interest_rate / 100.0) / 12.0
    if monthly_rate == 0:
        emi = principal / tenure_months
    else:
        emi = (principal * monthly_rate * ((1 + monthly_rate) ** tenure_months)) / (
            ((1 + monthly_rate) ** tenure_months) - 1
        )

    emi = round(emi, 2)
    total_payable = round(emi * tenure_months, 2)
    total_interest = round(total_payable - principal, 2)

    return {
        "principal": round(principal, 2),
        "annual_interest_rate": round(annual_interest_rate, 2),
        "tenure_months": tenure_months,
        "monthly_emi": emi,
        "total_interest": total_interest,
        "total_payable": total_payable,
        "currency": "INR",
        "disclaimer": "Simulated calculation for educational purposes only. Non-binding."
    }


# 10. calculate_loan_eligibility(customer_id, requested_amount, tenure_months)
def calculate_loan_eligibility(
    customer_id: str,
    requested_amount: float,
    tenure_months: int,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Evaluate customer eligibility for a loan based on KYC, Credit Score, and Debt-to-Income (DTI).
    Criteria:
    - Customer must exist and have VERIFIED KYC status.
    - Minimum credit score: 650.
    - DTI ratio (including proposed EMI) must not exceed 40% (0.40).
    """
    session, is_local = _get_db(db)
    try:
        customer = session.query(Customer).filter(Customer.id == customer_id.strip()).first()
        if not customer:
            return {"error": f"Customer '{customer_id}' not found", "found": False}

        # Determine rate based on credit score tier
        if customer.credit_score >= 750:
            annual_rate = 9.5
        elif customer.credit_score >= 700:
            annual_rate = 10.5
        elif customer.credit_score >= 650:
            annual_rate = 12.0
        else:
            annual_rate = 14.5

        emi_data = calculate_emi(requested_amount, annual_rate, tenure_months)
        proposed_emi = emi_data["monthly_emi"]
        
        # Calculate existing obligations from existing loans or estimate at 15% of income
        existing_obligations = 0.0
        existing_loans = session.query(LoanApplication).filter(
            LoanApplication.customer_id == customer.id,
            LoanApplication.status == "APPROVED"
        ).all()
        for l in existing_loans:
            existing_obligations += l.estimated_emi

        total_proposed_obligations = existing_obligations + proposed_emi
        monthly_income = customer.monthly_income if customer.monthly_income > 0 else 1.0
        dti_ratio = round((total_proposed_obligations / monthly_income) * 100, 2)

        reasons = []
        is_eligible = True

        # KYC check
        if customer.kyc_status != "VERIFIED":
            is_eligible = False
            reasons.append(f"KYC status is '{customer.kyc_status}'. Full verification required.")
        else:
            reasons.append("KYC identity verified.")

        # Credit score check
        if customer.credit_score < 650:
            is_eligible = False
            reasons.append(f"Credit score ({customer.credit_score}) below minimum threshold of 650.")
        else:
            reasons.append(f"Credit score ({customer.credit_score}) meets criteria (Tier rate: {annual_rate}%).")

        # DTI check
        max_dti = 40.0
        if dti_ratio > max_dti:
            is_eligible = False
            reasons.append(f"Proposed Debt-to-Income ratio ({dti_ratio}%) exceeds max allowable ceiling of {max_dti}%.")
        else:
            reasons.append(f"Proposed Debt-to-Income ratio ({dti_ratio}%) is within safe limit of {max_dti}%.")

        status = "ELIGIBLE" if is_eligible else "INELIGIBLE"

        return {
            "found": True,
            "customer_id": customer.id,
            "customer_name": customer.full_name,
            "requested_amount": requested_amount,
            "tenure_months": tenure_months,
            "monthly_income": customer.monthly_income,
            "existing_obligations": existing_obligations,
            "estimated_emi": proposed_emi,
            "proposed_total_obligations": round(total_proposed_obligations, 2),
            "debt_to_income_ratio": dti_ratio,
            "max_permissible_dti": max_dti,
            "credit_score": customer.credit_score,
            "min_required_credit_score": 650,
            "applicable_interest_rate": annual_rate,
            "is_eligible": is_eligible,
            "status": status,
            "reasons": reasons,
            "disclaimer": "Simulated credit eligibility result for technical assessment. Non-binding."
        }
    finally:
        if is_local:
            session.close()


# 11. get_compliance_policy(policy_name)
def get_compliance_policy(policy_name: str, db: Optional[Session] = None) -> Dict[str, Any]:
    """Retrieve details of a compliance policy by code or name."""
    session, is_local = _get_db(db)
    try:
        q = f"%{policy_name.strip()}%"
        policy = session.query(CompliancePolicy).filter(
            or_(
                CompliancePolicy.code.ilike(q),
                CompliancePolicy.name.ilike(q)
            )
        ).first()

        if not policy:
            # Fallback to default AML-KYC policy if not explicitly matched
            policy = session.query(CompliancePolicy).first()

        if not policy:
            return {"error": f"No compliance policy found matching '{policy_name}'", "found": False}

        return {
            "found": True,
            "id": policy.id,
            "code": policy.code,
            "name": policy.name,
            "description": policy.description,
            "max_unverified_limit": policy.max_unverified_limit,
            "aml_flag_threshold": policy.aml_flag_threshold,
            "rules": json.loads(policy.rules_json) if policy.rules_json else {},
            "is_active": policy.is_active
        }
    finally:
        if is_local:
            session.close()


# 12. write_audit_event(event)
def write_audit_event(event: Dict[str, Any], db: Optional[Session] = None) -> Dict[str, Any]:
    """Record an immutable compliance and security audit event."""
    session, is_local = _get_db(db)
    try:
        audit_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"
        actor = event.get("actor", "System")
        event_type = event.get("event_type", "GENERAL_AUDIT")
        request_id = event.get("request_id", f"REQ-{uuid.uuid4().hex[:6].upper()}")
        details = event.get("details", {})

        audit_entry = AuditEvent(
            id=audit_id,
            timestamp=datetime.datetime.utcnow(),
            actor=actor,
            event_type=event_type,
            request_id=request_id,
            details_json=json.dumps(details) if isinstance(details, (dict, list)) else str(details)
        )
        session.add(audit_entry)
        session.commit()

        return {
            "success": True,
            "audit_id": audit_id,
            "timestamp": audit_entry.timestamp.isoformat(),
            "actor": actor,
            "event_type": event_type,
            "request_id": request_id
        }
    except Exception as e:
        session.rollback()
        return {"success": False, "error": str(e)}
    finally:
        if is_local:
            session.close()
