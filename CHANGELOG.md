# Changelog

This is the changelog of `rstcheck`. Releases and their respective
changes are listed here. The order of releases is time and **not** version based!
For a list of all available releases see the
[tags section on Github](https://github.com/rstcheck/rstcheck/tags).
Links on the versions point to PyPI.

<!-- Valid subcategories
NOTE: please use them in this order.
### BREAKING CHANGES
### New features
### Bugfixes
### Documentation
### Miscellaneous
-->

## Unreleased

[diff v6.2.5...main](https://github.com/rstcheck/rstcheck/compare/v6.2.5...main)

## [v6.2.5 (2025-06-01)](https://github.com/rstcheck/rstcheck/releases/v6.2.5)

[diff v6.2.4...v6.2.5](https://github.com/rstcheck/rstcheck/compare/v6.2.4...v6.2.5)

### Documentation

- Fix readthedocs config by adding missing `build.os` value.

### Miscellaneous

- Dropped support for python 3.8
- Added python 3.13 to tox config as preparation for adding the version to the test pool. ([#247](https://github.com/rstcheck/rstcheck/issues/247))
- Dropped support for sphinx 5 ([#248](https://github.com/rstcheck/rstcheck/pull/248))
- Added python 3.13 to CI test pool ([#248](https://github.com/rstcheck/rstcheck/pull/248))
- Add sphinx 8 to test pool for python version > 3.9 ([#249](https://github.com/rstcheck/rstcheck/pull/249))

## [v6.2.4 (2024-07-07)](https://github.com/rstcheck/rstcheck/releases/v6.2.4)

[diff v6.2.3...v6.2.4](https://github.com/rstcheck/rstcheck/compare/v6.2.3...v6.2.4)

### Documentation

- Add note on how to disable pretty exception output ([#228](https://github.com/rstcheck/rstcheck/pull/228))

### Miscellaneous

- Add help text to `--version` flag ([#228](https://github.com/rstcheck/rstcheck/pull/228))

## [v6.2.3 (2024-07-07)](https://github.com/rstcheck/rstcheck/releases/v6.2.3)

[diff v6.2.2...v6.2.3](https://github.com/rstcheck/rstcheck/compare/v6.2.2...v6.2.3)

### Bugfixes

- Fix typer dependency by removing the `[standard]` extra which is only used on typer-slim.
  Typer by default has the extras included.

## [v6.2.2 (2024-07-07)](https://github.com/rstcheck/rstcheck/releases/v6.2.2)

[diff v6.2.1...v6.2.2](https://github.com/rstcheck/rstcheck/compare/v6.2.1...v6.2.2)

### Miscellaneous

- Bump min. version of typer and fix dependency group name ([#223](https://github.com/rstcheck/rstcheck/issues/223))
- Update configs for dev tooling ([#225](https://github.com/rstcheck/rstcheck/pull/225))
- Bump default python version to 3.12 ([#225](https://github.com/rstcheck/rstcheck/pull/225))

## [v6.2.1 (2024-03-23)](https://github.com/rstcheck/rstcheck/releases/v6.2.1)

[diff v6.2.0...v6.2.1](https://github.com/rstcheck/rstcheck/compare/v6.2.0...v6.2.1)

### Miscellaneous

- Remove unused pre python 3.8 compatibility code ([#195](https://github.com/rstcheck/rstcheck/pull/195))
- Drop support for sphinx v4 ([#207](https://github.com/rstcheck/rstcheck/pull/207))
- Added `__main__.py` to enable command-line execution via python -m rstcheck ([#206](https://github.com/rstcheck/rstcheck/pull/206))

## [v6.2.0 (2023-09-09)](https://github.com/rstcheck/rstcheck/releases/v6.2.0)

[diff v6.1.2...v6.2.0](https://github.com/rstcheck/rstcheck/compare/v6.1.2...v6.2.0)

### Bugfixes

- Fix bug where variable in log string was not substituted ([#188](https://github.com/rstcheck/rstcheck/pull/188))

### Miscellaneous

- Update Sphinx Theme Version and remove outdated Dark Mode Lib ([#176](https://github.com/rstcheck/rstcheck/pull/176))
- Drop support for Sphinx v2 and v3 ([#176](https://github.com/rstcheck/rstcheck/pull/176))
- Add tox environments for v6 and v7 ([#176](https://github.com/rstcheck/rstcheck/pull/176))
- Switch from poetry to setuptools ([#187](https://github.com/rstcheck/rstcheck/pull/187))
- Change test file naming convention ([#188](https://github.com/rstcheck/rstcheck/pull/188))
- Change dev tooling ([#188](https://github.com/rstcheck/rstcheck/pull/188))
- Add python 3.12 to CI ([#188](https://github.com/rstcheck/rstcheck/pull/188))

## [v6.1.2 (2023-03-12)](https://github.com/rstcheck/rstcheck/releases/v6.1.2)

[diff v6.1.1...v6.1.2](https://github.com/rstcheck/rstcheck/compare/v6.1.1...v6.1.2)

### Miscellaneous

- Update GHA workflows to use latest 'setup-python' action ([#150](https://github.com/rstcheck/rstcheck/issues/150))
- Set tomli extra dependency to python < 3.11 like rstcheck-core ([#162](https://github.com/rstcheck/rstcheck/issues/162))
- Drop python 3.7 ([#177](https://github.com/rstcheck/rstcheck/pull/177))

## [v6.1.1 (2022-11-12)](https://github.com/rstcheck/rstcheck/releases/v6.1.1)

[diff v6.1.0...v6.1.1](https://github.com/rstcheck/rstcheck/compare/v6.1.0...v6.1.1)

### Documentation

- Add link to rstcheck-core for FAQ
- Remove unused pydantic related stuff from docs ([#149](https://github.com/rstcheck/rstcheck/pull/149))

### Miscellaneous

- Remove unused dependencies (docutils & its stubs, pydantic) ([#149](https://github.com/rstcheck/rstcheck/pull/149))
- Add python 3.11 to CI

## [v6.1.0 (2022-08-14)](https://github.com/rstcheck/rstcheck/releases/v6.1.0)

[diff v6.0.0.post1...v6.1.0](https://github.com/rstcheck/rstcheck/compare/v6.0.0.post1...v6.1.0)

### Documentation

- Add note for incompatibility of typer <0.4.1 and click >=8.1 ([#138](https://github.com/rstcheck/rstcheck/issues/138))
- Update GitHub URL in installation instructions ([#139](https://github.com/rstcheck/rstcheck/pull/139))
- Fix broken mega-linter URLs ([#136](https://github.com/rstcheck/rstcheck/pull/136))
- Update release docs for changed release script

### Miscellaneous

- Fix release script's changelog insertion
- Add pre-commit-ci badge to README
- Update development tooling dependencies
- Bump lower version constraint on typer from 0.3.2 to 0.4.1 ([#138](https://github.com/rstcheck/rstcheck/issues/138))

## [v6.0.0.post1 (2022-06-05)](https://github.com/rstcheck/rstcheck/releases/v6.0.0.post1)

[diff v6.0.0...v6.0.0.post1](https://github.com/rstcheck/rstcheck/compare/v6.0.0...v6.0.0.post1)

### Miscellaneous

- Move release date into version headline link
- Don't include failing test example in sdist ([#128](https://github.com/rstcheck/rstcheck/issues/128))

## [v6.0.0 (2022-06-04)](https://github.com/rstcheck/rstcheck/releases/v6.0.0)

[diff v6.0.0rc3...v6.0.0](https://github.com/rstcheck/rstcheck/compare/v6.0.0rc3...v6.0.0)

### New features

- Add a `--version` flag back. This flag gets its information from the metadata in the virtualenv.

### Documentation

- Finalize v6 migration guide.
- Add notice to fix `rstcheck-core` version for needed features.

### Miscellaneous

- Add tox envs to test with sphinx v5.
- Update `sphinx` `extlinks` config for v5.
- Bump min version of `rstcheck-core` to v1.0.2.

## [v6.0.0rc3 (2022-05-28)](https://pypi.org/project/rstcheck/6.0.0rc3/)

[diff v6.0.0rc2...v6.0.0rc3](https://github.com/rstcheck/rstcheck/compare/v6.0.0rc2...v6.0.0rc3)

### BREAKING CHANGES

- **MOVED THE CORE LIBRARY INTO IT'S OWN REPOSITORY AT rstcheck/rstcheck-core**
- `rstcheck.config.load_config_file_from_path` now raises an FileNotFoundError if the given path
  is neither a file nor a directory ([#125](https://github.com/rstcheck/rstcheck/pull/125))
- The CLI runner exits 1 when the config path passed with `--config` does not exist ([#125](https://github.com/rstcheck/rstcheck/pull/125))

### New features

- Add `NONE` as a special config file path, to disable config file loading ([#125](https://github.com/rstcheck/rstcheck/pull/125))

### Documentation

- Update config documentation ([#126](https://github.com/rstcheck/rstcheck/pull/126))

## [v6.0.0rc2 (2022-05-26)](https://pypi.org/project/rstcheck/6.0.0rc2/)

[diff v6.0.0rc1...v6.0.0rc2](https://github.com/rstcheck/rstcheck/compare/v6.0.0rc1...v6.0.0rc2)

### New features

- Catch SyntaxWarnings in python code-blocks and handle them like SyntaxErrors ([#124](https://github.com/rstcheck/rstcheck/pull/124))
- Add additional inline configuration and flow control options ([#123](https://github.com/rstcheck/rstcheck/pull/123))
  (see the config docs for more information)

### Documentation

- Update links to new repository home at rstcheck/rstcheck
- Update config documentation

### Miscellaneous

- Fix release date in changelog for v6.0.0rc1 release
- Set the rstcheck pre-commit hook to run in serial to avoid overhead of doubling parallel runs
  with pre-commit
- Little improvements to logging messages
- Rename master branch to main

## [v6.0.0rc1 (2022-05-21)](https://pypi.org/project/rstcheck/6.0.0rc1/)

[diff v6.0.0a2...v6.0.0rc1](https://github.com/rstcheck/rstcheck/compare/v6.0.0a2...v6.0.0rc1)

### BREAKING CHANGES

- `find_ignored_languages` no longer throws exception but logs warning ([#108](https://github.com/rstcheck/rstcheck/pull/108))

### New features

- Add more thorough documentation ([#112](https://github.com/rstcheck/rstcheck/pull/112))
- Add `--log-level` option to CLI ([#108](https://github.com/rstcheck/rstcheck/pull/108))
- Add `--warn-unknown-settings` flag to CLI ([#118](https://github.com/rstcheck/rstcheck/pull/118))
- Setup logging to console for CLI ([#108](https://github.com/rstcheck/rstcheck/pull/108))
- Setup logging to console for library (deactivated by default) ([#108](https://github.com/rstcheck/rstcheck/pull/108))

## [v6.0.0a2 (2022-05-20)](https://pypi.org/project/rstcheck/6.0.0a2/)

[diff v6.0.0a1...v6.0.0a2](https://github.com/rstcheck/rstcheck/compare/v6.0.0a1...v6.0.0a2)

### BREAKING CHANGES

- String lists for `ignore_*` configs are white-space cleaned at string start and end.
  Restores behavior of pre v6. ([#116](https://github.com/rstcheck/rstcheck/pull/116))

### New features

- Add support for INI multi-line string back ([#116](https://github.com/rstcheck/rstcheck/pull/116))

### Bugfixes

- Fix bug #113 - sphinx print warnings for overwriting registered nodes ([#117](https://github.com/rstcheck/rstcheck/pull/117))

## [v6.0.0a1 (2022-05-13)](https://pypi.org/project/rstcheck/6.0.0a1/)

[diff v5.0.0...v6.0.0a1](https://github.com/rstcheck/rstcheck/compare/v5.0.0...v6.0.0a1)

### BREAKING CHANGES

- Full restructuring of the code base ([#100](https://github.com/rstcheck/rstcheck/pull/100))
- Rewrite of CLI with `typer` ([#100](https://github.com/rstcheck/rstcheck/pull/100))
- Renamed config `report` to `report_level` ([#100](https://github.com/rstcheck/rstcheck/pull/100))
- Renamed config `ignore_language` to `ignore_languages` ([#100](https://github.com/rstcheck/rstcheck/pull/100))
- Renamed CLI option `--report` to `--report-level` ([#100](https://github.com/rstcheck/rstcheck/pull/100))
- Renamed CLI option `--ignore-language` to `--ignore-languages` ([#100](https://github.com/rstcheck/rstcheck/pull/100))
- Drop CLI option `--ignore` as alias to `--ignore-languages` ([#100](https://github.com/rstcheck/rstcheck/pull/100))
- Drop CLI option `--debug` ([#100](https://github.com/rstcheck/rstcheck/pull/100))
- Drop CLI option `--version`; may be added back later ([#100](https://github.com/rstcheck/rstcheck/pull/100))
- Don't support multi-line strings in INI files ([#100](https://github.com/rstcheck/rstcheck/pull/100))
- Prohibit numbers as report level ([#100](https://github.com/rstcheck/rstcheck/pull/100))
- Non-existing files are skipped; `rstcheck non-existing-file.rst` exits 0; may be changed later ([#100](https://github.com/rstcheck/rstcheck/pull/100))
- Drop support for sphinx < 2.0
- Drop default values for directives and roles for sphinx ([#65](https://github.com/rstcheck/rstcheck/issues/65))
- CLI options now take precedence over config file options ([#96](https://github.com/rstcheck/rstcheck/issues/96))

### New features

- Add section with `Known limitations / FAQ` to the README ([#97](https://github.com/rstcheck/rstcheck/issues/97))
- Accumulate all errors in rst source instead of only one ([#83](https://github.com/rstcheck/rstcheck/issues/83))
- Allow errors in code blocks to be ignored via ignore_messages ([#100](https://github.com/rstcheck/rstcheck/pull/100))
- Add support for TOML config files ([#84](https://github.com/rstcheck/rstcheck/pull/84))

### Bugfixes

- Fix inability to ignore `code`, `code-block` and `sourcecode` directives ([#79](https://github.com/rstcheck/rstcheck/issues/79))
- Fix `code-block` options recognition ([#62](https://github.com/rstcheck/rstcheck/issues/62))
- Fix Malformed tables because of substitutions ([#82](https://github.com/rstcheck/rstcheck/pull/82))
- Fix: remove `include` directive from ignore list when sphinx is active ([#70](https://github.com/rstcheck/rstcheck/issues/70))

## [v5.0.0 (2022-04-17)](https://pypi.org/project/rstcheck/5.0.0/)

[diff v4.1.0...v5.0.0](https://github.com/rstcheck/rstcheck/compare/v4.1.0...v5.0.0)

- Add examples/ to sdist
- Add `Development` section to README and update `Testing` section
- Add `Mega-Linter` section to README
- Add `BREAKING CHANGES` sections to changelog

### BREAKING CHANGES

- Rewrite test.bash script in pytest test cases and run them on Linux in CI
- Rewrite old test suite in pytest and AAA style

## [v4.1.0 (2022-04-16)](https://pypi.org/project/rstcheck/4.1.0/)

[diff v4.0.0...v4.1.0](https://github.com/rstcheck/rstcheck/compare/v4.0.0...v4.1.0)

- Fix shebangs and scripts to use `python3` instead of `python` ([#78](https://github.com/rstcheck/rstcheck/pull/78))
- Improve the gcc checker functions by removing restrictions and
  using environment variable flags ([#88](https://github.com/rstcheck/rstcheck/pull/88))
- Fix pool size on windows by setting max to 61 ([#86](https://github.com/rstcheck/rstcheck/pull/86))
- Update test.bash script and makefile with new file location

## [v4.0.0 (2022-04-15)](https://pypi.org/project/rstcheck/4.0.0/)

[diff v3.5.0...v4.0.0](https://github.com/rstcheck/rstcheck/compare/v3.5.0...v4.0.0)

- Add inline type annotations
- Add `sphinx` as extra
- Update build process and set up `poetry`
- Add `pre-commit` and `tox` for automated testing, linting and formatting
- Move from travis to github actions
- Activate dependabot

### BREAKING CHANGES

- Drop support for python versions prior 3.7

## [v3.5.0 (2022-04-14)](https://pypi.org/project/rstcheck/3.5.0/)

[diff v3.4.0...v3.5.0](https://github.com/rstcheck/rstcheck/compare/v3.4.0...v3.5.0)

- Deprecate python versions prior 3.7

## [v3.4.0 (2022-04-12)](https://pypi.org/project/rstcheck/3.4.0/)

[diff v3.3.1...v3.4.0](https://github.com/rstcheck/rstcheck/compare/v3.3.1...v3.4.0)

- Add `--config` option to change the location of the config file.
- Add `pre-commit` hooks config.

## [v3.3.1 (2018-11-09)](https://pypi.org/project/rstcheck/3.3.1/)

[diff v3.3...v3.3.1](https://github.com/rstcheck/rstcheck/compare/v3.3...v3.3.1)

- Make compatible with Sphinx >= 1.8.

## [v3.3 (2018-03-17)](https://pypi.org/project/rstcheck/3.3/)

[diff v3.2...v3.3](https://github.com/rstcheck/rstcheck/compare/v3.2...v3.3)

- Parse more options from configuration file (thanks to Santos Gallegos).
- Allow ignoring specific (info/warning/error) messages via
  `--ignore-messages` (thanks to Santos Gallegos).

## [v3.2 (2018-02-17)](https://pypi.org/project/rstcheck/3.2/)

[diff v3.1...v3.2](https://github.com/rstcheck/rstcheck/compare/v3.1...v3.2)

- Check for invalid Markdown-style links (thanks to biscuitsnake).
- Allow configuration to be stored in `setup.cfg` (thanks to Maël Pedretti).
- Add `--recursive` option to recursively drill down directories to check for
  all `*.rst` files.

## [v3.1 (2017-03-08)](https://pypi.org/project/rstcheck/3.1/)

[diff v3.0.1...v3.1](https://github.com/rstcheck/rstcheck/compare/v3.0.1...v3.1)

- Add support for checking XML code blocks (thanks to Sameer Singh).

## [v3.0.1 (2017-03-02)](https://pypi.org/project/rstcheck/3.0.1/)

[diff v3.0...v3.0.1](https://github.com/rstcheck/rstcheck/compare/v3.0...v3.0.1)

- Support UTF-8 byte order marks (BOM). Previously, `docutils` would
  interpret the BOM as a visible character, which would lead to false positives
  about underlines being too short.

## [v3.0 (2016-12-19)](https://pypi.org/project/rstcheck/3.0/)

[diff v2.2...v3.0](https://github.com/rstcheck/rstcheck/compare/v2.2...v3.0)

- Optionally support Sphinx 1.5. Sphinx support will be enabled if Sphinx is
  installed.

## [v2.2 (2016-10-11)](https://pypi.org/project/rstcheck/2.2/)

[diff v2.1...v2.2](https://github.com/rstcheck/rstcheck/compare/v2.1...v2.2)

- Unknown

## [v2.1 (2016-10-11)](https://pypi.org/project/rstcheck/2.1/)

[diff v2.0...v2.1](https://github.com/rstcheck/rstcheck/compare/v2.0...v2.1)

- Unknown

## [v2.0 (2016-07-27)](https://pypi.org/project/rstcheck/2.0/)

[diff v1.5.1...v2.0](https://github.com/rstcheck/rstcheck/compare/v1.5.1...v2.0)

- Support loading settings from configuration files.

## [v1.5.1 (2016-05-29)](https://pypi.org/project/rstcheck/1.5.1/)

[diff v1.5...v1.5.1](https://github.com/rstcheck/rstcheck/compare/v1.5...v1.5.1)

- Unknown

## [v1.5 (2016-02-03)](https://pypi.org/project/rstcheck/1.5/)

[diff v1.4.2...v1.5](https://github.com/rstcheck/rstcheck/compare/v1.4.2...v1.5)

- Unknown

## [v1.4.2 (2015-12-16)](https://pypi.org/project/rstcheck/1.4.2/)

[diff v1.4.1...v1.4.2](https://github.com/rstcheck/rstcheck/compare/v1.4.1...v1.4.2)

- Unknown

## [v1.4.1 (2015-08-16)](https://pypi.org/project/rstcheck/1.4.1/)

[diff v1.4...v1.4.1](https://github.com/rstcheck/rstcheck/compare/v1.4...v1.4.1)

- Unknown

## [v1.4 (2015-06-26)](https://pypi.org/project/rstcheck/1.4/)

[diff v1.3.1...v1.4](https://github.com/rstcheck/rstcheck/compare/v1.3.1...v1.4)

- Unknown

## [v1.3.1 (2015-04-14)](https://pypi.org/project/rstcheck/1.3.1/)

[diff v1.3...v1.3.1](https://github.com/rstcheck/rstcheck/compare/v1.3...v1.3.1)

- Unknown

## [v1.3 (2015-04-11)](https://pypi.org/project/rstcheck/1.3/)

[diff v1.2.1...v1.3](https://github.com/rstcheck/rstcheck/compare/v1.2.1...v1.3)

- Unknown

## [v1.2.1 (2015-04-11)](https://pypi.org/project/rstcheck/1.2.1/)

[diff v1.2...v1.2.1](https://github.com/rstcheck/rstcheck/compare/v1.2...v1.2.1)

- Unknown

## [v1.2 (2015-04-11)](https://pypi.org/project/rstcheck/1.2/)

[diff v1.1.1...v1.2](https://github.com/rstcheck/rstcheck/compare/v1.1.1...v1.2)

- Unknown

## [v1.1.1 (2015-04-05)](https://pypi.org/project/rstcheck/1.1.1/)

[diff v1.1...v1.1.1](https://github.com/rstcheck/rstcheck/compare/v1.1...v1.1.1)

- Unknown

## [v1.1 (2015-04-03)](https://pypi.org/project/rstcheck/1.1/)

[diff v1.0...v1.1](https://github.com/rstcheck/rstcheck/compare/v1.0...v1.1)

- Unknown

## [v1.0 (2015-03-14)](https://pypi.org/project/rstcheck/1.0/)

[diff v0.6...v1.0](https://github.com/rstcheck/rstcheck/compare/v0.6...v1.0)

- Add Sphinx support.

## [v0.6 (2014-09-25)](https://pypi.org/project/rstcheck/0.6/)

[diff v0.5.1...v0.6](https://github.com/rstcheck/rstcheck/compare/v0.5.1...v0.6)

- Unknown

## [v0.5.1 (2014-08-23)](https://pypi.org/project/rstcheck/0.5.1/)

[diff v0.5...v0.5.1](https://github.com/rstcheck/rstcheck/compare/v0.5...v0.5.1)

- Unknown

## [v0.5 (2014-06-01)](https://pypi.org/project/rstcheck/0.5/)

[diff v0.4.1...v0.5](https://github.com/rstcheck/rstcheck/compare/v0.4.1...v0.5)

- Unknown

## [v0.4.1 (2014-05-31)](https://pypi.org/project/rstcheck/0.4.1/)

[diff v0.4...v0.4.1](https://github.com/rstcheck/rstcheck/compare/v0.4...v0.4.1)

- Unknown

## [v0.4 (2014-05-24)](https://pypi.org/project/rstcheck/0.4/)

[diff v0.3.6...v0.4](https://github.com/rstcheck/rstcheck/compare/v0.3.6...v0.4)

- Unknown

## [v0.3.6 (2014-04-12)](https://pypi.org/project/rstcheck/0.3.6/)

[diff v0.3.5...v0.3.6](https://github.com/rstcheck/rstcheck/compare/v0.3.5...v0.3.6)

- Unknown

## [v0.3.5 (2014-01-25)](https://pypi.org/project/rstcheck/0.3.5/)

[diff v0.3.4...v0.3.5](https://github.com/rstcheck/rstcheck/compare/v0.3.4...v0.3.5)

- Unknown

## [v0.3.4 (2013-12-29)](https://pypi.org/project/rstcheck/0.3.4/)

[diff v0.3.3...v0.3.4](https://github.com/rstcheck/rstcheck/compare/v0.3.3...v0.3.4)

- Unknown

## [v0.3.3 (2013-12-28)](https://pypi.org/project/rstcheck/0.3.3/)

[diff v0.3.2...v0.3.3](https://github.com/rstcheck/rstcheck/compare/v0.3.2...v0.3.3)

- Unknown

## [v0.3.2 (2013-12-27)](https://pypi.org/project/rstcheck/0.3.2/)

[diff v0.3.1...v0.3.2](https://github.com/rstcheck/rstcheck/compare/v0.3.1...v0.3.2)

- Unknown

## v0.3.1

[diff v0.2...v0.3.1](https://github.com/rstcheck/rstcheck/compare/v0.2...v0.3.1)

- Unknown

## v0.2

[diff v0.1.1...v0.2](https://github.com/rstcheck/rstcheck/compare/v0.1.1...v0.2)

- Unknown

## v0.1.1

[diff v0.1...v0.1.1](https://github.com/rstcheck/rstcheck/compare/v0.1...v0.1.1)

- Unknown

## v0.1 (2013-12-02)

[diff a146c93...v0.1](https://github.com/rstcheck/rstcheck/compare/a146c93...v0.1)

- Initial version.
