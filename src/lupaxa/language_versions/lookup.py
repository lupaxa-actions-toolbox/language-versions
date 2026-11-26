"""Resolve the same runtime versions as the Get Language Versions action."""

from __future__ import annotations

import datetime

import requests
from packaging.version import InvalidVersion, Version
from packaging.version import parse as parse_version

REQUEST_TIMEOUT = 5
MAX_VERSION = parse_version("99999")
MIN_VERSION = parse_version("0")

_NODE_SOURCE = {
    "releases_url": "https://github.com/actions/node-versions/releases/latest/",
    "head_branch": "main",
    "versions_url": "https://raw.githubusercontent.com/actions/node-versions/LATEST_TAG/versions-manifest.json",
    "eol_url": "https://endoflife.date/api/nodejs.json",
}

SOURCES: dict[str, dict[str, str]] = {
    "go": {
        "releases_url": "https://github.com/actions/go-versions/releases/latest/",
        "head_branch": "main",
        "versions_url": "https://raw.githubusercontent.com/actions/go-versions/LATEST_TAG/versions-manifest.json",
        "eol_url": "https://endoflife.date/api/go.json",
    },
    "node": _NODE_SOURCE,
    "nodejs": _NODE_SOURCE,
    "perl": {
        "releases_url": "https://github.com/shogo82148/actions-setup-perl/releases/latest/",
        "head_branch": "main",
        "versions_url": "https://raw.githubusercontent.com/shogo82148/actions-setup-perl/LATEST_TAG/src/versions/perl.json",
        "eol_url": "https://endoflife.date/api/perl.json",
    },
    "php": {
        "versions_url": "https://phpreleases.com/api/releases/",
        "eol_url": "https://endoflife.date/api/php.json",
    },
    "python": {
        "releases_url": "https://github.com/actions/python-versions/releases/latest/",
        "head_branch": "main",
        "versions_url": "https://raw.githubusercontent.com/actions/python-versions/LATEST_TAG/versions-manifest.json",
        "eol_url": "https://endoflife.date/api/python.json",
    },
    "ruby": {
        "releases_url": "https://github.com/ruby/setup-ruby/releases/latest/",
        "head_branch": "master",
        "versions_url": "https://raw.githubusercontent.com/ruby/setup-ruby/LATEST_TAG/ruby-builder-versions.json",
        "eol_url": "https://endoflife.date/api/ruby.json",
    },
}


class VersionLookupError(Exception):
    """The language lookup could not return versions."""


def fetch_json(url: str) -> list[object] | dict[str, object]:
    """Return the JSON object or list from a URL."""
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    body = response.json()
    if isinstance(body, list):
        return body
    if isinstance(body, dict):
        return body
    message = f"Unexpected JSON from {url}"
    raise TypeError(message)


def latest_release_tag(releases_url: str) -> str:
    """Return the tag from the redirected GitHub latest-release URL."""
    response = requests.get(releases_url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.url.rstrip("/").split("/")[-1]


def version_list_url(language: str, *, use_head: bool) -> str:
    """Return the URL that lists versions for a language."""
    source = SOURCES[language]
    versions_url = source["versions_url"]
    if use_head and "head_branch" in source:
        return versions_url.replace("LATEST_TAG", source["head_branch"])
    if "releases_url" in source:
        return versions_url.replace("LATEST_TAG", latest_release_tag(source["releases_url"]))
    return versions_url


def version_records(payload: list[object] | dict[str, object]) -> list[dict[str, object]]:
    """Return payload entries that are JSON objects."""
    if not isinstance(payload, list):
        message = "Expected a list of version records"
        raise TypeError(message)
    records: list[dict[str, object]] = []
    for item in payload:
        if not isinstance(item, dict):
            message = "Expected a version record"
            raise TypeError(message)
        records.append(item)
    return records


def supported_minimum(language: str) -> Version:
    """Return the oldest cycle that endoflife.date still marks as supported."""
    minimum = MAX_VERSION
    for release in version_records(fetch_json(SOURCES[language]["eol_url"])):
        try:
            cycle = parse_version(str(release["cycle"]))
        except InvalidVersion:
            continue

        eol = release["eol"]
        if eol is True:
            continue
        if eol is False:
            if cycle < minimum:
                minimum = cycle
            continue
        if datetime.date.today() < datetime.date.fromisoformat(str(eol)):
            minimum = cycle
    return minimum


def resolve_minimum(min_version: str, language: str) -> Version:
    """Resolve a min-version input to a comparable version."""
    normalised = min_version.upper()
    if normalised == "EOL":
        return supported_minimum(language)
    if normalised == "ALL":
        return MIN_VERSION
    return parse_version(min_version)


def resolve_maximum(max_version: str) -> Version:
    """Resolve a max-version input to a comparable version."""
    if max_version.upper() == "LATEST":
        return MAX_VERSION
    return parse_version(max_version)


def is_version(value: str) -> bool:
    """Return true when value parses as a version."""
    try:
        parse_version(value)
    except InvalidVersion:
        return False
    return True


def extract_versions(language: str, payload: list[object] | dict[str, object]) -> list[str]:
    """Pull version strings out of a language-specific payload."""
    if language == "php":
        candidates = [f"{item['major']}.{item['minor']}.{item['release']}" for item in version_records(payload)]
    elif language == "ruby":
        if not isinstance(payload, dict):
            message = "Expected a Ruby version object"
            raise TypeError(message)
        ruby_versions = payload["ruby"]
        if not isinstance(ruby_versions, list):
            message = "Expected a list of Ruby versions"
            raise TypeError(message)
        candidates = [str(version) for version in ruby_versions]
    else:
        candidates = [str(item["version"]) for item in version_records(payload)]
    return [version for version in candidates if is_version(version)]


def remember_highest(chosen: dict[Version, str], version: str, minimum: Version, maximum: Version) -> None:
    """Keep the highest version string for each major.minor inside the range."""
    major_minor = parse_version(".".join(version.split(".")[:2]))
    if not minimum <= major_minor <= maximum:
        return
    current = chosen.get(major_minor)
    if current is None or parse_version(current) < parse_version(version):
        chosen[major_minor] = version


def select_versions(versions: list[str], minimum: Version, maximum: Version, *, include_prereleases: bool, remove_patch_version: bool) -> list[str]:
    """Filter, collapse, and sort versions the same way the action does."""
    chosen: dict[Version, str] = {}
    for version in versions:
        if not is_version(version):
            continue
        if not include_prereleases and parse_version(version).is_prerelease:
            continue
        if remove_patch_version:
            version = ".".join(version.split(".")[:2])
        remember_highest(chosen, version, minimum, maximum)
    return sorted(chosen.values(), key=parse_version)


def limit_versions(versions: list[str], *, highest_only: bool, max_versions: int) -> list[str]:
    """Apply the same highest-only and max-versions cuts as the action."""
    if not versions:
        message = "No versions matched"
        raise VersionLookupError(message)
    if highest_only:
        return [versions[-1]]
    if max_versions > 0:
        return versions[-max_versions:]
    return list(versions)


def lookup(
    language: str,
    min_version: str = "eol",
    max_version: str = "latest",
    *,
    include_prereleases: bool = False,
    highest_only: bool = False,
    remove_patch_version: bool = False,
    use_head: bool = False,
    max_versions: int = 0,
) -> list[str]:
    """Return the versions the Get Language Versions action would publish."""
    language_key = language.lower()
    if language_key not in SOURCES:
        options = ", ".join(SOURCES)
        message = f"{language} is not a valid option. Valid options are: {options}"
        raise VersionLookupError(message)
    if remove_patch_version and include_prereleases:
        message = "include-prereleases cannot be combined with remove-patch-version"
        raise VersionLookupError(message)
    if max_versions < 0:
        message = "max-versions must be 0 or greater"
        raise VersionLookupError(message)

    payload = fetch_json(version_list_url(language_key, use_head=use_head))
    versions = select_versions(
        extract_versions(language_key, payload),
        resolve_minimum(min_version, language_key),
        resolve_maximum(max_version),
        include_prereleases=include_prereleases,
        remove_patch_version=remove_patch_version,
    )
    return limit_versions(versions, highest_only=highest_only, max_versions=max_versions)
