"""Runner of rstcheck."""
import multiprocessing
import os
import pathlib
import re
import sys
import typing

from . import _sphinx, checker, config, types


class RstcheckMainRunner:
    """Main runner of rstcheck."""

    def __init__(
        self,
        check_paths: typing.List[pathlib.Path],
        rstcheck_config: config.RstcheckConfig,
        overwrite_config: bool = True,
    ) -> None:
        """Initialize the ``RstcheckMainRunner`` with a base config.

        :param check_paths: Files to check.
        :param rstcheck_config: Base configuration config from e.g. the CLI.
        :param overwrite_config: If file config overwrites current config; defaults to True
        """
        self.config = rstcheck_config
        self.overwrite_config = overwrite_config
        if rstcheck_config.config_path:
            self.load_config_file(rstcheck_config.config_path)

        self.check_paths = check_paths
        self.files_to_check: typing.List[pathlib.Path] = []
        self.update_file_list()

        pool_size = multiprocessing.cpu_count()
        # NOTE: Work around https://bugs.python.org/issue45077
        self._pool_size = pool_size if sys.platform != "win32" else min(pool_size, 61)

        self.errors: typing.List[types.LintError] = []

    def load_config_file(self, config_path: pathlib.Path) -> None:
        """Load config from file and merge with current config.

        If the loaded file config overwrites the current config depends on the ``overwrite_config``
        attribute set on initialization.

        :param config_path: Path to config file; can be directory or file
        """
        file_config = config.load_config_file_from_path(config_path)

        if file_config is None:
            return

        self.config = config.merge_configs(
            self.config, file_config, config_add_is_dominant=self.overwrite_config
        )

    def update_file_list(self) -> None:  # noqa: CCR001
        """Update file path list with paths specified on initialization.

        Clear the current file list. Then get the file and directory paths specified with
        ``self.check_paths`` and search them for rst files to check. Add those files to the file
        list.
        """
        paths = list(self.check_paths)
        self.files_to_check = []

        if len(paths) == 1 and paths[0].name == "-":
            self.files_to_check.append(paths[0])
            return

        checkable_rst_file: typing.Callable[[pathlib.Path], bool] = (
            lambda f: f.is_file() and not f.name.startswith(".") and f.suffix.casefold() == ".rst"
        )

        while paths:
            path = paths.pop(0)
            resolved_path = path.resolve()
            if self.config.recursive and resolved_path.is_dir():
                for root, directories, children in os.walk(path):
                    root_path = pathlib.Path(root)
                    paths += [
                        root_path / f
                        for f in children
                        if checkable_rst_file((root_path / f).resolve())
                    ]
                    directories[:] = [d for d in directories if not d.startswith(".")]
                continue

            if checkable_rst_file(resolved_path) and resolved_path.name != "-":
                self.files_to_check.append(path)

    def _run_checks_sync(self) -> typing.List[typing.List[types.LintError]]:
        """Check all files from the file list syncronously and return the errors.

        :return: List of lists of errors found per file
        """
        with _sphinx.load_sphinx_if_available():
            results = [
                checker.check_file(file, self.config, self.overwrite_config)
                for file in self.files_to_check
            ]
        return results

    def _run_checks_parallel(self) -> typing.List[typing.List[types.LintError]]:
        """Check all files from the file list in parallel and return the errors.

        :return: List of lists of errors found per file
        """
        with _sphinx.load_sphinx_if_available(), multiprocessing.Pool(self._pool_size) as pool:
            results = pool.starmap(
                checker.check_file,
                [(file, self.config, self.overwrite_config) for file in self.files_to_check],
            )
        return results

    def _update_results(self, results: typing.List[typing.List[types.LintError]]) -> None:
        """Take results and update error cache.

        Result normally come from ``self._run_checks_sync`` or ``self._run_checks_parallel``.
        :param results: List of lists of errors found
        """
        self.errors = []
        for errors in results:
            self.errors += errors

    def check(self) -> None:
        """Check all files in the file list and save the errors.

        Multiple files are run in parallel.

        A new call overwrite the old cached errors.
        """
        results = (
            self._run_checks_parallel() if len(self.files_to_check) > 1 else self._run_checks_sync()
        )
        self._update_results(results)

    def get_result(self, output_file: typing.Optional[typing.TextIO] = None) -> int:
        """Print all cached error messages and return exit code.

        :param output_file: file to print to; defaults to sys.stderr (if ``None``)
        :return: exit code 0 if no error is printed; 1 if any error is printed
        """
        if len(self.errors) == 0:
            print("Success! No issues detected.", file=output_file or sys.stdout)
            return 0

        err_msg_regex = re.compile(r"\([A-Z]+/[0-9]+\)")

        for error in self.errors:
            err_msg = error["message"]
            if not err_msg_regex.match(err_msg):
                err_msg = "(ERROR/3) " + err_msg

            message = f"{error['source_origin']}:{error['line_number']}: {err_msg}"

            print(message, file=output_file or sys.stderr)

        return 1

    def run(self) -> int:  # pragma: no cover
        """Run checks, print error messages and return the result.

        :return: exit code 0 if no error is printed; 1 if any error is printed
        """
        self.check()
        return self.get_result()
