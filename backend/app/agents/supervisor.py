import time
import uuid
import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.models import ExecutionTrace
from app.services.llm_provider import llm_provider
from app.agents.banking import BankingAgent
from app.agents.risk_fraud import RiskFraudAgent
from app.agents.credit_loan import CreditLoanAgent
from app.agents.compliance import ComplianceAgent

logger = logging.getLogger("bankmind.supervisor")


class SupervisorAgent:
    name: str = "SupervisorAgent"
    role: str = "Orchestrator & Intent Routing Supervisor"
    description: str = "Decomposes banking requests, delegates to domain specialists, audits workflows, and grounds final answers in tool outputs."

    def __init__(self):
        self.specialists = {
            "BankingAgent": BankingAgent(),
            "RiskFraudAgent": RiskFraudAgent(),
            "CreditLoanAgent": CreditLoanAgent(),
            "ComplianceAgent": ComplianceAgent()
        }

    def process_request(
        self,
        user_query: str,
        customer_id_override: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        End-to-end multi-agent execution pipeline:
        1. Classify intent and identify required specialists.
        2. Route sequentially / in coordination to specialists.
        3. Collect real tool outputs and compile execution traces.
        4. Synthesize final answer grounded strictly in verified tool results.
        5. Persist traces and audit records to database.
        """
        request_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
        start_time = time.time()
        traces: List[Dict[str, Any]] = []
        agent_results: Dict[str, Any] = {}
        tools_invoked: List[str] = []
        warnings: List[str] = []

        # Step 1: Intent Classification & Routing Plan
        t0 = time.time()
        routing = llm_provider.classify_intent(user_query)
        classify_latency = (time.time() - t0) * 1000

        if customer_id_override and not routing.get("customer_id"):
            routing["customer_id"] = customer_id_override

        traces.append({
            "step_index": 1,
            "agent_name": self.name,
            "tool_name": "classify_intent",
            "status": "SUCCESS",
            "latency_ms": round(classify_latency, 2),
            "input_payload": {"query": user_query},
            "output_payload": routing,
            "summary": f"Intent: {routing.get('primary_intent')} | Specialists: {', '.join(routing.get('agents', []))}"
        })
        tools_invoked.append("classify_intent")

        selected_agents = routing.get("agents", [])

        # If unknown query or no agents routed
        if not selected_agents or routing.get("primary_intent") == "UNKNOWN":
            answer = llm_provider.synthesize_response(user_query, routing, {}, traces)
            total_latency = (time.time() - start_time) * 1000

            self._persist_traces(request_id, traces, db)

            return {
                "request_id": request_id,
                "answer": answer,
                "selected_agents": [self.name],
                "tools_invoked": tools_invoked,
                "traces": traces,
                "provider": llm_provider.provider_info["provider"],
                "model": llm_provider.provider_info["model"],
                "latency_ms": round(total_latency, 2),
                "warnings": ["Request was ambiguous or general. Clarification guidance returned."]
            }

        # Step 2: Delegate to Domain Specialist Agents
        step_idx = 2
        for agent_name in selected_agents:
            specialist = self.specialists.get(agent_name)
            if not specialist:
                continue

            try:
                # Prepare specialist params based on routing
                specialist_params = {
                    "customer_id": routing.get("customer_id"),
                    "transaction_id": routing.get("transaction_id"),
                    "loan_amount": routing.get("loan_amount"),
                    "loan_tenure": routing.get("loan_tenure"),
                    "request_id": request_id,
                    "actor": agent_name,
                    "event_type": f"{agent_name.upper()}_TASK_EXECUTION",
                    "audit_details": {"query": user_query, "routing": routing}
                }

                agent_out = specialist.execute(specialist_params, db=db)
                agent_results[agent_name] = agent_out.get("data", {})

                # Merge agent traces
                for t in agent_out.get("traces", []):
                    t["step_index"] = step_idx
                    traces.append(t)
                    tools_invoked.append(t.get("tool_name", "unknown_tool"))
                    step_idx += 1

            except Exception as e:
                logger.error(f"Error executing agent {agent_name}: {e}")
                err_msg = str(e)
                warnings.append(f"{agent_name} encountered an error: {err_msg}")
                traces.append({
                    "step_index": step_idx,
                    "agent_name": agent_name,
                    "tool_name": "agent_execution",
                    "status": "FAILED",
                    "latency_ms": 0.0,
                    "input_payload": {"agent": agent_name},
                    "output_payload": {"error": err_msg},
                    "summary": f"Failed executing {agent_name}: {err_msg}"
                })
                step_idx += 1

        # Step 3: Synthesis of Grounded Response
        t0 = time.time()
        final_answer = llm_provider.synthesize_response(user_query, routing, agent_results, traces)
        synth_latency = (time.time() - t0) * 1000

        traces.append({
            "step_index": step_idx,
            "agent_name": self.name,
            "tool_name": "synthesize_grounded_response",
            "status": "SUCCESS",
            "latency_ms": round(synth_latency, 2),
            "input_payload": {"tool_results_count": len(agent_results)},
            "output_payload": {"answer_length": len(final_answer)},
            "summary": "Synthesized final answer strictly grounded in verified Python tool outputs"
        })
        tools_invoked.append("synthesize_grounded_response")

        total_latency = (time.time() - start_time) * 1000

        # Step 4: Persist Traces to Database
        self._persist_traces(request_id, traces, db)

        return {
            "request_id": request_id,
            "answer": final_answer,
            "selected_agents": selected_agents,
            "tools_invoked": tools_invoked,
            "traces": traces,
            "provider": llm_provider.provider_info["provider"],
            "model": llm_provider.provider_info["model"],
            "latency_ms": round(total_latency, 2),
            "warnings": warnings
        }

    def _persist_traces(self, request_id: str, traces: List[Dict[str, Any]], db: Optional[Session]):
        """Save execution traces to the SQLite database for audit and inspection."""
        if db is None:
            return
        try:
            trace_objs = []
            for t in traces:
                trace_id = f"TRC-{uuid.uuid4().hex[:8].upper()}"
                trace_objs.append(
                    ExecutionTrace(
                        id=trace_id,
                        request_id=request_id,
                        step_index=t.get("step_index", 0),
                        agent_name=t.get("agent_name", "Unknown"),
                        tool_name=t.get("tool_name", "Unknown"),
                        status=t.get("status", "SUCCESS"),
                        input_payload=json.dumps(t.get("input_payload", {}), default=str),
                        output_payload=json.dumps(t.get("output_payload", {}), default=str),
                        latency_ms=t.get("latency_ms", 0.0),
                        warning=t.get("warning")
                    )
                )
            db.add_all(trace_objs)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.warning(f"Failed to persist execution traces: {e}")


supervisor_agent = SupervisorAgent()
