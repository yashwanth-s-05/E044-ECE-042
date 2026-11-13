# E044-ECE-042 — Electronic Toll RFID Tag Account Engine

A Python command-line application that simulates a single-plaza RFID toll account engine using CSV input files.

## Features

- Loads registered RFID tags and account balances.
- Processes toll reads, recharges and pass purchases chronologically.
- Applies single and return-trip fares.
- Handles higher/lower detected vehicle-class mismatches.
- Handles local monthly passes and 50-trip passes.
- Applies low-balance warnings and blacklisting.
- Ignores duplicate reads from the same tag and lane within 120 seconds.
- Generates five CSV reports.

## Technology

- Python 3.10+
- Python standard library
- pytest for automated tests

## Project structure

```text
data/       Input CSV files
src/        Application source code
tests/      Automated tests
output/     Generated reports (not committed)
docs/       Design and decision documentation
```

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install test dependency:

```powershell
python -m pip install -r requirements.txt
```

Place the four supplied input files in `data/`:

- tags.csv
- reads.csv
- recharges.csv
- passes.csv

## Run the application

Run from the repository root:

```powershell
python -m src.main
```

The application reads `commands.txt` and creates these files in `output/`:

- read_log.csv
- recharge_log.csv
- pass_log.csv
- daily_collection.csv
- statements.csv

## Run automated tests

```powershell
pytest
```

## Business rules

See [docs/DESIGN.md](docs/DESIGN.md) and [docs/decision_log.md](docs/decision_log.md).

## Important interpretation choices

- Exact 24-hour return boundary is included.
- Exactly 120 seconds is not considered a duplicate.
- Exempt status takes priority over class mismatch.
- A higher-class mismatch penalty is charged even when a pass covers the toll fare.
- A blacklist is removed only when a valid recharge makes the balance strictly positive.
- Pass purchases are separate cash collections, not deductions from the prepaid tag balance.
