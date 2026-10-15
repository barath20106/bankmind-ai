from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.models import ExecutionTrace
from app.schemas.schemas import ExecutionTraceResponse

router = APIRouter(prefix="/traces", tags=["Traces"])


@router.get("", response_model=List[ExecutionTraceResponse])
def list_execution_traces(
    request_id: Optional[str] = Query(None, description="Filter by request ID"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve recorded multi-agent execution traces for auditing and observability."""
    query = db.query(ExecutionTrace)
    if request_id:
        query = query.filter(ExecutionTrace.request_id == request_id.strip())
    traces = query.order_by(desc(ExecutionTrace.timestamp)).limit(limit).all()
    return [ExecutionTraceResponse.model_validate(t) for t in traces]
