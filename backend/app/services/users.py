import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.services.payment_destinations import ensure_default_destination
from app.services.security import DEFAULT_PASSWORD, hash_password, hash_value
from app.services.wallets import ensure_default_wallet


def ensure_user(
    db: Session,
    *,
    email: str,
    display_name: str | None = None,
    phone: str | None = None,
    password: str = DEFAULT_PASSWORD,
    user_id: str | None = None,
) -> User:
    normalized = email.strip().lower()
    email_hash = hash_value(normalized)

    user = db.execute(select(User).where(User.email_hash == email_hash)).scalar_one_or_none()
    if user:
        user.password_hash = hash_password(password)
        if display_name is not None:
            user.display_name = display_name
        if phone is not None:
            user.phone = phone
            user.phone_hash = hash_value(phone) if phone else None
        return user

    phone_hash = hash_value(phone) if phone else None
    user = User(
        id=user_id or str(uuid.uuid4()),
        email=normalized,
        email_hash=email_hash,
        password_hash=hash_password(password),
        display_name=display_name,
        phone=phone,
        phone_hash=phone_hash,
    )
    db.add(user)
    db.flush()
    ensure_default_wallet(db, user)
    ensure_default_destination(db, user)
    return user
