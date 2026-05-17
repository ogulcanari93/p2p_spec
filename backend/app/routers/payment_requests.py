from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import CreatePaymentRequestIn, CreatePaymentRequestResponse, PaymentRequestListOut
from app.serializers import request_to_detail, request_to_summary
from app.services.expiration import expire_pending_for_user
from app.services.payment_requests import create_payment_request, list_payment_requests, share_url

router = APIRouter(prefix="/api/requests", tags=["payment-requests"])


@router.post("", response_model=CreatePaymentRequestResponse, status_code=201)
def post_request(
    body: CreatePaymentRequestIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CreatePaymentRequestResponse:
    request = create_payment_request(
        db,
        current_user,
        recipient_contact=body.recipient_contact,
        amount=body.amount,
        currency=body.currency,
        note=body.note,
        destination_id=body.destination_id,
    )
    detail = request_to_detail(db, request, viewer=current_user, sender=current_user)
    return CreatePaymentRequestResponse(request=detail, share_url=share_url(request.share_token))


def _summaries_for_requests(db: Session, rows: list, viewer: User) -> list:
    sender_ids = {r.sender_user_id for r in rows}
    senders = {}
    if sender_ids:
        from sqlalchemy import select as sa_select

        from app.models import User as UserModel

        for user in db.execute(sa_select(UserModel).where(UserModel.id.in_(sender_ids))).scalars():
            senders[user.id] = user.email

    return [
        request_to_summary(r, viewer=viewer, sender_email=senders.get(r.sender_user_id))
        for r in rows
    ]


@router.get("", response_model=PaymentRequestListOut)
def list_requests(
    direction: str = Query(default="all"),
    status: str = Query(default="all"),
    search: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaymentRequestListOut:
    expire_pending_for_user(db, current_user)
    outgoing_rows, incoming_rows = list_payment_requests(
        db,
        current_user,
        direction=direction,
        status=status,
        search=search,
    )
    return PaymentRequestListOut(
        outgoing=_summaries_for_requests(db, outgoing_rows, current_user),
        incoming=_summaries_for_requests(db, incoming_rows, current_user),
    )
