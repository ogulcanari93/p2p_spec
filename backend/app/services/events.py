import json
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models import RequestEvent, RequestEventType


def record_event(
    db: Session,
    *,
    payment_request_id: str,
    event_type: RequestEventType | str,
    actor_user_id: str | None = None,
    previous_status: str | None = None,
    new_status: str | None = None,
    metadata: dict[str, Any] | None = None,
    ip_address_hash: str | None = None,
    user_agent_hash: str | None = None,
) -> RequestEvent:
    safe_metadata = metadata or {}
    allowed_keys = {"amount_minor", "currency", "direction"}
    filtered = {k: v for k, v in safe_metadata.items() if k in allowed_keys}

    event = RequestEvent(
        id=str(uuid.uuid4()),
        payment_request_id=payment_request_id,
        actor_user_id=actor_user_id,
        event_type=event_type.value if isinstance(event_type, RequestEventType) else event_type,
        previous_status=previous_status,
        new_status=new_status,
        metadata_json=json.dumps(filtered) if filtered else None,
        ip_address_hash=ip_address_hash,
        user_agent_hash=user_agent_hash,
    )
    db.add(event)
    return event
