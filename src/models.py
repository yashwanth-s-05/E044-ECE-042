from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from typing import Optional


@dataclass
class Tag:
    tag_id: str
    vehicle_number: str
    owner_name: str
    registered_class: str
    opening_balance: Decimal
    balance: Decimal
    is_local_resident: bool
    is_exempt: bool
    blacklisted: bool = False
    reverify_required: bool = False
    active_pass: Optional["TollPass"] = None
    paid_crossings: list = field(default_factory=list)
    total_crossings: int = 0
    total_fare: Decimal = Decimal("0.00")
    total_penalties: Decimal = Decimal("0.00")
    total_cash_paid: Decimal = Decimal("0.00")
    total_recharges: Decimal = Decimal("0.00")


@dataclass
class TollPass:
    tag_id: str
    pass_type: str
    price: Decimal
    valid_from: datetime
    valid_to: datetime
    remaining_trips: Optional[int] = None

    def is_valid(self, when: datetime) -> bool:
        if not self.valid_from <= when <= self.valid_to:
            return False
        if self.pass_type == "TRIP_50":
            return self.remaining_trips is not None and self.remaining_trips > 0
        return self.pass_type == "MONTHLY_LOCAL"


@dataclass
class TollEvent:
    timestamp: datetime
    event_type: str
    tag_id: str
    lane: Optional[str] = None
    detected_class: Optional[str] = None
    amount: Optional[Decimal] = None
    pass_type: Optional[str] = None
    sequence: int = 0


@dataclass
class ReadResult:
    timestamp: datetime
    tag_id: str
    lane: str
    registered_class: str
    detected_class: str
    outcome: str
    fare: Decimal
    penalty: Decimal
    balance_after: Decimal
    flags: str


@dataclass
class RechargeResult:
    timestamp: datetime
    tag_id: str
    amount: Decimal
    status: str
    balance_after: Decimal


@dataclass
class PassResult:
    timestamp: datetime
    tag_id: str
    pass_type: str
    status: str
    price: Decimal
    valid_from: Optional[date]
    valid_to: Optional[date]
