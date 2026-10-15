from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.tools.banking_tools import list_fraud_alerts, analyze_transaction_risk
from app.schemas.schemas import FraudAlertResponse, FraudAnalysisRequest, FraudAnalysisResponse

router = APIRouter(prefix="/fraud", tags=["Fraud & Risk"])


@router.get("/alerts", response_model=List[FraudAlertResponse])
def get_fraud_alerts(
    status: Optional[str] = Query(None, description="Filter by status: NEW, INVESTIGATING, RESOLVED, DISMISSED"),
    db: Session = Depends(get_db)
):
    """Retrieve simulated fraud alerts from surveillance monitoring."""
    alerts = list_fraud_alerts(status=status, db=db)
    return alerts


@router.post("/analyze", response_model=FraudAnalysisResponse)
def analyze_transaction(
    payload: FraudAnalysisRequest,
    db: Session = Depends(get_db)
):
    """Run deterministic fraud detection heuristics on any transaction ID."""
    result = analyze_transaction_risk(payload.transaction_id, db=db)
    if not result.get("found", True):
        raise HTTPException(status_code=404, detail=f"Transaction '{payload.transaction_id}' not found.")
    
    return FraudAnalysisResponse(
        transaction_id=result["transaction_id"],
        customer_id=result["customer_id"],
        amount=result["amount"],
        merchant=result["merchant"],
        location=result["location"],
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        triggered_rules=result["triggered_rules"],
        recommended_action=result["recommended_action"],
        is_flagged=result["is_flagged"],
        details=result,
        disclaimer=result.get("disclaimer", "Simulated fraud detection.")
    )
