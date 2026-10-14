"""Command-line entry point for repo-pulse."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from repo_pulse.analyzer import GitError, _build_report, analyze_repo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repo-pulse",
        description="Summarize a local git repository's recent activity.",
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="path to a git repository (default: .)"
    )
    parser.add_argument(
        "--since", help='only count commits since this date, e.g. "7 days ago" or 2024-01-01'
    )
    parser.add_argument("--json", action="store_true", help="output JSON instead of text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        summary = analyze_repo(args.path, since=args.since)
    except GitError as exc:
        print(f"repo-pulse: error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(asdict(summary), indent=2))
    else:
        print(_build_report(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
