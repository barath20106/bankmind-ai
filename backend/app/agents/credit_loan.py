import time
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.tools.banking_tools import (
    calculate_loan_eligibility,
    calculate_emi,
    get_loan_application
)


class CreditLoanAgent:
    name: str = "CreditLoanAgent"
    role: str = "Credit Underwriting & Lending Specialist"
    description: str = "Computes EMI amortization schedules, evaluates Debt-to-Income (DTI) metrics, verifies credit scores, and determines loan eligibility."

    def execute(self, params: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Execute simulated loan underwriting and eligibility evaluation.
        Labels every result as simulated and non-binding.
        """
        results: Dict[str, Any] = {}
        traces: List[Dict[str, Any]] = []

        customer_id = params.get("customer_id")
        requested_amount = float(params.get("loan_amount") or 300000.0)
        tenure_months = int(params.get("loan_tenure") or 36)
        annual_rate = float(params.get("annual_rate") or 10.5)

        # 1. Calculate Loan Eligibility
        if customer_id:
            t0 = time.time()
            eligibility_data = calculate_loan_eligibility(
                customer_id=customer_id,
                requested_amount=requested_amount,
                tenure_months=tenure_months,
                db=db
            )
            latency = (time.time() - t0) * 1000
            results["eligibility"] = eligibility_data
            traces.append({
                "agent_name": self.name,
                "tool_name": "calculate_loan_eligibility",
                "status": "SUCCESS" if eligibility_data.get("found", True) else "FAILED",
                "latency_ms": round(latency, 2),
                "input_payload": {
                    "customer_id": customer_id,
                    "requested_amount": requested_amount,
                    "tenure_months": tenure_months
                },
                "output_payload": {
                    "status": eligibility_data.get("status"),
                    "is_eligible": eligibility_data.get("is_eligible"),
                    "estimated_emi": eligibility_data.get("estimated_emi"),
                    "dti_ratio": eligibility_data.get("debt_to_income_ratio")
                },
                "summary": f"Calculated eligibility for {customer_id}: {eligibility_data.get('status')} (EMI ₹{eligibility_data.get('estimated_emi', 0):,.2f}, DTI {eligibility_data.get('debt_to_income_ratio')}%)"
            })

        # 2. Standalone EMI calculation
        t0 = time.time()
        emi_data = calculate_emi(
            principal=requested_amount,
            annual_interest_rate=annual_rate,
            tenure_months=tenure_months
        )
        latency = (time.time() - t0) * 1000
        results["emi_schedule"] = emi_data
        traces.append({
            "agent_name": self.name,
            "tool_name": "calculate_emi",
            "status": "SUCCESS",
            "latency_ms": round(latency, 2),
            "input_payload": {
                "principal": requested_amount,
                "annual_interest_rate": annual_rate,
                "tenure_months": tenure_months
            },
            "output_payload": emi_data,
            "summary": f"Computed EMI schedule: ₹{emi_data.get('monthly_emi'):,.2f}/mo for ₹{requested_amount:,.2f} over {tenure_months}m"
        })

        return {
            "agent": self.name,
            "data": results,
            "traces": traces,
            "disclaimer": "Simulated credit underwriting calculation. Strictly non-binding."
        }
