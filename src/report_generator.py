import csv
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from src.config import (
    OUTPUT_DIR, READ_LOG, RECHARGE_LOG, PASS_LOG,
    DAILY_COLLECTION, STATEMENTS
)


def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"))


def write_csv(path, columns, rows):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def generate_read_log(processor):
    columns = ["timestamp", "tag_id", "lane", "registered_class", "detected_class",
               "outcome", "fare", "penalty", "balance_after", "flags"]
    rows = []
    for r in processor.read_results:
        rows.append({
            "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "tag_id": r.tag_id, "lane": r.lane,
            "registered_class": r.registered_class,
            "detected_class": r.detected_class, "outcome": r.outcome,
            "fare": money(r.fare), "penalty": money(r.penalty),
            "balance_after": money(r.balance_after),
            "flags": ";".join(filter(None, r.flags.split(","))),
        })
    write_csv(READ_LOG, columns, rows)


def generate_recharge_log(processor):
    columns = ["timestamp", "tag_id", "amount", "status", "balance_after"]
    rows = [{
        "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "tag_id": r.tag_id, "amount": money(r.amount),
        "status": r.status, "balance_after": money(r.balance_after),
    } for r in processor.recharge_results]
    write_csv(RECHARGE_LOG, columns, rows)


def generate_pass_log(processor):
    columns = ["timestamp", "tag_id", "pass_type", "status", "price",
               "valid_from", "valid_to"]
    rows = [{
        "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "tag_id": r.tag_id, "pass_type": r.pass_type,
        "status": "SOLD" if r.status == "OK" else "REJECTED",
        "price": money(r.price),
        "valid_from": r.valid_from.isoformat() if r.valid_from else "",
        "valid_to": r.valid_to.isoformat() if r.valid_to else "",
    } for r in processor.pass_results]
    write_csv(PASS_LOG, columns, rows)


def generate_daily_collection(processor, start_date, end_date):
    columns = ["date", "reads", "duplicates_ignored", "exempt_crossings",
               "pass_crossings", "paid_crossings", "tag_collection",
               "cash_collection", "penalties", "total_collection"]
    daily = defaultdict(lambda: {
        "reads": 0, "duplicates_ignored": 0, "exempt_crossings": 0,
        "pass_crossings": 0, "paid_crossings": 0,
        "tag_collection": Decimal("0.00"),
        "cash_collection": Decimal("0.00"),
        "penalties": Decimal("0.00"),
    })
    for r in processor.read_results:
        day = r.timestamp.date().isoformat()
        d = daily[day]
        d["reads"] += 1
        if r.outcome == "DUPLICATE_IGNORED":
            d["duplicates_ignored"] += 1
        elif r.outcome == "EXEMPT":
            d["exempt_crossings"] += 1
        elif r.outcome == "PASS":
            d["pass_crossings"] += 1
        elif r.outcome in {"SINGLE", "RETURN", "CASH_BLACKLISTED"}:
            d["paid_crossings"] += 1
        d["tag_collection"] += money(r.fare)
        d["penalties"] += money(r.penalty)

    for day, amount in processor.cash_collection_entries:
        daily[day]["cash_collection"] += money(amount)
    for r in processor.pass_results:
        if r.status == "OK":
            daily[r.timestamp.date().isoformat()]["cash_collection"] += money(r.price)

    rows = []
    current = start_date
    while current <= end_date:
        day = current.isoformat()
        d = daily[day]
        total = d["tag_collection"] + d["cash_collection"] + d["penalties"]
        rows.append({
            "date": day, "reads": d["reads"],
            "duplicates_ignored": d["duplicates_ignored"],
            "exempt_crossings": d["exempt_crossings"],
            "pass_crossings": d["pass_crossings"],
            "paid_crossings": d["paid_crossings"],
            "tag_collection": money(d["tag_collection"]),
            "cash_collection": money(d["cash_collection"]),
            "penalties": money(d["penalties"]),
            "total_collection": money(total),
        })
        current += timedelta(days=1)
    write_csv(DAILY_COLLECTION, columns, rows)


def generate_statements(processor, tags, month):
    columns = ["month", "tag_id", "registered_class", "opening_balance",
               "crossings", "fare_charged", "penalties", "cash_paid",
               "recharges", "closing_balance", "status"]
    # The specification requires one statement row for every registered tag.
    rows = []
    for tag_id in sorted(tags):
        tag = tags[tag_id]
        if tag.blacklisted:
            status = "BLACKLISTED"
        elif tag.reverify_required:
            status = "REVERIFY"
        elif tag.active_pass is not None:
            status = "ACTIVE_PASS"
        else:
            status = "ACTIVE"
        rows.append({
            "month": month, "tag_id": tag_id,
            "registered_class": tag.registered_class,
            "opening_balance": money(tag.opening_balance),
            "crossings": tag.total_crossings,
            "fare_charged": money(tag.total_fare),
            "penalties": money(tag.total_penalties),
            "cash_paid": money(tag.total_cash_paid),
            "recharges": money(tag.total_recharges),
            "closing_balance": money(tag.balance),
            "status": status,
        })
    write_csv(STATEMENTS, columns, rows)


def generate_all_reports(processor, tags, start_date, end_date, month):
    generate_read_log(processor)
    generate_recharge_log(processor)
    generate_pass_log(processor)
    generate_daily_collection(processor, start_date, end_date)
    generate_statements(processor, tags, month)
