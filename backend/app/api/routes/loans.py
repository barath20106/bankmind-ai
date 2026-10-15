from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.models import LoanApplication
from app.tools.banking_tools import calculate_loan_eligibility, calculate_emi
from app.schemas.schemas import (
    LoanApplicationResponse,
    LoanEligibilityRequest,
    LoanEligibilityResponse,
    EMICalculationRequest,
    EMICalculationResponse
)

router = APIRouter(prefix="/loans", tags=["Credit & Loans"])


@router.get("", response_model=List[LoanApplicationResponse])
def list_loans(db: Session = Depends(get_db)):
    """Retrieve simulated loan applications."""
    loans = db.query(LoanApplication).order_by(desc(LoanApplication.created_at)).all()
    return [LoanApplicationResponse.model_validate(l) for l in loans]


@router.get("/{loan_id}", response_model=LoanApplicationResponse)
def get_loan(loan_id: str, db: Session = Depends(get_db)):
    """Retrieve a specific loan application."""
    loan = db.query(LoanApplication).filter(LoanApplication.id == loan_id.strip()).first()
    if not loan:
        raise HTTPException(status_code=404, detail=f"Loan application '{loan_id}' not found.")
    return LoanApplicationResponse.model_validate(loan)


@router.post("/eligibility", response_model=LoanEligibilityResponse)
def evaluate_loan_eligibility(
    payload: LoanEligibilityRequest,
    db: Session = Depends(get_db)
):
    """Evaluate customer eligibility for a loan with DTI ratio, EMI, and credit score."""
    result = calculate_loan_eligibility(
        customer_id=payload.customer_id,
        requested_amount=payload.requested_amount,
        tenure_months=payload.tenure_months,
        db=db
    )
    if not result.get("found", True):
        raise HTTPException(status_code=404, detail=result.get("error", "Customer not found."))

    return LoanEligibilityResponse(
        customer_id=result["customer_id"],
        customer_name=result["customer_name"],
        requested_amount=result["requested_amount"],
        tenure_months=result["tenure_months"],
        monthly_income=result["monthly_income"],
        existing_obligations=result["existing_obligations"],
        estimated_emi=result["estimated_emi"],
        proposed_total_obligations=result["proposed_total_obligations"],
        debt_to_income_ratio=result["debt_to_income_ratio"],
        max_permissible_dti=result["max_permissible_dti"],
        credit_score=result["credit_score"],
        min_required_credit_score=result["min_required_credit_score"],
        is_eligible=result["is_eligible"],
        status=result["status"],
        reasons=result["reasons"],
        disclaimer=result.get("disclaimer", "Simulated non-binding evaluation.")
    )


@router.post("/emi", response_model=EMICalculationResponse)
def calculate_loan_emi(payload: EMICalculationRequest):
    """Calculate monthly loan installment using standard amortization formula."""
    res = calculate_emi(
        principal=payload.principal,
        annual_interest_rate=payload.annual_interest_rate,
        tenure_months=payload.tenure_months
    )
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])

    return EMICalculationResponse(**res)
