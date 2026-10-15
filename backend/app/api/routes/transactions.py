from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.models import Transaction
from app.schemas.schemas import TransactionResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=List[TransactionResponse])
def list_transactions(
    limit: int = Query(50, ge=1, le=200),
    category: Optional[str] = None,
    txn_type: Optional[str] = None,
    is_flagged: Optional[bool] = None,
    customer_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List transactions with optional filtering."""
    query = db.query(Transaction)
    if customer_id:
        query = query.filter(Transaction.customer_id == customer_id.strip())
    if category:
        query = query.filter(Transaction.category.ilike(f"%{category.strip()}%"))
    if txn_type:
        query = query.filter(Transaction.txn_type == txn_type.strip().upper())
    if is_flagged is not None:
        query = query.filter(Transaction.is_flagged == is_flagged)

    txns = query.order_by(desc(Transaction.timestamp)).limit(limit).all()
    return [TransactionResponse.model_validate(t) for t in txns]


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction_detail(transaction_id: str, db: Session = Depends(get_db)):
    """Retrieve details of a single transaction."""
    txn = db.query(Transaction).filter(Transaction.id == transaction_id.strip()).first()
    if not txn:
        raise HTTPException(status_code=404, detail=f"Transaction '{transaction_id}' not found.")
    return TransactionResponse.model_validate(txn)
