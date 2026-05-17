import enum
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PaymentRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class RecipientContactType(str, enum.Enum):
    EMAIL = "EMAIL"
    PHONE = "PHONE"


class RequestEventType(str, enum.Enum):
    REQUEST_CREATED = "REQUEST_CREATED"
    REQUEST_PAID = "REQUEST_PAID"
    REQUEST_DECLINED = "REQUEST_DECLINED"
    REQUEST_CANCELLED = "REQUEST_CANCELLED"
    REQUEST_EXPIRED = "REQUEST_EXPIRED"


class WalletTransactionDirection(str, enum.Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    email_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    phone_hash: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    wallets: Mapped[list["Wallet"]] = relationship(back_populates="user")
    destinations: Mapped[list["PaymentDestination"]] = relationship(back_populates="user")


class Wallet(Base):
    __tablename__ = "wallets"
    __table_args__ = (
        CheckConstraint("balance_minor >= 0", name="ck_wallet_balance_nonneg"),
        CheckConstraint("available_balance_minor >= 0", name="ck_wallet_avail_nonneg"),
        Index("ix_wallets_user_id", "user_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="TRY")
    wallet_type: Mapped[str] = mapped_column(String(32), nullable=False, default="INTERNAL")
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    balance_minor: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available_balance_minor: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    user: Mapped["User"] = relationship(back_populates="wallets")


class PaymentDestination(Base):
    __tablename__ = "payment_destinations"
    __table_args__ = (Index("ix_payment_destinations_user_id", "user_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    wallet_id: Mapped[str | None] = mapped_column(ForeignKey("wallets.id"), nullable=True)
    destination_type: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="TRY")
    display_label: Mapped[str] = mapped_column(String(255), nullable=False)
    masked_identifier: Mapped[str | None] = mapped_column(String(64), nullable=True)
    identifier_hash: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    encrypted_identifier: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    provider_account_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    user: Mapped["User"] = relationship(back_populates="destinations")
    wallet: Mapped["Wallet | None"] = relationship()


class PaymentRequest(Base):
    __tablename__ = "payment_requests"
    __table_args__ = (
        CheckConstraint("amount_minor > 0", name="ck_request_amount_positive"),
        Index("ix_payment_requests_sender_user_id", "sender_user_id"),
        Index("ix_payment_requests_recipient_user_id", "recipient_user_id"),
        Index("ix_payment_requests_recipient_contact_hash", "recipient_contact_hash"),
        Index("ix_payment_requests_status", "status"),
        Index("ix_payment_requests_expires_at", "expires_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    share_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    sender_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    recipient_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    recipient_contact: Mapped[str] = mapped_column(String(320), nullable=False)
    recipient_contact_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    recipient_contact_type: Mapped[str] = mapped_column(String(16), nullable=False)
    destination_id: Mapped[str] = mapped_column(ForeignKey("payment_destinations.id"), nullable=False)
    destination_snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)
    amount_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="TRY")
    note: Mapped[str | None] = mapped_column(String(280), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default=PaymentRequestStatus.PENDING.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    declined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    events: Mapped[list["RequestEvent"]] = relationship(back_populates="payment_request")


class RequestEvent(Base):
    __tablename__ = "request_events"
    __table_args__ = (Index("ix_request_events_payment_request_id", "payment_request_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    payment_request_id: Mapped[str] = mapped_column(ForeignKey("payment_requests.id"), nullable=False)
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    previous_status: Mapped[str | None] = mapped_column(String(16), nullable=True)
    new_status: Mapped[str | None] = mapped_column(String(16), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    payment_request: Mapped["PaymentRequest"] = relationship(back_populates="events")


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"
    __table_args__ = (
        CheckConstraint("amount_minor > 0", name="ck_wtx_amount_positive"),
        Index("ix_wallet_transactions_wallet_id", "wallet_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    wallet_id: Mapped[str] = mapped_column(ForeignKey("wallets.id"), nullable=False)
    payment_request_id: Mapped[str | None] = mapped_column(
        ForeignKey("payment_requests.id"), nullable=True
    )
    direction: Mapped[str] = mapped_column(String(8), nullable=False)
    amount_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="POSTED")
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
