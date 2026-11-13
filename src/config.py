from pathlib import Path
from decimal import Decimal

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

TOLL_RATES = {
    "CAR": Decimal("65.00"),
    "LCV": Decimal("105.00"),
    "BUS_TRUCK": Decimal("220.00"),
    "MAV": Decimal("345.00"),
}
CLASS_ORDER = {"CAR": 1, "LCV": 2, "BUS_TRUCK": 3, "MAV": 4}

MINIMUM_RECHARGE = Decimal("100.00")
RETURN_WINDOW_HOURS = 24
DUPLICATE_WINDOW_SECONDS = 120
LOW_BALANCE_MULTIPLIER = 2
MISMATCH_PENALTY = Decimal("100.00")

MONTHLY_LOCAL_PRICE = Decimal("330.00")
TRIP_50_COUNT = 50
TRIP_50_PRICE_MULTIPLIER = 30

EVENT_PRIORITY = {"PASS": 0, "RECHARGE": 1, "READ": 2}

READ_LOG = OUTPUT_DIR / "read_log.csv"
RECHARGE_LOG = OUTPUT_DIR / "recharge_log.csv"
PASS_LOG = OUTPUT_DIR / "pass_log.csv"
DAILY_COLLECTION = OUTPUT_DIR / "daily_collection.csv"
STATEMENTS = OUTPUT_DIR / "statements.csv"
