"""Command-line tools for Constellation calculation spike."""

from __future__ import annotations

import argparse
import json

from .chart import calculate_chart
from .schemas import BirthData


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calculate a natal chart as JSON.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--time", required=False, help="HH:MM or HH:MM:SS local time")
    parser.add_argument("--time-known", action="store_true", default=False)
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--timezone", required=True, help="IANA timezone, e.g. America/Chicago")
    parser.add_argument("--house-system", default="placidus")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    time_known = args.time_known or bool(args.time)
    birth = BirthData(
        name=args.name,
        date=args.date,
        time=args.time,
        time_known=time_known,
        latitude=args.lat,
        longitude=args.lon,
        timezone=args.timezone,
    )
    chart = calculate_chart(birth, house_system=args.house_system)
    print(json.dumps(chart.model_dump(), indent=2))


if __name__ == "__main__":
    main()
