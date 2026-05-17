from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.security import hash_value


def get_current_user(
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
    db: Session = Depends(get_db),
) -> User:
    if not x_user_email or not x_user_email.strip():
        raise HTTPException(status_code=401, detail="Authentication required. Provide X-User-Email header.")

    email = x_user_email.strip().lower()
    email_h = hash_value(email)
    user = db.execute(select(User).where(User.email_hash == email_h)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Unknown user. Please log in first.")
    return user
