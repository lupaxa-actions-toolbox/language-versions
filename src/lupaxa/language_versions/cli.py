"""Command-line entry point for the local language-version lookup."""

from __future__ import annotations

import argparse
import os
import sys
from typing import NoReturn

from packaging.version import InvalidVersion

from lupaxa.language_versions.lookup import SOURCES, VersionLookupError, lookup
from lupaxa.language_versions.version import get_version


def _cell(text: str, width: int) -> str:
    """Return one padded table cell, including its side spaces."""
    return f" {text.ljust(width)} "


def _pair_rule(left: str, middle: str, right: str, left_width: int, right_width: int) -> str:
    """Return a two-column box-drawing rule."""
    return f"{left}{'─' * (left_width + 2)}{middle}{'─' * (right_width + 2)}{right}"


def _pair_row(left: str, right: str, left_width: int, right_width: int) -> str:
    """Return one two-column table row."""
    return f"│{_cell(left, left_width)}│{_cell(right, right_width)}│"


def _span_row(text: str, width: int) -> str:
    """Return one row that spans both columns."""
    return f"│{_cell(text, width)}│"


def format_report(
    language: str, min_version: str, max_version: str, versions: list[str], *, include_prereleases: bool, highest_only: bool, remove_patch_version: bool, use_head: bool, max_versions: int
) -> str:
    """Return a table of the flags used and the matching versions."""
    max_versions_text = "0 (every match)" if max_versions == 0 else str(max_versions)
    rows = [
        ("language", language),
        ("min-version", min_version),
        ("max-version", max_version),
        ("max-versions", max_versions_text),
        ("include-prereleases", "yes" if include_prereleases else "no"),
        ("highest-only", "yes" if highest_only else "no"),
        ("remove-patch-version", "yes" if remove_patch_version else "no"),
        ("use-head", "yes" if use_head else "no"),
    ]
    headers = ("Flag", "Value")
    left_width = max(len(headers[0]), *(len(label) for label, _ in rows))
    right_width = max(len(headers[1]), *(len(value) for _, value in rows))
    span_width = left_width + right_width + 3
    lines = [
        _pair_rule("┌", "┬", "┐", left_width, right_width),
        _pair_row(headers[0], headers[1], left_width, right_width),
        _pair_rule("├", "┼", "┤", left_width, right_width),
    ]
    lines.extend(_pair_row(label, value, left_width, right_width) for label, value in rows)
    lines.append(_pair_rule("├", "┴", "┤", left_width, right_width))
    lines.append(_span_row(f"Versions ({len(versions)})", span_width))
    lines.append(f"├{'─' * (span_width + 2)}┤")
    lines.extend(_span_row(version, span_width) for version in versions)
    lines.append(f"└{'─' * (span_width + 2)}┘")
    return "\n".join(lines)


def _use_color() -> bool:
    """Return true when an error line should be printed in red."""
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return sys.stderr.isatty()


def _red(text: str) -> str:
    """Return text in red when the error stream is a colour terminal."""
    if not _use_color():
        return text
    return f"\033[31m{text}\033[0m"


class LanguageVersionsParser(argparse.ArgumentParser):
    """Parser that leads invalid input with a red error, then the help."""

    def error(self, message: str) -> NoReturn:
        """Print the error in red, then the help, and exit."""
        print(_red(f"[ Error ] {message}"), file=sys.stderr)
        print(file=sys.stderr)
        self.print_help(sys.stderr)
        self.exit(2)


def build_parser() -> LanguageVersionsParser:
    """Return the parser for the local companion command."""
    description = "Local supporting tool for the Get Language Versions GitHub Action.\nThe workflow step remains lupaxa-actions-toolbox/get-language-versions."
    parser = LanguageVersionsParser(prog="language-versions", formatter_class=argparse.RawDescriptionHelpFormatter, description=description)
    parser.add_argument("language", choices=sorted(SOURCES), help="Language to query: go, node, nodejs, perl, php, python, or ruby")
    parser.add_argument("--min-version", default="eol", help="Lowest major.minor, eol for the oldest supported release, or all")
    parser.add_argument("--max-version", default="latest", help="Highest major.minor, or latest for no upper bound")
    parser.add_argument("--max-versions", type=int, default=0, help="How many of the newest matching versions to print. 0 prints every match")
    parser.add_argument("--include-prereleases", action="store_true", help="Include prerelease versions. Cannot be combined with --remove-patch-version")
    parser.add_argument("--highest-only", action="store_true", help="Print only the highest matching version")
    parser.add_argument("--remove-patch-version", action="store_true", help="Print major.minor only. Cannot be combined with --include-prereleases")
    parser.add_argument("--use-head", action="store_true", help="Read the default branch instead of the latest release. Ignored for PHP")
    parser.add_argument("--version", action="version", version=get_version())
    return parser


def main(argv: list[str] | None = None) -> None:
    """Look up versions and print the flags used with the matching versions."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        versions = lookup(
            args.language,
            args.min_version,
            args.max_version,
            include_prereleases=args.include_prereleases,
            highest_only=args.highest_only,
            remove_patch_version=args.remove_patch_version,
            use_head=args.use_head,
            max_versions=args.max_versions,
        )
    except (VersionLookupError, InvalidVersion) as exc:
        parser.error(str(exc))
    else:
        print(
            format_report(
                args.language,
                args.min_version,
                args.max_version,
                versions,
                include_prereleases=args.include_prereleases,
                highest_only=args.highest_only,
                remove_patch_version=args.remove_patch_version,
                use_head=args.use_head,
                max_versions=args.max_versions,
            )
        )


if __name__ == "__main__":
    main()
