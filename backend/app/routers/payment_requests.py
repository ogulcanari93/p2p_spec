from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import CreatePaymentRequestIn, CreatePaymentRequestResponse, PaymentRequestListOut
from app.serializers import request_to_detail, request_to_summary
from app.services.payment_requests import create_payment_request, list_outgoing_requests, share_url

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


@router.get("", response_model=PaymentRequestListOut)
def list_requests(
    direction: str = Query(default="all"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaymentRequestListOut:
    outgoing: list = []
    if direction in ("outgoing", "all"):
        rows = list_outgoing_requests(db, current_user)
        outgoing = [request_to_summary(r, viewer=current_user) for r in rows]
    return PaymentRequestListOut(outgoing=outgoing, incoming=[])
