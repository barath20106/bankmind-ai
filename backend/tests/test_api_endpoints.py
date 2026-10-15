import pytest


def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["is_simulated_system"] is True


def test_dashboard_summary_endpoint(client):
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_customers"] >= 8
    assert data["total_accounts"] >= 10
    assert data["total_deposits"] > 0
    assert len(data["activity_chart"]) > 0
    assert len(data["recent_transactions"]) > 0


def test_customers_endpoints(client):
    # List customers
    res = client.get("/api/customers")
    assert res.status_code == 200
    customers = res.json()
    assert len(customers) >= 8

    # Search customer
    res_search = client.get("/api/customers?search=Priya")
    assert res_search.status_code == 200
    assert len(res_search.json()) >= 1

    # Single customer
    res_single = client.get("/api/customers/CUST-1001")
    assert res_single.status_code == 200
    assert res_single.json()["id"] == "CUST-1001"

    # Customer accounts
    res_accts = client.get("/api/customers/CUST-1001/accounts")
    assert res_accts.status_code == 200
    assert len(res_accts.json()) >= 2

    # Customer transactions
    res_txns = client.get("/api/customers/CUST-1001/transactions")
    assert res_txns.status_code == 200
    assert len(res_txns.json()) >= 1


def test_customer_not_found(client):
    res = client.get("/api/customers/CUST-NONEXISTENT")
    assert res.status_code == 404


def test_fraud_endpoints(client):
    # List alerts
    res = client.get("/api/fraud/alerts")
    assert res.status_code == 200
    alerts = res.json()
    assert len(alerts) >= 5

    # Analyze suspicious transaction
    res_analyze = client.post("/api/fraud/analyze", json={"transaction_id": "TXN-3001"})
    assert res_analyze.status_code == 200
    analysis = res_analyze.json()
    assert analysis["transaction_id"] == "TXN-3001"
    assert analysis["risk_score"] >= 80
    assert analysis["risk_level"] in ["HIGH", "CRITICAL"]


def test_fraud_analyze_not_found(client):
    res = client.post("/api/fraud/analyze", json={"transaction_id": "TXN-INVALID"})
    assert res.status_code == 404


def test_loans_endpoints(client):
    # List loans
    res = client.get("/api/loans")
    assert res.status_code == 200
    loans = res.json()
    assert len(loans) >= 5

    # Eligibility check
    eligibility_payload = {
        "customer_id": "CUST-1002",
        "requested_amount": 300000.0,
        "tenure_months": 36,
        "annual_interest_rate": 10.5
    }
    res_elig = client.post("/api/loans/eligibility", json=eligibility_payload)
    assert res_elig.status_code == 200
    data = res_elig.json()
    assert data["customer_id"] == "CUST-1002"
    assert data["is_eligible"] is True
    assert data["estimated_emi"] > 0

    # EMI calculation
    emi_payload = {
        "principal": 500000.0,
        "annual_interest_rate": 10.5,
        "tenure_months": 48
    }
    res_emi = client.post("/api/loans/emi", json=emi_payload)
    assert res_emi.status_code == 200
    assert res_emi.json()["monthly_emi"] > 10000


def test_chat_endpoint(client):
    # Chat with supervisor for Use Case 1
    chat_payload = {
        "message": "What is the current balance of customer CUST-1001?"
    }
    res = client.post("/api/chat", json=chat_payload)
    assert res.status_code == 200
    chat_data = res.json()
    assert "BankingAgent" in chat_data["selected_agents"]
    assert "₹" in chat_data["answer"]
    assert len(chat_data["traces"]) > 0
    assert "provider" in chat_data
    assert "model" in chat_data


def test_agents_endpoint(client):
    res = client.get("/api/agents")
    assert res.status_code == 200
    agents = res.json()
    assert len(agents) >= 5
    agent_names = [a["name"] for a in agents]
    assert "SupervisorAgent" in agent_names
    assert "BankingAgent" in agent_names
    assert "RiskFraudAgent" in agent_names
    assert "CreditLoanAgent" in agent_names
    assert "ComplianceAgent" in agent_names


def test_traces_and_audit_endpoints(client):
    # Run a chat query to ensure traces exist
    client.post("/api/chat", json={"message": "What is the current balance of customer CUST-1001?"})

    # List traces
    res_traces = client.get("/api/traces")
    assert res_traces.status_code == 200
    assert len(res_traces.json()) > 0

    # List audit events
    res_audit = client.get("/api/audit")
    assert res_audit.status_code == 200
    assert len(res_audit.json()) > 0
