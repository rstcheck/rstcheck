# Changelog

## (next version)

## 6.0.0a1 (2022-05-13)

- Fix inability to ignore `code`, `code-block` and `sourcecode` directives (#79)
- Fix `code-block` options recognition (#62)
- Add section with `Known limitations / FAQ` to the README (#97)
- Accumulate all errors in rst source instead of only one (#83)
- Fix Malformed tables because of substitutions (#82)
- Fix: remove `include` directive from ignore list when sphinx is active (#70)
- Allow errors in code blocks to be ignored via ignore_messages (#100)

### BREAKING CHANGES

- Full restructuring of the code base (#100)
- Rewrite of CLI with `typer` (#100)
- Renamed config `report` to `report_level` (#100)
- Renamed config `ignore_language` to `ignore_languages` (#100)
- Renamed CLI option `--report` to `--report-level` (#100)
- Renamed CLI option `--ignore-language` to `--ignore-languages` (#100)
- Drop CLI option `--ignore` as alias to `--ignore-languages` (#100)
- Drop CLI option `--debug` (#100)
- Drop CLI option `--version`; may be readded later (#100)
- Don't support multiline strings in INI files (#100)
- Allow a string or list of strings for `ignore_messages` in TOML config files (#100)
- Prohibit numbers as report level (#100)
- Non-existing files are skipped; `rstcheck non-existing-file.rst` exits 0; may be changed later (#100)
- Drop support for sphinx < 2.0
- Drop default values for directves and roles for sphinx (#65)
- CLI options now take precedence over config file options (#96)

## 5.0.0 (2022-04-17)

- Add examples/ to sdist
- Add `Development` section to README and update `Testing` section
- Add `Mega-Linter` section to README
- Add `BREAKING CHANGES` sections to changelog

### BREAKING CHANGES

- Rewrite test.bash script in pytest test cases adn run them on linux in CI
- Rewrite old test suite in pytest and AAA style

## 4.1.0 (2022-04-16)

- Fix shebangs and scripts to use `python3` instead of `python` (#78)
- Improve the gcc checker functions by removing restrictions and
  using environment variable flags (#88)
- Fix pool size on windows by setting max to 61 (#86)
- Update test.bash script and makefile with new file location

## 4.0.0 (2022-04-15)

- Add inline type annotations
- Add `sphinx` as extra
- Update build process and set up `poetry`
- Add `pre-commit` and `tox` for automated testing, linting and formatting
- Move from travis to github actions
- Activate dependabot

### BREAKING CHANGES

- Drop support for python versions prior 3.7

## 3.5.0 (2022-04-14)

- Deprecate python versions prior 3.7

## 3.4.0 (2022-04-12)

- Add `--config` option to change the location of the config file.
- Add `pre-commit` hooks config.

## 3.3.1 (2018-10-09)

- Make compatible with Sphinx >= 1.8.

## 3.3 (2018-03-17)

- Parse more options from configuration file (thanks to Santos Gallegos).
- Allow ignoring specific (info/warning/error) messages via
  `--ignore-messages` (thanks to Santos Gallegos).

## 3.2 (2018-02-17)

- Check for invalid Markdown-style links (thanks to biscuitsnake).
- Allow configuration to be stored in `setup.cfg` (thanks to Maël Pedretti).
- Add `--recursive` option to recursively drill down directories to check for
  all `*.rst` files.

## 3.1 (2017-03-08)

- Add support for checking XML code blocks (thanks to Sameer Singh).

## 3.0.1 (2017-03-01)

- Support UTF-8 byte order marks (BOM). Previously, `docutils` would
  interpret the BOM as a visible character, which would lead to false positives
  about underlines being too short.

## 3.0 (2016-12-19)

- Optionally support Sphinx 1.5. Sphinx support will be enabled if Sphinx is
  installed.

## 2.0 (2015-07-27)

- Support loading settings from configuration files.

## 1.0 (2015-03-14)

- Add Sphinx support.

## 0.1 (2013-12-02)

- Initial version.
