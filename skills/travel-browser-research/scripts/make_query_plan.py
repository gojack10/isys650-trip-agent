#!/usr/bin/env python3
"""Create focused web-search queries for an already-defined trip."""

from __future__ import annotations

import argparse
import json
from datetime import date


def iso_date(value: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("use YYYY-MM-DD") from exc


def build_plan(args: argparse.Namespace) -> list[dict[str, str]]:
    if args.end_date < args.start_date:
        raise ValueError("end date must be on or after start date")
    if args.travelers < 1:
        raise ValueError("travelers must be at least 1")
    if args.budget <= 0:
        raise ValueError("budget must be greater than 0")

    dates = f"{args.start_date} to {args.end_date}"
    needs = f" interests {args.interests}" if args.interests else ""
    return [
        {
            "category": "transportation",
            "goal": "Find two or three dated ways to reach the destination.",
            "query": f"{args.origin} to {args.destination} {args.start_date} official fare schedule",
        },
        {
            "category": "lodging",
            "goal": "Find three viable stays and their total-price status.",
            "query": f"{args.destination} hotel {dates} {args.travelers} travelers official total price",
        },
        {
            "category": "attractions",
            "goal": "Discover attractions that fit the traveler's interests.",
            "query": f"{args.destination} official tourism top attractions{needs}",
        },
        {
            "category": "food",
            "goal": "Find restaurants with official menus and prices.",
            "query": f"{args.destination}{needs} restaurants official menu prices",
        },
        {
            "category": "local_transit",
            "goal": "Find official local fares, passes, and service constraints.",
            "query": f"{args.destination} public transit official fares day pass",
        },
        {
            "category": "weather",
            "goal": "Find an official forecast or mark a future recheck.",
            "query": f"{args.destination} official weather forecast {dates}",
        },
        {
            "category": "safety",
            "goal": "Find current official visitor safety guidance.",
            "query": f"{args.destination} government official visitor safety advisory",
        },
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--start-date", required=True, type=iso_date)
    parser.add_argument("--end-date", required=True, type=iso_date)
    parser.add_argument("--budget", required=True, type=float)
    parser.add_argument("--travelers", type=int, default=1)
    parser.add_argument("--interests", default="")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        plan = build_plan(args)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if args.format == "json":
        print(json.dumps({
            "trip": {
                "origin": args.origin,
                "destination": args.destination,
                "start_date": args.start_date,
                "end_date": args.end_date,
                "budget": args.budget,
                "travelers": args.travelers,
                "interests": args.interests,
            },
            "queries": plan,
        }, indent=2))
    else:
        for number, item in enumerate(plan, start=1):
            print(f"{number}. [{item['category']}] {item['query']}")
            print(f"   Goal: {item['goal']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
