import time
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.tools.banking_tools import (
    get_customer,
    get_accounts,
    get_transactions,
    calculate_spending_summary,
    search_customers
)


class BankingAgent:
    name: str = "BankingAgent"
    role: str = "Core Banking Operations Specialist"
    description: str = "Retrieves customer profiles, linked accounts, real-time balances, transaction histories, and computes spending breakdowns."

    def execute(self, params: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Execute core banking operations based on task parameters.
        Returns actual tool execution results and execution trace metadata.
        """
        results: Dict[str, Any] = {}
        traces: List[Dict[str, Any]] = []

        customer_id = params.get("customer_id")
        action = params.get("action", "full_inquiry")

        # 1. Customer profile lookup
        if customer_id:
            t0 = time.time()
            customer_data = get_customer(customer_id, db=db)
            latency = (time.time() - t0) * 1000
            results["customer"] = customer_data
            traces.append({
                "agent_name": self.name,
                "tool_name": "get_customer",
                "status": "SUCCESS" if customer_data.get("found", True) else "FAILED",
                "latency_ms": round(latency, 2),
                "input_payload": {"customer_id": customer_id},
                "output_payload": customer_data,
                "summary": f"Looked up customer {customer_id}: {customer_data.get('full_name', 'Not found')}"
            })

            # 2. Account balances lookup
            t0 = time.time()
            accounts_data = get_accounts(customer_id, db=db)
            latency = (time.time() - t0) * 1000
            results["accounts"] = accounts_data
            traces.append({
                "agent_name": self.name,
                "tool_name": "get_accounts",
                "status": "SUCCESS",
                "latency_ms": round(latency, 2),
                "input_payload": {"customer_id": customer_id},
                "output_payload": {"accounts_count": len(accounts_data), "accounts": accounts_data},
                "summary": f"Retrieved {len(accounts_data)} account(s) for customer {customer_id}"
            })

            # 3. Transactions lookup
            limit = params.get("limit", 10)
            filters = params.get("filters", {})
            t0 = time.time()
            txns_data = get_transactions(customer_id, limit=limit, filters=filters, db=db)
            latency = (time.time() - t0) * 1000
            results["transactions"] = txns_data
            traces.append({
                "agent_name": self.name,
                "tool_name": "get_transactions",
                "status": "SUCCESS",
                "latency_ms": round(latency, 2),
                "input_payload": {"customer_id": customer_id, "limit": limit, "filters": filters},
                "output_payload": {"transactions_count": len(txns_data), "transactions": txns_data[:3]},
                "summary": f"Retrieved {len(txns_data)} transaction record(s) for customer {customer_id}"
            })

            # 4. Spending summary calculation
            t0 = time.time()
            spending_data = calculate_spending_summary(customer_id, db=db)
            latency = (time.time() - t0) * 1000
            results["spending_summary"] = spending_data
            traces.append({
                "agent_name": self.name,
                "tool_name": "calculate_spending_summary",
                "status": "SUCCESS",
                "latency_ms": round(latency, 2),
                "input_payload": {"customer_id": customer_id},
                "output_payload": spending_data,
                "summary": f"Computed spending summary: Total Debits ₹{spending_data.get('total_debits', 0):,.2f}, Credits ₹{spending_data.get('total_credits', 0):,.2f}"
            })

        return {
            "agent": self.name,
            "data": results,
            "traces": traces
        }
