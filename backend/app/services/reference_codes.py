"""Human-readable payment request reference codes (PR-YYYYMMDD-NNNN)."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import PaymentRequest


def allocate_reference_code(db: Session, *, when: datetime | None = None) -> str:
    """Next sequential code for the UTC calendar day — not random, easy to track."""
    when = when or datetime.now(timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    day_key = when.strftime("%Y%m%d")
    prefix = f"PR-{day_key}-"
    count = db.execute(
        select(func.count())
        .select_from(PaymentRequest)
        .where(PaymentRequest.reference_code.like(f"{prefix}%"))
    ).scalar_one()
    return f"{prefix}{int(count) + 1:04d}"
