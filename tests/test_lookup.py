"""Version filtering matches the Get Language Versions action."""

from __future__ import annotations

import pytest
from packaging.version import parse as parse_version

from lupaxa.language_versions.lookup import VersionLookupError, extract_versions, limit_versions, select_versions


def test_select_versions_keeps_highest_patch_in_range() -> None:
    chosen = select_versions(["3.11.1", "3.11.9", "3.12.0", "3.13.0rc1", "2.7.18"], parse_version("3.11"), parse_version("3.12"), include_prereleases=False, remove_patch_version=False)
    assert chosen == ["3.11.9", "3.12.0"]


def test_select_versions_can_drop_the_patch() -> None:
    chosen = select_versions(["3.11.9", "3.12.1"], parse_version("3.11"), parse_version("3.12"), include_prereleases=False, remove_patch_version=True)
    assert chosen == ["3.11", "3.12"]


def test_extract_php_and_ruby_shapes() -> None:
    php = extract_versions("php", [{"major": 8, "minor": 3, "release": 12}, {"major": 8, "minor": 4, "release": 0}])
    ruby = extract_versions("ruby", {"ruby": ["3.3.0", "3.4.1"]})
    assert php == ["8.3.12", "8.4.0"]
    assert ruby == ["3.3.0", "3.4.1"]


def test_limit_versions_applies_the_same_cuts_as_the_action() -> None:
    versions = ["3.11.9", "3.12.1", "3.13.0"]
    assert limit_versions(versions, highest_only=False, max_versions=0) == versions
    assert limit_versions(versions, highest_only=True, max_versions=0) == ["3.13.0"]
    assert limit_versions(versions, highest_only=False, max_versions=2) == ["3.12.1", "3.13.0"]


def test_limit_versions_rejects_an_empty_match() -> None:
    with pytest.raises(VersionLookupError, match="No versions matched"):
        limit_versions([], highest_only=False, max_versions=0)
