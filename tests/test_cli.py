"""The command prints the lookup and explains that it supports the action."""

from __future__ import annotations

import pytest

from lupaxa.language_versions.cli import build_parser, format_report, main


def test_help_names_the_action(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args(["--help"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "lupaxa-actions-toolbox/get-language-versions" in captured.out


def test_report_lists_flags_and_versions() -> None:
    report = format_report("python", "3.11", "latest", ["3.11.9", "3.12.1"], include_prereleases=False, highest_only=False, remove_patch_version=True, use_head=False, max_versions=0)
    assert "│ Flag                 │ Value           │" in report
    assert "│ language             │ python          │" in report
    assert "│ min-version          │ 3.11            │" in report
    assert "│ max-versions         │ 0 (every match) │" in report
    assert "│ include-prereleases  │ no              │" in report
    assert "│ remove-patch-version │ yes             │" in report
    assert "│ Versions (2)" in report
    assert "│ 3.11.9" in report
    assert "│ 3.12.1" in report
    assert report.startswith("┌")
    assert report.endswith("┘")
    assert "[" not in report


def test_invalid_language_prints_the_error_then_help(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    with pytest.raises(SystemExit) as exc:
        main(["fish"])
    assert exc.value.code == 2
    captured = capsys.readouterr()
    error_at = captured.err.index("invalid choice: 'fish'")
    help_at = captured.err.index("options:")
    assert error_at < help_at
    assert captured.err.startswith("\033[31m[ Error ] ")
    assert "language-versions: error:" not in captured.err.split("\n", 1)[0]
    assert "\033[0m" in captured.err[: captured.err.index("\n\n")]
    assert "--min-version" in captured.err


def test_conflicting_flags_fail(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["python", "--include-prereleases", "--remove-patch-version"])
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert captured.err.index("cannot be combined") < captured.err.index("options:")
