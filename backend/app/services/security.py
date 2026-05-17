import hashlib
import hmac
import json
import re
from typing import Any

from app.models import PaymentDestination, RecipientContactType

DEFAULT_PASSWORD = "1234"
_PASSWORD_SALT = "p2p-payment-request-prototype-v1"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[0-9][0-9\s\-()]{6,20}$")


def hash_value(value: str) -> str:
    normalized = value.strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    payload = f"{_PASSWORD_SALT}:{password}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), password_hash)


def detect_contact_type(contact: str) -> RecipientContactType:
    stripped = contact.strip()
    if EMAIL_RE.match(stripped):
        return RecipientContactType.EMAIL
    if PHONE_RE.match(stripped):
        return RecipientContactType.PHONE
    raise ValueError("Recipient contact must be a valid email or phone number.")


def normalize_contact(contact: str, contact_type: RecipientContactType) -> str:
    stripped = contact.strip()
    if contact_type == RecipientContactType.EMAIL:
        return stripped.lower()
    return re.sub(r"[\s\-()]", "", stripped)


def contact_hash(contact: str, contact_type: RecipientContactType) -> str:
    return hash_value(normalize_contact(contact, contact_type))


def build_destination_snapshot(destination: PaymentDestination) -> dict[str, Any]:
    return {
        "destination_type": destination.destination_type,
        "display_label": destination.display_label,
        "masked_identifier": destination.masked_identifier,
        "currency": destination.currency,
    }


def snapshot_to_json(snapshot: dict[str, Any]) -> str:
    return json.dumps(snapshot, separators=(",", ":"), sort_keys=True)
