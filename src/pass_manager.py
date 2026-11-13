import calendar
from datetime import datetime, time
from decimal import Decimal

from src.config import (
    TOLL_RATES, MONTHLY_LOCAL_PRICE, TRIP_50_COUNT,
    TRIP_50_PRICE_MULTIPLIER
)
from src.models import TollPass, PassResult


def month_end(purchase_time):
    last_day = calendar.monthrange(purchase_time.year, purchase_time.month)[1]
    return datetime.combine(purchase_time.date().replace(day=last_day), time(23, 59, 59))


def pass_price(tag, pass_type):
    pass_type = pass_type.upper()
    if pass_type == "MONTHLY_LOCAL":
        if tag.registered_class != "CAR" or not tag.is_local_resident:
            return None
        return MONTHLY_LOCAL_PRICE
    if pass_type == "TRIP_50":
        return (TOLL_RATES[tag.registered_class] * TRIP_50_PRICE_MULTIPLIER).quantize(Decimal("0.01"))
    return None


def purchase_pass(tag, pass_type, purchase_time):
    pass_type = pass_type.upper()
    price = pass_price(tag, pass_type)
    if price is None:
        return PassResult(purchase_time, tag.tag_id, pass_type, "REJECTED",
                          Decimal("0.00"), None, None)
    valid_to = month_end(purchase_time)
    tag.active_pass = TollPass(
        tag_id=tag.tag_id,
        pass_type=pass_type,
        price=price,
        valid_from=purchase_time,
        valid_to=valid_to,
        remaining_trips=TRIP_50_COUNT if pass_type == "TRIP_50" else None,
    )
    tag.total_cash_paid += price
    return PassResult(purchase_time, tag.tag_id, pass_type, "OK",
                      price, purchase_time.date(), valid_to.date())


def consume_pass_trip(tag, crossing_time):
    active = tag.active_pass
    if active is None or not active.is_valid(crossing_time):
        return False
    if active.pass_type == "MONTHLY_LOCAL":
        return True
    if active.pass_type == "TRIP_50" and active.remaining_trips > 0:
        active.remaining_trips -= 1
        return True
    return False
