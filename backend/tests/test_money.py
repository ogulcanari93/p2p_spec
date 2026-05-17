import pytest

from app.services.money import MoneyValidationError, parse_amount_to_minor


def test_parse_valid_try_amount():
    assert parse_amount_to_minor("100.00", "TRY") == 10000
    assert parse_amount_to_minor("0.01", "TRY") == 1


def test_reject_zero():
    with pytest.raises(MoneyValidationError):
        parse_amount_to_minor("0", "TRY")


def test_reject_negative():
    with pytest.raises(MoneyValidationError):
        parse_amount_to_minor("-5.00", "TRY")


def test_reject_too_many_decimals_try():
    with pytest.raises(MoneyValidationError):
        parse_amount_to_minor("1.234", "TRY")


def test_reject_non_numeric():
    with pytest.raises(MoneyValidationError):
        parse_amount_to_minor("abc", "TRY")
