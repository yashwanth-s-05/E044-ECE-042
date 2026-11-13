from decimal import Decimal
from src.data_loader import parse_decimal, parse_bool, parse_timestamp


def test_parse_decimal():
    assert parse_decimal("100", "amount") == Decimal("100.00")


def test_parse_boolean():
    assert parse_bool("True", "flag") is True
    assert parse_bool("0", "flag") is False


def test_parse_timestamp():
    assert parse_timestamp("2026-10-01 05:00:51").year == 2026
