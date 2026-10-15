from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.agents.supervisor import supervisor_agent
from app.schemas.schemas import ChatRequest, ChatResponse, ExecutionTraceItem

router = APIRouter(prefix="/chat", tags=["AI Assistant"])


@router.post("", response_model=ChatResponse)
def chat_with_supervisor(
    payload: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Core AI banking assistant endpoint.
    Accepts natural-language queries, orchestrates multi-agent tool execution,
    and returns grounded responses with step-by-step traces.
    """
    result = supervisor_agent.process_request(
        user_query=payload.message,
        customer_id_override=payload.customer_id,
        db=db
    )

    trace_items = [
        ExecutionTraceItem(
            step_index=t.get("step_index", 0),
            agent_name=t.get("agent_name", "Unknown"),
            tool_name=t.get("tool_name", "Unknown"),
            status=t.get("status", "SUCCESS"),
            latency_ms=t.get("latency_ms", 0.0),
            input_payload=t.get("input_payload", {}),
            output_payload=t.get("output_payload", {}),
            summary=t.get("summary", ""),
            warning=t.get("warning")
        )
        for t in result["traces"]
    ]

    return ChatResponse(
        request_id=result["request_id"],
        answer=result["answer"],
        selected_agents=result["selected_agents"],
        tools_invoked=result["tools_invoked"],
        traces=trace_items,
        provider=result["provider"],
        model=result["model"],
        latency_ms=result["latency_ms"],
        warnings=result.get("warnings", [])
    )
