from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import PublicShareViewOut
from app.services.payment_requests import get_public_share_view

router = APIRouter(prefix="/api/share", tags=["share"])


@router.get("/{share_token}", response_model=PublicShareViewOut)
def get_share_view(
    share_token: str,
    db: Session = Depends(get_db),
) -> PublicShareViewOut:
    return get_public_share_view(db, share_token)
