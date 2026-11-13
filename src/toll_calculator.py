from datetime import timedelta
from decimal import Decimal

from src.config import TOLL_RATES, CLASS_ORDER, RETURN_WINDOW_HOURS


def effective_vehicle_class(registered_class, detected_class):
    registered_class = registered_class.upper()
    detected_class = detected_class.upper()
    if registered_class not in TOLL_RATES:
        raise ValueError(f"Unknown registered class: {registered_class}")
    if detected_class not in TOLL_RATES:
        raise ValueError(f"Unknown detected class: {detected_class}")
    if CLASS_ORDER[detected_class] > CLASS_ORDER[registered_class]:
        return detected_class, True
    return registered_class, False


def calculate_toll(tag, detected_class, crossing_time):
    if tag.is_exempt:
        return Decimal("0.00"), False, tag.registered_class
    effective_class, mismatch = effective_vehicle_class(
        tag.registered_class, detected_class
    )
    rate = TOLL_RATES[effective_class]
    window_start = crossing_time - timedelta(hours=RETURN_WINDOW_HOURS)
    previous = [
        item for item in tag.paid_crossings
        if window_start <= item < crossing_time
    ]
    fare = rate * Decimal("0.50") if len(previous) == 1 else rate
    return fare.quantize(Decimal("0.01")), mismatch, effective_class


def record_paid_crossing(tag, crossing_time):
    window_start = crossing_time - timedelta(hours=RETURN_WINDOW_HOURS)
    tag.paid_crossings = [
        item for item in tag.paid_crossings
        if window_start <= item < crossing_time
    ]
    tag.paid_crossings.append(crossing_time)
