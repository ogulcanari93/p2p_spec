from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models import PaymentRequestStatus, RecipientContactType


class UserOut(BaseModel):
    id: str
    email: EmailStr
    display_name: str | None = None
    phone: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class LoginResponse(BaseModel):
    user: UserOut


class WalletOut(BaseModel):
    id: str
    currency: str
    wallet_type: str = "INTERNAL"
    display_name: str | None = None
    balance_minor: int
    available_balance_minor: int
    status: str

    model_config = {"from_attributes": True}


class PaymentDestinationOut(BaseModel):
    id: str
    destination_type: str
    currency: str
    display_label: str
    masked_identifier: str | None = None
    status: str
    is_default: bool = False

    model_config = {"from_attributes": True}


class DestinationSnapshotOut(BaseModel):
    destination_type: str
    display_label: str
    masked_identifier: str | None = None
    currency: str


class CreatePaymentRequestIn(BaseModel):
    recipient_contact: str = Field(min_length=3, max_length=320)
    amount: str
    currency: str = "TRY"
    note: str | None = Field(default=None, max_length=280)
    destination_id: str | None = None

    @field_validator("note")
    @classmethod
    def validate_note(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 280:
            raise ValueError("Note must be at most 280 characters.")
        return v


class PaymentRequestSummaryOut(BaseModel):
    id: str
    reference_code: str
    share_token: str
    status: str
    amount_minor: int
    currency: str
    note: str | None = None
    recipient_contact: str
    recipient_contact_type: RecipientContactType
    counterparty_label: str
    destination_snapshot: DestinationSnapshotOut
    created_at: datetime
    expires_at: datetime
    is_expired: bool = False
    can_pay: bool = False
    can_decline: bool = False
    can_cancel: bool = False


class SenderOut(BaseModel):
    id: str
    email: EmailStr
    display_name: str | None = None

    model_config = {"from_attributes": True}


class RequestEventOut(BaseModel):
    id: str
    event_type: str
    previous_status: str | None = None
    new_status: str | None = None
    created_at: datetime
    actor_user_id: str | None = None

    model_config = {"from_attributes": True}


class PaymentRequestDetailOut(PaymentRequestSummaryOut):
    sender: SenderOut | None = None
    recipient_user_id: str | None = None
    paid_at: datetime | None = None
    declined_at: datetime | None = None
    cancelled_at: datetime | None = None
    expired_at: datetime | None = None
    share_url: str | None = None
    events: list[RequestEventOut] = []


class CreatePaymentRequestResponse(BaseModel):
    request: PaymentRequestDetailOut
    share_url: str


class PaymentRequestListOut(BaseModel):
    outgoing: list[PaymentRequestSummaryOut] = []
    incoming: list[PaymentRequestSummaryOut] = []


class PublicShareViewOut(BaseModel):
    reference_code: str
    status: str
    amount_minor: int
    currency: str
    note: str | None = None
    sender_display: str
    recipient_contact_masked: str
    created_at: datetime
    expires_at: datetime
    share_token: str
