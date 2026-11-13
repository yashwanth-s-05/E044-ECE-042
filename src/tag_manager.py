from decimal import Decimal
from src.config import MINIMUM_RECHARGE, TOLL_RATES, LOW_BALANCE_MULTIPLIER


def apply_recharge(tag, amount):
    amount = Decimal(amount).quantize(Decimal("0.01"))
    if amount < MINIMUM_RECHARGE:
        return "REJECTED_MINIMUM"
    tag.balance += amount
    tag.total_recharges += amount
    if tag.blacklisted and tag.balance > Decimal("0.00"):
        tag.blacklisted = False
    return "OK"


def apply_account_charge(tag, fare, penalty):
    fare = Decimal(fare)
    penalty = Decimal(penalty)
    tag.balance -= fare + penalty
    tag.total_fare += fare
    tag.total_penalties += penalty
    if tag.balance < Decimal("0.00"):
        tag.blacklisted = True
    return tag.balance


def low_balance(tag):
    threshold = TOLL_RATES[tag.registered_class] * LOW_BALANCE_MULTIPLIER
    return tag.balance < threshold


def tag_status(tag):
    if tag.blacklisted:
        return "BLACKLISTED"
    if tag.reverify_required:
        return "REVERIFY"
    if tag.active_pass is not None:
        return "ACTIVE_PASS"
    return "ACTIVE"
