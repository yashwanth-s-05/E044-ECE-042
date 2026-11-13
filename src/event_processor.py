from datetime import timedelta
from decimal import Decimal

from src.config import EVENT_PRIORITY, TOLL_RATES, DUPLICATE_WINDOW_SECONDS, MISMATCH_PENALTY
from src.models import ReadResult, RechargeResult
from src.toll_calculator import calculate_toll, record_paid_crossing
from src.tag_manager import apply_recharge, apply_account_charge, low_balance
from src.pass_manager import purchase_pass, consume_pass_trip


class EventProcessor:
    def __init__(self, tags):
        self.tags = tags
        self.read_results = []
        self.recharge_results = []
        self.pass_results = []
        self.last_reads = {}
        self.cash_collection_entries = []

    def process_events(self, events):
        ordered = sorted(
            enumerate(events),
            key=lambda pair: (
                pair[1].timestamp,
                EVENT_PRIORITY[pair[1].event_type],
                pair[0],
            ),
        )
        for _, event in ordered:
            if event.tag_id not in self.tags:
                raise ValueError(f"Unknown tag ID in event: {event.tag_id}")
            tag = self.tags[event.tag_id]
            if event.event_type == "PASS":
                self.pass_results.append(
                    purchase_pass(tag, event.pass_type, event.timestamp)
                )
            elif event.event_type == "RECHARGE":
                status = apply_recharge(tag, event.amount)
                self.recharge_results.append(RechargeResult(
                    event.timestamp, tag.tag_id, event.amount, status, tag.balance
                ))
            elif event.event_type == "READ":
                self._process_read(tag, event)
            else:
                raise ValueError(f"Unknown event type: {event.event_type}")
        return self

    def _process_read(self, tag, event):
        timestamp = event.timestamp
        key = (tag.tag_id, event.lane)
        previous = self.last_reads.get(key)
        self.last_reads[key] = timestamp

        if previous is not None:
            difference = timestamp - previous
            if timedelta(0) <= difference < timedelta(seconds=DUPLICATE_WINDOW_SECONDS):
                self._append_read(tag, event, "DUPLICATE_IGNORED",
                                  Decimal("0.00"), Decimal("0.00"), [])
                return

        tag.total_crossings += 1

        if tag.is_exempt:
            self._append_read(tag, event, "EXEMPT",
                              Decimal("0.00"), Decimal("0.00"), [])
            return

        if tag.blacklisted:
            cash = TOLL_RATES[tag.registered_class] * Decimal("2")
            tag.total_cash_paid += cash
            self.cash_collection_entries.append((timestamp.date().isoformat(), cash))
            self._append_read(tag, event, "CASH_BLACKLISTED",
                              Decimal("0.00"), Decimal("0.00"), ["BLACKLISTED"])
            return

        fare, mismatch, effective_class = calculate_toll(
            tag, event.detected_class, timestamp
        )
        penalty = MISMATCH_PENALTY if mismatch else Decimal("0.00")
        flags = []
        if mismatch:
            tag.reverify_required = True
            flags.append("MISMATCH")

        covered = consume_pass_trip(tag, timestamp)
        if covered:
            fare = Decimal("0.00")
            outcome = "PASS"
        else:
            outcome = "RETURN" if fare < TOLL_RATES[effective_class] else "SINGLE"

        apply_account_charge(tag, fare, penalty)
        if fare > Decimal("0.00"):
            record_paid_crossing(tag, timestamp)

        if tag.blacklisted:
            flags.append("BLACKLISTED")
        if low_balance(tag):
            flags.append("LOW_BALANCE")

        self._append_read(tag, event, outcome, fare, penalty, flags)

    def _append_read(self, tag, event, outcome, fare, penalty, flags):
        self.read_results.append(ReadResult(
            timestamp=event.timestamp,
            tag_id=tag.tag_id,
            lane=event.lane or "",
            registered_class=tag.registered_class,
            detected_class=event.detected_class or "",
            outcome=outcome,
            fare=Decimal(fare).quantize(Decimal("0.01")),
            penalty=Decimal(penalty).quantize(Decimal("0.01")),
            balance_after=tag.balance.quantize(Decimal("0.01")),
            flags=",".join(flags),
        ))
