from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, LoginResponse, UserOut
from app.services.payment_destinations import ensure_default_destination
from app.services.security import hash_value, verify_password
from app.services.wallets import ensure_default_wallet

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    email = str(body.email).strip().lower()
    email_h = hash_value(email)
    user = db.execute(select(User).where(User.email_hash == email_h)).scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    ensure_default_wallet(db, user)
    ensure_default_destination(db, user)
    db.commit()
    db.refresh(user)
    return LoginResponse(user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)
