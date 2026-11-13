from datetime import datetime
from decimal import Decimal
from src.models import Tag
from src.pass_manager import purchase_pass, consume_pass_trip


def tag(vehicle_class="CAR", local=True):
    return Tag("T1", "KA01", "Test", vehicle_class, Decimal("1000"),
               Decimal("1000"), local, False)


def test_local_car_monthly_pass():
    t = tag()
    result = purchase_pass(t, "MONTHLY_LOCAL", datetime(2026, 10, 15, 10))
    assert result.status == "OK"
    assert result.price == Decimal("330.00")
    assert result.valid_to.isoformat() == "2026-10-31"


def test_non_local_car_monthly_pass_rejected():
    result = purchase_pass(tag(local=False), "MONTHLY_LOCAL", datetime(2026, 10, 1))
    assert result.status == "REJECTED"


def test_trip_50_price_and_usage():
    t = tag("BUS_TRUCK", False)
    when = datetime(2026, 10, 1, 10)
    result = purchase_pass(t, "TRIP_50", when)
    assert result.price == Decimal("6600.00")
    assert consume_pass_trip(t, when) is True
    assert t.active_pass.remaining_trips == 49
