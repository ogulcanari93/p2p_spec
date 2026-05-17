import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PaymentDestination, User, Wallet
from app.services.wallets import ensure_default_wallet


def ensure_default_destination(db: Session, user: User, currency: str = "TRY") -> PaymentDestination:
    wallet = ensure_default_wallet(db, user, currency=currency)
    stmt = select(PaymentDestination).where(
        PaymentDestination.user_id == user.id,
        PaymentDestination.currency == currency,
        PaymentDestination.destination_type == "INTERNAL_WALLET",
        PaymentDestination.status == "ACTIVE",
    )
    destination = db.execute(stmt).scalar_one_or_none()
    if destination:
        return destination

    masked = f"Wallet ••••{wallet.id[-4:]}"
    destination = PaymentDestination(
        id=str(uuid.uuid4()),
        user_id=user.id,
        wallet_id=wallet.id,
        destination_type="INTERNAL_WALLET",
        currency=currency,
        display_label=f"{currency} Wallet",
        masked_identifier=masked,
        identifier_hash=None,
        status="ACTIVE",
    )
    db.add(destination)
    db.flush()
    return destination


def get_user_destinations(db: Session, user: User, currency: str | None = None) -> list[PaymentDestination]:
    stmt = select(PaymentDestination).where(
        PaymentDestination.user_id == user.id,
        PaymentDestination.status == "ACTIVE",
    )
    if currency:
        stmt = stmt.where(PaymentDestination.currency == currency.upper())
    return list(db.execute(stmt).scalars().all())


def get_destination_for_user(
    db: Session, user: User, destination_id: str
) -> PaymentDestination | None:
    stmt = select(PaymentDestination).where(
        PaymentDestination.id == destination_id,
        PaymentDestination.user_id == user.id,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_default_destination(db: Session, user: User, currency: str) -> PaymentDestination | None:
    destinations = get_user_destinations(db, user, currency=currency)
    internal = [d for d in destinations if d.destination_type == "INTERNAL_WALLET"]
    return internal[0] if internal else (destinations[0] if destinations else None)
