from datetime import datetime, timedelta
from decimal import Decimal
from src.models import Tag
from src.toll_calculator import calculate_toll, record_paid_crossing


def make_tag():
    return Tag("T1", "KA01", "Test", "CAR", Decimal("500"),
               Decimal("500"), False, False)


def test_first_second_and_third_paid_crossing():
    tag = make_tag()
    first = datetime(2026, 10, 1, 10)
    fare, _, _ = calculate_toll(tag, "CAR", first)
    assert fare == Decimal("65.00")
    record_paid_crossing(tag, first)

    second = first + timedelta(hours=2)
    fare, _, _ = calculate_toll(tag, "CAR", second)
    assert fare == Decimal("32.50")
    record_paid_crossing(tag, second)

    third = first + timedelta(hours=3)
    fare, _, _ = calculate_toll(tag, "CAR", third)
    assert fare == Decimal("65.00")


def test_exact_24_hour_boundary_is_included():
    tag = make_tag()
    first = datetime(2026, 10, 1, 10)
    record_paid_crossing(tag, first)
    fare, _, _ = calculate_toll(tag, "CAR", first + timedelta(hours=24))
    assert fare == Decimal("32.50")


def test_higher_detected_class():
    tag = make_tag()
    fare, mismatch, effective = calculate_toll(
        tag, "LCV", datetime(2026, 10, 1, 10)
    )
    assert fare == Decimal("105.00")
    assert mismatch is True
    assert effective == "LCV"


def test_lower_detected_class_is_ignored():
    tag = make_tag()
    tag.registered_class = "LCV"
    fare, mismatch, effective = calculate_toll(
        tag, "CAR", datetime(2026, 10, 1, 10)
    )
    assert fare == Decimal("105.00")
    assert mismatch is False
    assert effective == "LCV"
