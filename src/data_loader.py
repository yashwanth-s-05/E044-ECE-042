import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation

from src.config import DATA_DIR, TOLL_RATES
from src.models import Tag, TollEvent

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def parse_timestamp(value):
    try:
        return datetime.strptime(value.strip(), TIMESTAMP_FORMAT)
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid timestamp: {value!r}")


def parse_decimal(value, field_name):
    try:
        number = Decimal(str(value).strip())
        if not number.is_finite():
            raise ValueError
        return number.quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError, AttributeError):
        raise ValueError(f"Invalid {field_name}: {value!r}")


def parse_bool(value, field_name):
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"Invalid {field_name}: {value!r}")


def read_rows(path, required_columns):
    if not path.exists():
        raise FileNotFoundError(f"Required input file not found: {path}")
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{path.name} is empty")
        missing = set(required_columns) - set(reader.fieldnames)
        if missing:
            raise ValueError(f"{path.name} missing columns: {sorted(missing)}")
        return list(reader)


def load_tags(path=None):
    path = path or DATA_DIR / "tags.csv"
    columns = [
        "tag_id", "vehicle_number", "owner_name", "registered_class",
        "opening_balance", "local_resident", "exempt"
    ]
    tags = {}
    for line, row in enumerate(read_rows(path, columns), start=2):
        tag_id = row["tag_id"].strip()
        vehicle_class = row["registered_class"].strip().upper()
        if not tag_id:
            raise ValueError(f"Empty tag_id at {path.name}:{line}")
        if tag_id in tags:
            raise ValueError(f"Duplicate tag_id: {tag_id}")
        if vehicle_class not in TOLL_RATES:
            raise ValueError(f"Invalid registered_class for {tag_id}: {vehicle_class}")
        balance = parse_decimal(row["opening_balance"], "opening_balance")
        if balance < 0:
            raise ValueError(f"Negative opening balance for {tag_id}")
        tags[tag_id] = Tag(
            tag_id=tag_id,
            vehicle_number=row["vehicle_number"].strip(),
            owner_name=row["owner_name"].strip(),
            registered_class=vehicle_class,
            opening_balance=balance,
            balance=balance,
            is_local_resident=parse_bool(row["local_resident"], "local_resident"),
            is_exempt=parse_bool(row["exempt"], "exempt"),
        )
    return tags


def load_events(reads_path=None, recharges_path=None, passes_path=None):
    reads_path = reads_path or DATA_DIR / "reads.csv"
    recharges_path = recharges_path or DATA_DIR / "recharges.csv"
    passes_path = passes_path or DATA_DIR / "passes.csv"
    events = []

    for row in read_rows(reads_path, ["timestamp", "tag_id", "lane", "detected_class"]):
        events.append(TollEvent(
            timestamp=parse_timestamp(row["timestamp"]),
            event_type="READ",
            tag_id=row["tag_id"].strip(),
            lane=row["lane"].strip(),
            detected_class=row["detected_class"].strip().upper(),
        ))

    for row in read_rows(recharges_path, ["timestamp", "tag_id", "amount"]):
        events.append(TollEvent(
            timestamp=parse_timestamp(row["timestamp"]),
            event_type="RECHARGE",
            tag_id=row["tag_id"].strip(),
            amount=parse_decimal(row["amount"], "recharge amount"),
        ))

    for row in read_rows(passes_path, ["timestamp", "tag_id", "pass_type"]):
        pass_type = row["pass_type"].strip().upper()
        if pass_type not in {"MONTHLY_LOCAL", "TRIP_50"}:
            raise ValueError(f"Invalid pass type: {pass_type}")
        events.append(TollEvent(
            timestamp=parse_timestamp(row["timestamp"]),
            event_type="PASS",
            tag_id=row["tag_id"].strip(),
            pass_type=pass_type,
        ))

    return events
