<p align="center">
  <a href="https://github.com/lupaxa-actions-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/actions-toolbox/readme-logo.png" alt="Actions Toolbox" />
  </a>
</p>

<h1 align="center">Language Versions</h1>

Local supporting tool for the [Get Language Versions](https://github.com/lupaxa-actions-toolbox/get-language-versions) GitHub Action.
It lives in Actions Toolbox so it sits next to that action.
Install it on your machine, look up the same runtime versions the action would return, and copy the ones you want into the workflow.

The action remains the workflow step. This command prints a table of the flags you passed and the versions that matched. It does not replace `lupaxa-actions-toolbox/get-language-versions`.

> **Note:** The action still writes JSON to `latest-versions` for `fromJson`. This command prints the same versions in a table.

## Install

```bash
pip install lupaxa-language-versions
```

The first stable GitHub release publishes the package to PyPI.

## Usage

```bash
language-versions python
language-versions python --min-version 3.11 --max-version 3.13
language-versions python --highest-only
```

The table lists the flags used, then the matching versions. `--highest-only` keeps a single version in that list.

```text
┌──────────────────────┬─────────────────┐
│ Flag                 │ Value           │
├──────────────────────┼─────────────────┤
│ language             │ python          │
│ min-version          │ 3.11            │
│ max-version          │ latest          │
│ max-versions         │ 0 (every match) │
│ include-prereleases  │ no              │
│ highest-only         │ no              │
│ remove-patch-version │ no              │
│ use-head             │ no              │
├──────────────────────┴─────────────────┤
│ Versions (3)                           │
├────────────────────────────────────────┤
│ 3.11.9                                 │
│ 3.12.1                                 │
│ 3.13.0                                 │
└────────────────────────────────────────┘
```

The versions in that table are an example of the layout.

## Invalid Input

An invalid argument prints one error line, then the help text. The error line is red in a terminal.

```text
[ Error ] argument language: invalid choice: 'fish' (choose from go, node, nodejs, perl, php, python, ruby)
```

Check the versions locally, then keep the action in the workflow:

```yaml
- uses: lupaxa-actions-toolbox/get-language-versions@master
  id: get-versions
  with:
    language: "python"
    min-version: "3.11"
```

```bash
language-versions python --min-version 3.11
```

## Options

The flags match the action inputs.

| Option                 | Default | Meaning                                                                  |
| :--------------------- | :------ | :----------------------------------------------------------------------- |
| language               |         | go, node, nodejs, perl, php, python, or ruby. Required.                  |
| --min-version          | eol     | Lowest major.minor. eol is the oldest supported release. all is every.   |
| --max-version          | latest  | Highest major.minor, or latest for no upper bound.                       |
| --max-versions         | 0       | 0 keeps every match. A positive number keeps that many newest versions.  |
| --include-prereleases  | off     | Include prerelease versions.                                             |
| --highest-only         | off     | Keep only the highest matching version.                                  |
| --remove-patch-version | off     | Print major.minor only. Cannot be combined with --include-prereleases.   |
| --use-head             | off     | Read the default branch instead of the latest release. Ignored for PHP.  |

## Version Sources

The command reads the same lists as the action.

| Language | Setup Action                                                   | Version Source                                                         |
| :------- | :------------------------------------------------------------- | :--------------------------------------------------------------------- |
| Go       | [setup-go](https://github.com/actions/setup-go)                | [go-versions](https://github.com/actions/go-versions)                  |
| Node     | [setup-node](https://github.com/actions/setup-node)            | [node-versions](https://github.com/actions/node-versions)              |
| Perl     | [setup-perl](https://github.com/shogo82148/actions-setup-perl) | [actions-setup-perl](https://github.com/shogo82148/actions-setup-perl) |
| PHP      | [setup-php](https://github.com/shivammathur/setup-php)         | [phpreleases](https://phpreleases.com/api/releases/)                   |
| Python   | [setup-python](https://github.com/actions/setup-python)        | [python-versions](https://github.com/actions/python-versions)          |
| Ruby     | [setup-ruby](https://github.com/ruby/setup-ruby)               | [setup-ruby](https://github.com/ruby/setup-ruby)                       |

<a href="https://github.com/the-lupaxa-project">
  <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
