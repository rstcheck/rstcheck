# Changelog

This is the changelog of `rstcheck`. Releases and their respective
changes are listed here. The order of releases is time and **not** version based!
For a list of all available releases see the
[tags section on Github](https://github.com/myint/rstcheck/tags).
Links on the versions point to PyPI.

<!-- Valid subcategories
### BREAKING CHANGES
### New features
### Bugfixes
### Documentation
### Miscellaneous
-->

## Unreleased

[diff v6.0.0a2...master](https://github.com/myint/rstcheck/compare/v6.0.0a2...master)

- Add more thorough documentation (#112)

## [v6.0.0a2 (2022-05-20)](https://pypi.org/project/rstcheck/6.0.0a2/)

[diff v6.0.0a1...v6.0.0a2](https://github.com/myint/rstcheck/compare/v6.0.0a1...v6.0.0a2)

- Add support for INI multi-line string back (#116)
- Fix bug #113 - sphinx print warnings for overwriting registered nodes (#117)

### BREAKING CHANGES

- String lists for `ignore_*` configs are white-space cleaned at string start and end.
  Restores behavior of pre v6. (#116)

## [v6.0.0a1 (2022-05-13)](https://pypi.org/project/rstcheck/6.0.0a1/)

[diff v5.0.0...v6.0.0a1](https://github.com/myint/rstcheck/compare/v5.0.0...v6.0.0a1)

- Fix inability to ignore `code`, `code-block` and `sourcecode` directives (#79)
- Fix `code-block` options recognition (#62)
- Add section with `Known limitations / FAQ` to the README (#97)
- Accumulate all errors in rst source instead of only one (#83)
- Fix Malformed tables because of substitutions (#82)
- Fix: remove `include` directive from ignore list when sphinx is active (#70)
- Allow errors in code blocks to be ignored via ignore_messages (#100)
- Add support for TOML config files (#84)

### BREAKING CHANGES

- Full restructuring of the code base (#100)
- Rewrite of CLI with `typer` (#100)
- Renamed config `report` to `report_level` (#100)
- Renamed config `ignore_language` to `ignore_languages` (#100)
- Renamed CLI option `--report` to `--report-level` (#100)
- Renamed CLI option `--ignore-language` to `--ignore-languages` (#100)
- Drop CLI option `--ignore` as alias to `--ignore-languages` (#100)
- Drop CLI option `--debug` (#100)
- Drop CLI option `--version`; may be added back later (#100)
- Don't support multi-line strings in INI files (#100)
- Prohibit numbers as report level (#100)
- Non-existing files are skipped; `rstcheck non-existing-file.rst` exits 0; may be changed later (#100)
- Drop support for sphinx < 2.0
- Drop default values for directives and roles for sphinx (#65)
- CLI options now take precedence over config file options (#96)

## [v5.0.0 (2022-04-17)](https://pypi.org/project/rstcheck/5.0.0/)

[diff v4.1.0...v5.0.0](https://github.com/myint/rstcheck/compare/v4.1.0...v5.0.0)

- Add examples/ to sdist
- Add `Development` section to README and update `Testing` section
- Add `Mega-Linter` section to README
- Add `BREAKING CHANGES` sections to changelog

### BREAKING CHANGES

- Rewrite test.bash script in pytest test cases and run them on Linux in CI
- Rewrite old test suite in pytest and AAA style

## [v4.1.0 (2022-04-16)](https://pypi.org/project/rstcheck/4.1.0/)

[diff v4.0.0...v4.1.0](https://github.com/myint/rstcheck/compare/v4.0.0...v4.1.0)

- Fix shebangs and scripts to use `python3` instead of `python` (#78)
- Improve the gcc checker functions by removing restrictions and
  using environment variable flags (#88)
- Fix pool size on windows by setting max to 61 (#86)
- Update test.bash script and makefile with new file location

## [v4.0.0 (2022-04-15)](https://pypi.org/project/rstcheck/4.0.0/)

[diff v3.5.0...v4.0.0](https://github.com/myint/rstcheck/compare/v3.5.0...v4.0.0)

- Add inline type annotations
- Add `sphinx` as extra
- Update build process and set up `poetry`
- Add `pre-commit` and `tox` for automated testing, linting and formatting
- Move from travis to github actions
- Activate dependabot

### BREAKING CHANGES

- Drop support for python versions prior 3.7

## [v3.5.0 (2022-04-14)](https://pypi.org/project/rstcheck/3.5.0/)

[diff v3.4.0...v3.5.0](https://github.com/myint/rstcheck/compare/v3.4.0...v3.5.0)

- Deprecate python versions prior 3.7

## [v3.4.0 (2022-04-12)](https://pypi.org/project/rstcheck/3.4.0/)

[diff v3.3.1...v3.4.0](https://github.com/myint/rstcheck/compare/v3.3.1...v3.4.0)

- Add `--config` option to change the location of the config file.
- Add `pre-commit` hooks config.

## [v3.3.1 (2018-11-09)](https://pypi.org/project/rstcheck/3.3.1/)

[diff v3.3...v3.3.1](https://github.com/myint/rstcheck/compare/v3.3...v3.3.1)

- Make compatible with Sphinx >= 1.8.

## [v3.3 (2018-03-17)](https://pypi.org/project/rstcheck/3.3/)

[diff v3.2...v3.3](https://github.com/myint/rstcheck/compare/v3.2...v3.3)

- Parse more options from configuration file (thanks to Santos Gallegos).
- Allow ignoring specific (info/warning/error) messages via
  `--ignore-messages` (thanks to Santos Gallegos).

## [v3.2 (2018-02-17)](https://pypi.org/project/rstcheck/3.2/)

[diff v3.1...v3.2](https://github.com/myint/rstcheck/compare/v3.1...v3.2)

- Check for invalid Markdown-style links (thanks to biscuitsnake).
- Allow configuration to be stored in `setup.cfg` (thanks to Maël Pedretti).
- Add `--recursive` option to recursively drill down directories to check for
  all `*.rst` files.

## [v3.1 (2017-03-08)](https://pypi.org/project/rstcheck/3.1/)

[diff v3.0.1...v3.1](https://github.com/myint/rstcheck/compare/v3.0.1...v3.1)

- Add support for checking XML code blocks (thanks to Sameer Singh).

## [v3.0.1 (2017-03-02)](https://pypi.org/project/rstcheck/3.0.1/)

[diff v3.0...v3.0.1](https://github.com/myint/rstcheck/compare/v3.0...v3.0.1)

- Support UTF-8 byte order marks (BOM). Previously, `docutils` would
  interpret the BOM as a visible character, which would lead to false positives
  about underlines being too short.

## [v3.0 (2016-12-19)](https://pypi.org/project/rstcheck/3.0/)

[diff v2.2...v3.0](https://github.com/myint/rstcheck/compare/v2.2...v3.0)

- Optionally support Sphinx 1.5. Sphinx support will be enabled if Sphinx is
  installed.

## [v2.2 (2016-10-11)](https://pypi.org/project/rstcheck/2.2/)

[diff v2.1...v2.2](https://github.com/myint/rstcheck/compare/v2.1...v2.2)

- Unknown

## [v2.1 (2016-10-11)](https://pypi.org/project/rstcheck/2.1/)

[diff v2.0...v2.1](https://github.com/myint/rstcheck/compare/v2.0...v2.1)

- Unknown

## [v2.0 (2016-07-27)](https://pypi.org/project/rstcheck/2.0/)

[diff v1.5.1...v2.0](https://github.com/myint/rstcheck/compare/v1.5.1...v2.0)

- Support loading settings from configuration files.

## [v1.5.1 (2016-05-29)](https://pypi.org/project/rstcheck/1.5.1/)

[diff v1.5...v1.5.1](https://github.com/myint/rstcheck/compare/v1.5...v1.5.1)

- Unknown

## [v1.5 (2016-02-03)](https://pypi.org/project/rstcheck/1.5/)

[diff v1.4.2...v1.5](https://github.com/myint/rstcheck/compare/v1.4.2...v1.5)

- Unknown

## [v1.4.2 (2015-12-16)](https://pypi.org/project/rstcheck/1.4.2/)

[diff v1.4.1...v1.4.2](https://github.com/myint/rstcheck/compare/v1.4.1...v1.4.2)

- Unknown

## [v1.4.1 (2015-08-16)](https://pypi.org/project/rstcheck/1.4.1/)

[diff v1.4...v1.4.1](https://github.com/myint/rstcheck/compare/v1.4...v1.4.1)

- Unknown

## [v1.4 (2015-06-26)](https://pypi.org/project/rstcheck/1.4/)

[diff v1.3.1...v1.4](https://github.com/myint/rstcheck/compare/v1.3.1...v1.4)

- Unknown

## [v1.3.1 (2015-04-14)](https://pypi.org/project/rstcheck/1.3.1/)

[diff v1.3...v1.3.1](https://github.com/myint/rstcheck/compare/v1.3...v1.3.1)

- Unknown

## [v1.3 (2015-04-11)](https://pypi.org/project/rstcheck/1.3/)

[diff v1.2.1...v1.3](https://github.com/myint/rstcheck/compare/v1.2.1...v1.3)

- Unknown

## [v1.2.1 (2015-04-11)](https://pypi.org/project/rstcheck/1.2.1/)

[diff v1.2...v1.2.1](https://github.com/myint/rstcheck/compare/v1.2...v1.2.1)

- Unknown

## [v1.2 (2015-04-11)](https://pypi.org/project/rstcheck/1.2/)

[diff v1.1.1...v1.2](https://github.com/myint/rstcheck/compare/v1.1.1...v1.2)

- Unknown

## [v1.1.1 (2015-04-05)](https://pypi.org/project/rstcheck/1.1.1/)

[diff v1.1...v1.1.1](https://github.com/myint/rstcheck/compare/v1.1...v1.1.1)

- Unknown

## [v1.1 (2015-04-03)](https://pypi.org/project/rstcheck/1.1/)

[diff v1.0...v1.1](https://github.com/myint/rstcheck/compare/v1.0...v1.1)

- Unknown

## [v1.0 (2015-03-14)](https://pypi.org/project/rstcheck/1.0/)

[diff v0.6...v1.0](https://github.com/myint/rstcheck/compare/v0.6...v1.0)

- Add Sphinx support.

## [v0.6 (2014-09-25)](https://pypi.org/project/rstcheck/0.6/)

[diff v0.5.1...v0.6](https://github.com/myint/rstcheck/compare/v0.5.1...v0.6)

- Unknown

## [v0.5.1 (2014-08-23)](https://pypi.org/project/rstcheck/0.5.1/)

[diff v0.5...v0.5.1](https://github.com/myint/rstcheck/compare/v0.5...v0.5.1)

- Unknown

## [v0.5 (2014-06-01)](https://pypi.org/project/rstcheck/0.5/)

[diff v0.4.1...v0.5](https://github.com/myint/rstcheck/compare/v0.4.1...v0.5)

- Unknown

## [v0.4.1 (2014-05-31)](https://pypi.org/project/rstcheck/0.4.1/)

[diff v0.4...v0.4.1](https://github.com/myint/rstcheck/compare/v0.4...v0.4.1)

- Unknown

## [v0.4 (2014-05-24)](https://pypi.org/project/rstcheck/0.4/)

[diff v0.3.6...v0.4](https://github.com/myint/rstcheck/compare/v0.3.6...v0.4)

- Unknown

## [v0.3.6 (2014-04-12)](https://pypi.org/project/rstcheck/0.3.6/)

[diff v0.3.5...v0.3.6](https://github.com/myint/rstcheck/compare/v0.3.5...v0.3.6)

- Unknown

## [v0.3.5 (2014-01-25)](https://pypi.org/project/rstcheck/0.3.5/)

[diff v0.3.4...v0.3.5](https://github.com/myint/rstcheck/compare/v0.3.4...v0.3.5)

- Unknown

## [v0.3.4 (2013-12-29)](https://pypi.org/project/rstcheck/0.3.4/)

[diff v0.3.3...v0.3.4](https://github.com/myint/rstcheck/compare/v0.3.3...v0.3.4)

- Unknown

## [v0.3.3 (2013-12-28)](https://pypi.org/project/rstcheck/0.3.3/)

[diff v0.3.2...v0.3.3](https://github.com/myint/rstcheck/compare/v0.3.2...v0.3.3)

- Unknown

## [v0.3.2 (2013-12-27)](https://pypi.org/project/rstcheck/0.3.2/)

[diff v0.3.1...v0.3.2](https://github.com/myint/rstcheck/compare/v0.3.1...v0.3.2)

- Unknown

## v0.3.1

[diff v0.2...v0.3.1](https://github.com/myint/rstcheck/compare/v0.2...v0.3.1)

- Unknown

## v0.2

[diff v0.1.1...v0.2](https://github.com/myint/rstcheck/compare/v0.1.1...v0.2)

- Unknown

## v0.1.1

[diff v0.1...v0.1.1](https://github.com/myint/rstcheck/compare/v0.1...v0.1.1)

- Unknown

## v0.1 (2013-12-02)

[diff a146c93...v0.1](https://github.com/myint/rstcheck/compare/a146c93...v0.1)

- Initial version.
