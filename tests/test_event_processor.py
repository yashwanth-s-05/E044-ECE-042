from datetime import datetime, timedelta
from decimal import Decimal
from src.models import Tag, TollEvent
from src.event_processor import EventProcessor


def make_tag(balance="1000"):
    return Tag("T1", "KA01", "Test", "CAR", Decimal(balance),
               Decimal(balance), False, False)


def test_duplicate_read_inside_120_seconds_is_ignored():
    tag = make_tag()
    start = datetime(2026, 10, 1, 10)
    events = [
        TollEvent(start, "READ", "T1", "L1", "CAR"),
        TollEvent(start + timedelta(seconds=45), "READ", "T1", "L1", "CAR"),
    ]
    processor = EventProcessor({"T1": tag}).process_events(events)
    assert [r.outcome for r in processor.read_results] == [
        "SINGLE", "DUPLICATE_IGNORED"
    ]


def test_exactly_120_seconds_is_not_duplicate():
    tag = make_tag()
    start = datetime(2026, 10, 1, 10)
    events = [
        TollEvent(start, "READ", "T1", "L1", "CAR"),
        TollEvent(start + timedelta(seconds=120), "READ", "T1", "L1", "CAR"),
    ]
    processor = EventProcessor({"T1": tag}).process_events(events)
    assert all(r.outcome != "DUPLICATE_IGNORED" for r in processor.read_results)


def test_equal_timestamp_event_priority_pass_before_read():
    tag = make_tag()
    when = datetime(2026, 10, 1, 10)
    tag.is_local_resident = True
    events = [
        TollEvent(when, "READ", "T1", "L1", "CAR"),
        TollEvent(when, "PASS", "T1", pass_type="MONTHLY_LOCAL"),
    ]
    processor = EventProcessor({"T1": tag}).process_events(events)
    assert processor.read_results[0].outcome == "PASS"


def test_negative_balance_blacklists_tag():
    tag = make_tag("10")
    when = datetime(2026, 10, 1, 10)
    processor = EventProcessor({"T1": tag}).process_events([
        TollEvent(when, "READ", "T1", "L1", "CAR")
    ])
    assert tag.blacklisted is True
    assert processor.read_results[0].balance_after == Decimal("-55.00")


from datetime import datetime
from decimal import Decimal
from src.models import Tag, TollEvent
from src.event_processor import EventProcessor


def build_tag(tag_id, vehicle_class="CAR", balance="1000", local=False):
    return Tag(tag_id, "KA01", "Test", vehicle_class, Decimal(balance),
               Decimal(balance), local, False)


def test_pass_mismatch_penalty_is_charged_and_logged():
    tag = build_tag("T1", "CAR", "1000", True)
    when = datetime(2026, 10, 1, 10)
    events = [
        TollEvent(when, "PASS", "T1", pass_type="MONTHLY_LOCAL"),
        TollEvent(when, "READ", "T1", "L1", "LCV"),
    ]
    processor = EventProcessor({"T1": tag}).process_events(events)
    result = processor.read_results[0]
    assert result.outcome == "PASS"
    assert result.fare == Decimal("0.00")
    assert result.penalty == Decimal("100.00")
    assert tag.balance == Decimal("900.00")
    assert tag.total_penalties == Decimal("100.00")


def test_blacklist_recharge_to_exact_zero_stays_blacklisted():
    from src.tag_manager import apply_recharge
    tag = build_tag("T1", balance="-100")
    tag.blacklisted = True
    assert apply_recharge(tag, Decimal("100")) == "OK"
    assert tag.balance == Decimal("0.00")
    assert tag.blacklisted is True


def test_exempt_tag_is_logged_without_charge():
    tag = build_tag("T1")
    tag.is_exempt = True
    when = datetime(2026, 10, 1, 10)
    processor = EventProcessor({"T1": tag}).process_events([
        TollEvent(when, "READ", "T1", "L1", "MAV")
    ])
    assert processor.read_results[0].outcome == "EXEMPT"
    assert processor.read_results[0].fare == Decimal("0.00")
