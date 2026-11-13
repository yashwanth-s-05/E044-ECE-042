import csv
from src.report_generator import write_csv


def test_write_csv_creates_header_and_row(tmp_path):
    path = tmp_path / "sample.csv"
    write_csv(path, ["id", "value"], [{"id": "A1", "value": 10}])
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows == [{"id": "A1", "value": "10"}]


def test_output_contract_status_flags_and_all_tag_statements(tmp_path, monkeypatch):
    import csv
    from datetime import date, datetime
    from decimal import Decimal
    from src.models import Tag, TollEvent
    from src.event_processor import EventProcessor
    from src import report_generator as reports

    monkeypatch.setattr(reports, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(reports, "READ_LOG", tmp_path / "read_log.csv")
    monkeypatch.setattr(reports, "RECHARGE_LOG", tmp_path / "recharge_log.csv")
    monkeypatch.setattr(reports, "PASS_LOG", tmp_path / "pass_log.csv")
    monkeypatch.setattr(reports, "DAILY_COLLECTION", tmp_path / "daily_collection.csv")
    monkeypatch.setattr(reports, "STATEMENTS", tmp_path / "statements.csv")

    tag = Tag("T1", "KA01", "Test", "CAR", Decimal("500"),
              Decimal("500"), True, False)
    unused = Tag("T2", "KA02", "Other", "LCV", Decimal("100"),
                 Decimal("100"), False, False)
    when = datetime(2026, 10, 1, 10)
    processor = EventProcessor({"T1": tag, "T2": unused}).process_events([
        TollEvent(when, "PASS", "T1", pass_type="MONTHLY_LOCAL"),
        TollEvent(when, "READ", "T1", "L1", "LCV"),
    ])
    reports.generate_all_reports(processor, {"T1": tag, "T2": unused},
                                 date(2026, 10, 1), date(2026, 10, 1), "2026-10")

    with (tmp_path / "pass_log.csv").open(newline="", encoding="utf-8") as f:
        pass_rows = list(csv.DictReader(f))
    assert pass_rows[0]["status"] == "SOLD"

    with (tmp_path / "read_log.csv").open(newline="", encoding="utf-8") as f:
        read_rows = list(csv.DictReader(f))
    assert read_rows[0]["flags"] == "MISMATCH"

    with (tmp_path / "statements.csv").open(newline="", encoding="utf-8") as f:
        statement_rows = list(csv.DictReader(f))
    assert [row["tag_id"] for row in statement_rows] == ["T1", "T2"]


def test_blacklisted_crossing_counts_as_paid_crossing_and_cash():
    from datetime import date, datetime
    from decimal import Decimal
    from src.models import Tag, TollEvent
    from src.event_processor import EventProcessor
    from src import report_generator as reports
    import csv

    tag = Tag("T1", "KA01", "Test", "CAR", Decimal("1"),
              Decimal("1"), False, False)
    when = datetime(2026, 10, 1, 10)
    processor = EventProcessor({"T1": tag}).process_events([
        TollEvent(when, "READ", "T1", "L1", "CAR"),
        TollEvent(when.replace(hour=11), "READ", "T1", "L2", "CAR"),
    ])
    assert [r.outcome for r in processor.read_results] == ["SINGLE", "CASH_BLACKLISTED"]
    assert processor.cash_collection_entries == [("2026-10-01", Decimal("130.00"))]
