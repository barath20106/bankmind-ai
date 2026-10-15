from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.core.database import get_db
from app.models.models import Customer, Account, Transaction
from app.schemas.schemas import CustomerResponse, AccountResponse, TransactionResponse

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=List[CustomerResponse])
def list_customers(
    search: Optional[str] = Query(None, description="Search by name, ID, email, or city"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve list of customers with optional search filtering."""
    query = db.query(Customer)
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Customer.id.ilike(s),
                Customer.full_name.ilike(s),
                Customer.email.ilike(s),
                Customer.city.ilike(s)
            )
        )
    customers = query.order_by(Customer.id).limit(limit).all()
    return [CustomerResponse.model_validate(c) for c in customers]


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer_by_id(customer_id: str, db: Session = Depends(get_db)):
    """Retrieve customer details by ID."""
    cust = db.query(Customer).filter(Customer.id == customer_id.strip()).first()
    if not cust:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found.")
    return CustomerResponse.model_validate(cust)


@router.get("/{customer_id}/accounts", response_model=List[AccountResponse])
def get_customer_accounts(customer_id: str, db: Session = Depends(get_db)):
    """Retrieve all bank accounts belonging to a customer."""
    cust = db.query(Customer).filter(Customer.id == customer_id.strip()).first()
    if not cust:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found.")
    accounts = db.query(Account).filter(Account.customer_id == customer_id.strip()).all()
    return [AccountResponse.model_validate(a) for a in accounts]


@router.get("/{customer_id}/transactions", response_model=List[TransactionResponse])
def get_customer_transactions(
    customer_id: str,
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    txn_type: Optional[str] = None,
    is_flagged: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Retrieve transactions for a customer with optional filtering."""
    cust = db.query(Customer).filter(Customer.id == customer_id.strip()).first()
    if not cust:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found.")

    query = db.query(Transaction).filter(Transaction.customer_id == customer_id.strip())
    if category:
        query = query.filter(Transaction.category.ilike(f"%{category.strip()}%"))
    if txn_type:
        query = query.filter(Transaction.txn_type == txn_type.strip().upper())
    if is_flagged is not None:
        query = query.filter(Transaction.is_flagged == is_flagged)

    txns = query.order_by(desc(Transaction.timestamp)).limit(limit).all()
    return [TransactionResponse.model_validate(t) for t in txns]
