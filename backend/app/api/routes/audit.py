import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.models import AuditEvent
from app.schemas.schemas import AuditEventResponse

router = APIRouter(prefix="/audit", tags=["Audit Log"])


@router.get("", response_model=List[AuditEventResponse])
def list_audit_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve immutable compliance audit events."""
    query = db.query(AuditEvent)
    if event_type:
        query = query.filter(AuditEvent.event_type.ilike(f"%{event_type.strip()}%"))
    events = query.order_by(desc(AuditEvent.timestamp)).limit(limit).all()

    results = []
    for e in events:
        try:
            details_obj = json.loads(e.details_json) if e.details_json else {}
        except Exception:
            details_obj = {"raw": e.details_json}

        results.append(
            AuditEventResponse(
                id=e.id,
                timestamp=e.timestamp,
                actor=e.actor,
                event_type=e.event_type,
                request_id=e.request_id,
                details=details_obj
            )
        )
    return results
