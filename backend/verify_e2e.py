import json
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.seed import seed_database
from app.agents.supervisor import supervisor_agent


def run_e2e_verification():
    print("==================================================================")
    print("BankMind AI — End-to-End Multi-Agent Use Case Verification")
    print("==================================================================")

    # 1. Initialize DB and Seed
    db = SessionLocal()
    seed_res = seed_database(db=db, force_recreate=True)
    print(f"\n[INIT] Database Seed Status: {seed_res['status']} - {seed_res['message']}")

    use_cases = [
        {
            "num": 1,
            "title": "Customer Account Inquiry",
            "prompt": "What is the current balance of customer CUST-1001?",
            "expected_agent": "BankingAgent",
            "expected_check": lambda r: "CUST-1001" in r["answer"] and "₹" in r["answer"]
        },
        {
            "num": 2,
            "title": "Transaction Analysis & Spending",
            "prompt": "Show the last 10 transactions for customer CUST-1001 and summarize their spending.",
            "expected_agent": "BankingAgent",
            "expected_check": lambda r: "Debits" in r["answer"] or "debits" in r["answer"].lower()
        },
        {
            "num": 3,
            "title": "Fraud Investigation",
            "prompt": "Investigate transaction TXN-3001. Why was it flagged?",
            "expected_agent": "RiskFraudAgent",
            "expected_check": lambda r: "TXN-3001" in r["answer"] and ("Dubai" in r["answer"] or "Forex" in r["answer"] or "Risk Score" in r["answer"])
        },
        {
            "num": 4,
            "title": "Loan Eligibility Underwriting",
            "prompt": "Can customer CUST-1002 qualify for a loan of ₹300000 over 36 months?",
            "expected_agent": "CreditLoanAgent",
            "expected_check": lambda r: ("Priya" in r["answer"] or "CUST-1002" in r["answer"]) and "EMI" in r["answer"]
        },
        {
            "num": 5,
            "title": "Cross-Agent Financial Assistance",
            "prompt": "Review customer CUST-1001's spending, check for suspicious activity, and suggest whether a loan payment would be affordable.",
            "expected_agent": "BankingAgent",
            "expected_check": lambda r: "RiskFraudAgent" in r["selected_agents"] and "CreditLoanAgent" in r["selected_agents"]
        },
        {
            "num": 6,
            "title": "Ambiguous / General Inquiry Handling",
            "prompt": "Tell me a joke about robots.",
            "expected_agent": None,
            "expected_check": lambda r: "BankMind AI" in r["answer"]
        }
    ]

    all_passed = True

    for uc in use_cases:
        print(f"\n------------------------------------------------------------------")
        print(f"Executing Use Case {uc['num']}: {uc['title']}")
        print(f"User Query: \"{uc['prompt']}\"")
        print(f"------------------------------------------------------------------")

        result = supervisor_agent.process_request(uc['prompt'], db=db)

        print(f"Request ID:       {result['request_id']}")
        print(f"Selected Agents:  {result['selected_agents']}")
        print(f"Tools Invoked:    {result['tools_invoked']}")
        print(f"Traces Count:     {len(result['traces'])} steps")
        print(f"Execution Latency: {result['latency_ms']} ms")
        print(f"Provider / Model: {result['provider']} / {result['model']}")
        print(f"\nAssistant Response Preview:")
        for line in result['answer'].split('\n')[:8]:
            print(f"  {line}")
        if len(result['answer'].split('\n')) > 8:
            print("  ...")

        # Assertions
        passed = True
        if uc['expected_agent'] and uc['expected_agent'] not in result['selected_agents']:
            print(f"❌ FAILED: Expected agent '{uc['expected_agent']}' not selected.")
            passed = False

        if not uc['expected_check'](result):
            print(f"❌ FAILED: Content assertion check failed.")
            passed = False

        if passed:
            print(f"✅ PASSED Use Case {uc['num']}")
        else:
            all_passed = False

    db.close()
    print("\n==================================================================")
    if all_passed:
        print("🎉 ALL 5 REQUIRED USE CASES + CLARIFICATION VERIFIED SUCCESSFULLY!")
    else:
        print("❌ SOME USE CASES FAILED VERIFICATION.")
    print("==================================================================")
    return all_passed


if __name__ == "__main__":
    success = run_e2e_verification()
    sys.exit(0 if success else 1)
