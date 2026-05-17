import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User, Wallet


def ensure_default_wallet(db: Session, user: User, currency: str = "TRY") -> Wallet:
    stmt = select(Wallet).where(
        Wallet.user_id == user.id,
        Wallet.currency == currency,
        Wallet.wallet_type == "INTERNAL",
    )
    wallet = db.execute(stmt).scalar_one_or_none()
    if wallet:
        return wallet

    wallet = Wallet(
        id=str(uuid.uuid4()),
        user_id=user.id,
        currency=currency,
        wallet_type="INTERNAL",
        display_name=f"{currency} Wallet",
        balance_minor=0,
        available_balance_minor=0,
        status="ACTIVE",
    )
    db.add(wallet)
    db.flush()
    return wallet


def get_default_wallet(db: Session, user: User, currency: str = "TRY") -> Wallet | None:
    stmt = select(Wallet).where(
        Wallet.user_id == user.id,
        Wallet.currency == currency,
        Wallet.status == "ACTIVE",
    )
    return db.execute(stmt).scalars().first()
