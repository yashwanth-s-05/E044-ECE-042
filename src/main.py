import argparse
from datetime import datetime

from src.config import DATA_DIR
from src.data_loader import load_tags, load_events
from src.event_processor import EventProcessor
from src.report_generator import generate_all_reports


def parse_commands(path):
    commands = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            commands.append([part.strip() for part in line.split("|")])
    return commands


def main():
    parser = argparse.ArgumentParser(
        description="Electronic Toll RFID Tag Account Engine"
    )
    parser.add_argument(
        "--commands", default="commands.txt",
        help="Path to the command file (default: commands.txt)"
    )
    args = parser.parse_args()

    from pathlib import Path
    command_path = Path(args.commands)
    if not command_path.is_absolute():
        command_path = Path.cwd() / command_path
    if not command_path.exists():
        raise FileNotFoundError(f"Command file not found: {command_path}")

    commands = parse_commands(command_path)
    tags = None
    processor = None
    daily_start = None
    daily_end = None
    statement_month = None

    for parts in commands:
        action = parts[0].upper()

        if action == "LOAD_TAGS":
            tags = load_tags(DATA_DIR / Path(parts[1]).name)
            print(f"Loaded {len(tags)} tags.")

        elif action == "PROCESS_EVENTS":
            if tags is None:
                raise RuntimeError("Run LOAD_TAGS before PROCESS_EVENTS.")
            events = load_events(
                DATA_DIR / Path(parts[1]).name,
                DATA_DIR / Path(parts[2]).name,
                DATA_DIR / Path(parts[3]).name,
            )
            processor = EventProcessor(tags).process_events(events)
            print(f"Processed {len(events)} events.")

        elif action == "PRINT_DAILY_COLLECTION":
            daily_start = datetime.strptime(parts[1], "%Y-%m-%d").date()
            daily_end = datetime.strptime(parts[2], "%Y-%m-%d").date()
            if daily_end < daily_start:
                raise ValueError("Daily collection end date precedes start date.")

        elif action == "PRINT_STATEMENTS":
            statement_month = parts[1]
            datetime.strptime(statement_month, "%Y-%m")

        else:
            raise ValueError(f"Unknown command: {action}")

    if tags is None or processor is None:
        raise RuntimeError("Command file must load tags and process events.")
    if daily_start is None or daily_end is None or statement_month is None:
        raise RuntimeError("Command file must include both report commands.")

    generate_all_reports(
        processor, tags, daily_start, daily_end, statement_month
    )
    print("Generated five reports in the output/ folder.")


if __name__ == "__main__":
    main()
