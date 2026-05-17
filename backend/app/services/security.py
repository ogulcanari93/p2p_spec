import hashlib
import json
import re
from typing import Any

from app.models import PaymentDestination, RecipientContactType

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[0-9][0-9\s\-()]{6,20}$")


def hash_value(value: str) -> str:
    normalized = value.strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


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
