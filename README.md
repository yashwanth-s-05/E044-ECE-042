# Electronic Toll RFID Tag Account Engine

A Python-based command-line application that simulates the account management engine of a single RFID-based highway toll plaza.

## Quick Start

### Prerequisites
- Python 3.10 or later
- Required input CSV files in the `data/` directory

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Run the application

```bash
python -m src.main
```

### Run automated tests

```bash
python -m pytest -v
```

**Note:** Run these commands from the project's root directory.

## 1. Project Overview

The Electronic Toll RFID Tag Account Engine is designed to automate toll transaction processing and prepaid RFID tag account management.

The application processes vehicle crossing records, calculates toll charges, updates tag balances, manages recharges and passes, handles exceptional transaction conditions, and generates structured reports.

The system uses CSV files for input and output, with Python handling the transaction processing and business logic.

## 2. Project Objectives

- Register and manage RFID tags and vehicle information.
- Calculate toll charges based on vehicle class.
- Apply return-trip discounts.
- Manage monthly and 50-trip passes.
- Process recharges and monitor account balances.
- Identify and manage blacklisted tags.
- Detect vehicle-class mismatches and apply penalties.
- Handle exempt vehicles and duplicate RFID reads.
- Generate daily collection reports and tag-wise statements.

## 3. Key Features

- Chronological processing of toll reads, recharges and pass purchases.
- Automated toll calculation and prepaid balance management.
- Return-trip discount calculation within the 24-hour window.
- Monthly local-resident passes and 50-trip passes.
- Low-balance warnings.
- Automatic blacklisting when a crossing results in a negative balance.
- Blacklisted tag cash transaction handling.
- Vehicle-class mismatch detection and penalties.
- Duplicate-read detection for the same tag and lane.
- Automated generation of five CSV reports.

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Application development |
| CSV | Input datasets and generated reports |
| pytest | Automated testing |
| Git | Version control |
| Visual Studio Code | Development environment |

## 5. Toll Rates

| Vehicle Class | Single-Trip Toll |
|---|---:|
| CAR | ₹65 |
| LCV | ₹105 |
| BUS_TRUCK | ₹220 |
| MAV | ₹345 |

## 6. Project Architecture

The application is organised into the following modules:

| Module | Responsibility |
|---|---|
| `config.py` | Application configuration and constants |
| `data_loader.py` | Loads input CSV datasets |
| `models.py` | Defines the data models |
| `event_processor.py` | Processes toll events chronologically |
| `toll_calculator.py` | Calculates toll fares and applicable charges |
| `tag_manager.py` | Manages tag balances and blacklist status |
| `pass_manager.py` | Handles pass management |
| `report_generator.py` | Generates transaction and collection reports |
| `main.py` | Application entry point |

## 7. Project Structure

```text
E044-ECE-042/
│
├── data/
│   ├── tags.csv
│   ├── reads.csv
│   ├── recharges.csv
│   └── passes.csv
│
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── event_processor.py
│   ├── models.py
│   ├── pass_manager.py
│   ├── report_generator.py
│   ├── tag_manager.py
│   ├── toll_calculator.py
│   └── main.py
│
├── tests/
│   ├── test_data_loader.py
│   ├── test_event_processor.py
│   ├── test_pass_manager.py
│   ├── test_reports.py
│   └── test_toll_calculator.py
│
├── docs/
│   ├── DESIGN.md
│   ├── DESIGN.pdf
│   ├── DESIGN.docx
│   ├── decision_log.md
│   ├── class-diagram.png
│   └── state-diagram.png
│
├── output/
│   └── .gitkeep
│
├── .gitignore
├── README.md
├── requirements.txt
└── commands.txt
```

## 8. Input Data

The application requires four CSV input files inside the `data/` directory.

| File | Description |
|---|---|
| `tags.csv` | Registered tag details, vehicle information and initial balances |
| `reads.csv` | Vehicle crossing records, timestamps, lanes and detected classes |
| `recharges.csv` | Tag recharge transactions |
| `passes.csv` | Pass purchase records |

These files provide the transaction data required for processing.

## 9. Business Rules

The application implements the following toll-management rules:

1. Single-trip toll charges depend on the registered vehicle class.
2. A second paid crossing within 24 hours of the first paid crossing receives a 50% discount.
3. A third crossing within the same 24-hour period is charged at the full rate.
4. Eligible local CAR tags can purchase a ₹330 monthly pass.
5. Other vehicle classes can purchase a 50-trip pass at 30 times the single-trip rate.
6. A LOW_BALANCE warning is generated when the post-crossing balance falls below twice the registered-class single-trip rate.
7. A crossing that makes the balance negative is allowed once, after which the tag is blacklisted.
8. Subsequent blacklisted crossings are charged at twice the registered-class single-trip rate in cash.
9. A higher detected vehicle class incurs the applicable higher-class rate and a ₹100 penalty.
10. A lower detected class does not reduce the registered-class toll.
11. Exempt tags are charged zero.
12. Recharge transactions must meet the minimum recharge amount of ₹100.
13. Duplicate reads of the same tag at the same lane within less than 120 seconds are ignored.

Detailed implementation decisions and edge-case interpretations are documented in `docs/DESIGN.md` and `docs/decision_log.md`.

## 10. Installation and Setup

### Prerequisites

- Python 3.10 or later
- pip package manager
- Git (for cloning the repository)

### Clone the repository

```bash
git clone https://github.com/yashwanth-s-05/E044-ECE-042.git
cd E044-ECE-042
```

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate the virtual environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Verify input files

Ensure the four required CSV files are present in the `data/` directory:

- `tags.csv`
- `reads.csv`
- `recharges.csv`
- `passes.csv`

## 11. Running the Application

Open the terminal from the repository's root directory and execute:

```bash
python -m src.main
```

The application performs the following operations:

1. Loads registered RFID tag information.
2. Reads toll transactions, recharges and pass records.
3. Processes events chronologically.
4. Applies the defined toll-management business rules.
5. Updates tag balances and transaction statuses.
6. Generates reports in the `output/` directory.

## 12. Generated Reports

After successful execution, the application generates five CSV reports.

| Output File | Description |
|---|---|
| `read_log.csv` | Toll-read outcomes, fares, penalties, balances and flags |
| `recharge_log.csv` | Recharge transaction records |
| `pass_log.csv` | Pass purchase and processing records |
| `daily_collection.csv` | Daily toll collection summary |
| `statements.csv` | Tag-wise transaction statements |

The generated reports can be opened using Microsoft Excel or any CSV-compatible application.

## 13. Automated Testing

The project includes an automated test suite using pytest.

Run all test cases using a single command:

```bash
python -m pytest -v
```

The tests cover:

- CSV data loading
- Toll-event processing
- Toll calculations
- Pass management
- Report generation

Individual test modules can also be executed separately when required.

## 14. Project Documentation

The `docs/` directory contains the supporting technical documentation:

- **DESIGN.pdf** – Complete system design document.
- **DESIGN.md** – Markdown version of the design document.
- **DESIGN.docx** – Editable design document.
- **decision_log.md** – Record of implementation decisions.
- **class-diagram.png** – System class diagram.
- **state-diagram.png** – Tag state transition diagram.

## 15. Project Demonstration

**Demonstration Video:** [Watch the Project Demo](PASTE_YOUR_VIDEO_LINK_HERE)

The demonstration covers the application workflow, execution, generated reports and selected edge-case validations.

## 16. Conclusion

The Electronic Toll RFID Tag Account Engine demonstrates an automated approach to managing RFID-based toll transactions for a single highway plaza.

It combines transaction processing, prepaid account management, toll calculations, business-rule validation, automated testing and report generation through a structured Python and CSV-based implementation.