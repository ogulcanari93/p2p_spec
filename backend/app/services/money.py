from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from fastapi import HTTPException


class MoneyValidationError(ValueError):
    pass


def normalize_currency(currency: str) -> str:
    code = currency.strip().upper()
    if len(code) != 3 or not code.isalpha():
        raise MoneyValidationError("Currency must be a 3-letter code.")
    return code


def parse_amount_to_minor(amount: str, currency: str = "TRY") -> int:
    code = normalize_currency(currency)
    raw = amount.strip()
    if not raw:
        raise MoneyValidationError("Amount is required.")

    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise MoneyValidationError("Amount must be a valid number.") from exc

    if value <= 0:
        raise MoneyValidationError("Amount must be greater than zero.")

    if code == "TRY":
        exponent = value.as_tuple().exponent
        if isinstance(exponent, int) and exponent < -2:
            raise MoneyValidationError("TRY amounts allow at most two decimal places.")

    minor = int((value * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    if minor <= 0:
        raise MoneyValidationError("Amount must be greater than zero.")
    return minor


def minor_to_decimal_string(amount_minor: int, currency: str = "TRY") -> str:
    if currency == "TRY":
        return f"{Decimal(amount_minor) / 100:.2f}"
    return str(amount_minor)


def money_validation_http_error(exc: MoneyValidationError) -> HTTPException:
    return HTTPException(status_code=422, detail=str(exc))
