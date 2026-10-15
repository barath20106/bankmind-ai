import pytest
from app.tools.banking_tools import (
    get_customer,
    search_customers,
    get_accounts,
    get_account_balance,
    get_transactions,
    calculate_spending_summary,
    analyze_transaction_risk,
    list_fraud_alerts,
    calculate_emi,
    calculate_loan_eligibility,
    get_compliance_policy,
    write_audit_event
)


def test_customer_lookup(db_session):
    cust = get_customer("CUST-1001", db=db_session)
    assert cust["found"] is True
    assert cust["id"] == "CUST-1001"
    assert cust["full_name"] == "Rajesh Sharma"
    assert cust["city"] == "Mumbai"
    assert cust["kyc_status"] == "VERIFIED"


def test_customer_lookup_unknown(db_session):
    cust = get_customer("CUST-9999", db=db_session)
    assert cust["found"] is False
    assert "not found" in cust["error"].lower()


def test_search_customers(db_session):
    results = search_customers("Priya", db=db_session)
    assert len(results) >= 1
    assert any(c["id"] == "CUST-1002" for c in results)

    results_city = search_customers("Mumbai", db=db_session)
    assert len(results_city) >= 2


def test_get_accounts_and_balance(db_session):
    accounts = get_accounts("CUST-1001", db=db_session)
    assert len(accounts) >= 2
    assert any(a["id"] == "ACCT-2001" for a in accounts)

    acct = get_account_balance("ACCT-2001", db=db_session)
    assert acct["found"] is True
    assert acct["balance"] > 100000.0
    assert acct["currency"] == "INR"


def test_get_transactions_and_spending_summary(db_session):
    txns = get_transactions("CUST-1001", limit=10, db=db_session)
    assert len(txns) >= 5

    # Filter by DEBIT
    debits = get_transactions("CUST-1001", limit=10, filters={"txn_type": "DEBIT"}, db=db_session)
    assert all(t["txn_type"] == "DEBIT" for t in debits)

    summary = calculate_spending_summary("CUST-1001", db=db_session)
    assert summary["total_debits"] > 0
    assert summary["total_credits"] > 0
    assert "category_breakdown" in summary
    assert summary["currency"] == "INR"


def test_calculate_emi():
    # Principal: 3,00,000, 10.5% p.a., 36 months
    emi_res = calculate_emi(300000, 10.5, 36)
    assert emi_res["principal"] == 300000
    assert emi_res["monthly_emi"] > 9000
    assert emi_res["monthly_emi"] < 10500
    assert emi_res["total_payable"] > 300000
    assert "Simulated" in emi_res["disclaimer"]


def test_calculate_emi_invalid():
    res = calculate_emi(-5000, 10.5, 12)
    assert "error" in res


def test_fraud_rule_behavior_high_risk(db_session):
    # TXN-3001 is a 2,75,000 offshore wire to Dubai
    risk = analyze_transaction_risk("TXN-3001", db=db_session)
    assert risk["found"] is True
    assert risk["risk_score"] >= 80
    assert risk["risk_level"] in ["HIGH", "CRITICAL"]
    assert risk["recommended_action"] == "BLOCK_AND_VERIFY"
    assert len(risk["triggered_rules"]) >= 2


def test_fraud_rule_behavior_normal(db_session):
    # TXN-3004 is a grocery transaction in Mumbai
    risk = analyze_transaction_risk("TXN-3004", db=db_session)
    assert risk["found"] is True
    assert risk["risk_score"] < 40
    assert risk["risk_level"] == "LOW"
    assert risk["recommended_action"] == "APPROVE_TRANSACTION"


def test_list_fraud_alerts(db_session):
    alerts = list_fraud_alerts(db=db_session)
    assert len(alerts) >= 5
    assert any(a["id"] == "FA-5001" for a in alerts)


def test_loan_eligibility_qualified(db_session):
    # CUST-1002 (Priya Patel, income 145000, credit 780)
    res = calculate_loan_eligibility("CUST-1002", 300000, 36, db=db_session)
    assert res["found"] is True
    assert res["is_eligible"] is True
    assert res["status"] == "ELIGIBLE"
    assert res["debt_to_income_ratio"] < 40.0


def test_loan_eligibility_unverified_kyc(db_session):
    # CUST-1007 (Rohan Mehra, KYC status PENDING, credit 590)
    res = calculate_loan_eligibility("CUST-1007", 200000, 24, db=db_session)
    assert res["found"] is True
    assert res["is_eligible"] is False
    assert res["status"] == "INELIGIBLE"
    assert any("KYC" in r for r in res["reasons"])


def test_compliance_policy_lookup(db_session):
    pol = get_compliance_policy("AML-CFT-01", db=db_session)
    assert pol["found"] is True
    assert pol["code"] == "AML-CFT-01"
    assert pol["aml_flag_threshold"] == 200000.0


def test_write_audit_event(db_session):
    evt = {
        "actor": "TestingSuite",
        "event_type": "UNIT_TEST_VERIFY",
        "request_id": "REQ-TEST-001",
        "details": {"test_name": "test_write_audit_event", "passed": True}
    }
    res = write_audit_event(evt, db=db_session)
    assert res["success"] is True
    assert res["audit_id"].startswith("AUD-")
