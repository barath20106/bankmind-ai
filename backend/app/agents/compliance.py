import time
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.tools.banking_tools import (
    get_compliance_policy,
    write_audit_event
)


class ComplianceAgent:
    name: str = "ComplianceAgent"
    role: str = "Regulatory & Governance Officer"
    description: str = "Validates banking compliance policies, reviews KYC mandates, verifies audit adherence, and records immutable system logs."

    def execute(self, params: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Execute compliance validations and write immutable audit records.
        """
        results: Dict[str, Any] = {}
        traces: List[Dict[str, Any]] = []

        policy_code = params.get("policy_code", "AML-CFT-01")
        request_id = params.get("request_id", "REQ-SYS")
        actor = params.get("actor", "SupervisorAgent")
        event_type = params.get("event_type", "POLICY_VERIFICATION")
        audit_details = params.get("audit_details", {})

        # 1. Fetch compliance policy
        t0 = time.time()
        policy_data = get_compliance_policy(policy_code, db=db)
        latency = (time.time() - t0) * 1000
        results["policy"] = policy_data
        traces.append({
            "agent_name": self.name,
            "tool_name": "get_compliance_policy",
            "status": "SUCCESS" if policy_data.get("found", True) else "FAILED",
            "latency_ms": round(latency, 2),
            "input_payload": {"policy_name": policy_code},
            "output_payload": {
                "code": policy_data.get("code"),
                "name": policy_data.get("name"),
                "aml_threshold": policy_data.get("aml_flag_threshold")
            },
            "summary": f"Verified compliance policy: {policy_data.get('code')} - {policy_data.get('name')}"
        })

        # 2. Write Audit Event
        t0 = time.time()
        audit_res = write_audit_event({
            "actor": actor,
            "event_type": event_type,
            "request_id": request_id,
            "details": audit_details
        }, db=db)
        latency = (time.time() - t0) * 1000
        results["audit_event"] = audit_res
        traces.append({
            "agent_name": self.name,
            "tool_name": "write_audit_event",
            "status": "SUCCESS" if audit_res.get("success") else "FAILED",
            "latency_ms": round(latency, 2),
            "input_payload": {"actor": actor, "event_type": event_type, "request_id": request_id},
            "output_payload": audit_res,
            "summary": f"Logged immutable audit event {audit_res.get('audit_id')} for {event_type}"
        })

        return {
            "agent": self.name,
            "data": results,
            "traces": traces
        }
