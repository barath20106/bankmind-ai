from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Account
from app.schemas.schemas import AccountResponse

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("", response_model=List[AccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    """Retrieve all simulated bank accounts."""
    accounts = db.query(Account).all()
    return [AccountResponse.model_validate(a) for a in accounts]


@router.get("/{account_id}", response_model=AccountResponse)
def get_account_detail(account_id: str, db: Session = Depends(get_db)):
    """Retrieve details and live balance of a specific bank account."""
    account = db.query(Account).filter(Account.id == account_id.strip()).first()
    if not account:
        raise HTTPException(status_code=404, detail=f"Account '{account_id}' not found.")
    return AccountResponse.model_validate(account)
