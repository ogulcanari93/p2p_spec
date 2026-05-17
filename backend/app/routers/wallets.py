from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import PaymentDestinationOut, WalletOut
from app.services.payment_destinations import ensure_default_destination, get_user_destinations
from app.services.wallets import ensure_default_wallet, get_default_wallet

router = APIRouter(prefix="/api", tags=["wallets"])


@router.get("/wallets/me", response_model=WalletOut)
def get_my_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WalletOut:
    wallet = get_default_wallet(db, current_user)
    if not wallet:
        wallet = ensure_default_wallet(db, current_user)
        db.commit()
        db.refresh(wallet)
    return WalletOut.model_validate(wallet)


@router.get("/payment-destinations/me", response_model=list[PaymentDestinationOut])
def list_my_destinations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PaymentDestinationOut]:
    destinations = get_user_destinations(db, current_user)
    if not destinations:
        default = ensure_default_destination(db, current_user)
        db.commit()
        destinations = [default]

    default_dest = destinations[0] if destinations else None
    result: list[PaymentDestinationOut] = []
    for d in destinations:
        out = PaymentDestinationOut.model_validate(d).model_copy(
            update={"is_default": default_dest is not None and d.id == default_dest.id}
        )
        result.append(out)
    return result
