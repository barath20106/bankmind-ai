import time
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.tools.banking_tools import (
    analyze_transaction_risk,
    list_fraud_alerts
)


class RiskFraudAgent:
    name: str = "RiskFraudAgent"
    role: str = "Fraud Detection & Surveillance Specialist"
    description: str = "Runs deterministic fraud heuristics, AML thresholds, geo-anomaly detection, velocity checks, and assigns risk scores."

    def execute(self, params: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Execute risk and fraud surveillance checks.
        Explicitly distinguishes deterministic rule-based signals from AI interpretations.
        """
        results: Dict[str, Any] = {}
        traces: List[Dict[str, Any]] = []

        transaction_id = params.get("transaction_id")
        customer_id = params.get("customer_id")

        if transaction_id:
            t0 = time.time()
            risk_data = analyze_transaction_risk(transaction_id, db=db)
            latency = (time.time() - t0) * 1000
            results["risk_analysis"] = risk_data
            traces.append({
                "agent_name": self.name,
                "tool_name": "analyze_transaction_risk",
                "status": "SUCCESS" if risk_data.get("found", True) else "FAILED",
                "latency_ms": round(latency, 2),
                "input_payload": {"transaction_id": transaction_id},
                "output_payload": {
                    "risk_score": risk_data.get("risk_score"),
                    "risk_level": risk_data.get("risk_level"),
                    "triggered_rules": risk_data.get("triggered_rules"),
                    "recommended_action": risk_data.get("recommended_action")
                },
                "summary": f"Analyzed {transaction_id}: Risk Score {risk_data.get('risk_score', 0)} ({risk_data.get('risk_level')}) - Action: {risk_data.get('recommended_action')}"
            })

        # List active fraud alerts for context
        t0 = time.time()
        alerts_data = list_fraud_alerts(status=None, db=db)
        latency = (time.time() - t0) * 1000
        # If customer_id provided, filter alerts
        if customer_id:
            alerts_data = [a for a in alerts_data if a.get("customer_id") == customer_id]
        results["active_alerts"] = alerts_data
        traces.append({
            "agent_name": self.name,
            "tool_name": "list_fraud_alerts",
            "status": "SUCCESS",
            "latency_ms": round(latency, 2),
            "input_payload": {"customer_id": customer_id},
            "output_payload": {"alerts_count": len(alerts_data), "alerts": alerts_data[:3]},
            "summary": f"Retrieved {len(alerts_data)} active fraud alert(s)"
        })

        return {
            "agent": self.name,
            "data": results,
            "traces": traces
        }
