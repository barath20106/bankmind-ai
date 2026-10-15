from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import get_db
from app.models.models import Customer, Account, Transaction, LoanApplication, FraudAlert
from app.schemas.schemas import DashboardSummaryResponse, ChartPoint, TransactionResponse, FraudAlertResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Retrieve aggregate banking metrics and recent activity for the overview dashboard."""
    total_customers = db.query(Customer).count()
    total_accounts = db.query(Account).count()
    total_deposits = db.query(func.sum(Account.balance)).scalar() or 0.0
    total_transactions = db.query(Transaction).count()
    flagged_txns = db.query(Transaction).filter(Transaction.is_flagged == True).count()
    active_alerts = db.query(FraudAlert).filter(FraudAlert.status.in_(["NEW", "INVESTIGATING"])).count()
    total_loans = db.query(LoanApplication).count()

    # Generate recent activity chart points
    activity_chart = [
        ChartPoint(name="Mon", volume=185000.0, count=8),
        ChartPoint(name="Tue", volume=242000.0, count=12),
        ChartPoint(name="Wed", volume=395000.0, count=15),
        ChartPoint(name="Thu", volume=178000.0, count=9),
        ChartPoint(name="Fri", volume=520000.0, count=18),
        ChartPoint(name="Sat", volume=145000.0, count=6),
        ChartPoint(name="Sun", volume=95000.0, count=4),
    ]

    recent_txns = db.query(Transaction).order_by(desc(Transaction.timestamp)).limit(6).all()
    recent_alerts = db.query(FraudAlert).order_by(desc(FraudAlert.created_at)).limit(5).all()

    return DashboardSummaryResponse(
        total_customers=total_customers,
        total_accounts=total_accounts,
        total_deposits=round(total_deposits, 2),
        total_transactions=total_transactions,
        flagged_transactions_count=flagged_txns,
        active_fraud_alerts=active_alerts,
        total_loan_applications=total_loans,
        system_status="Operational",
        currency="INR",
        activity_chart=activity_chart,
        recent_transactions=[TransactionResponse.model_validate(t) for t in recent_txns],
        recent_alerts=[FraudAlertResponse.model_validate(a) for a in recent_alerts]
    )
