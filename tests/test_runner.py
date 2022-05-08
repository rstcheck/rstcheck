"""Tests for ``runner`` module."""
# pylint: disable=protected-access
import contextlib
import multiprocessing
import pathlib
import sys
import typing

import pytest
import pytest_mock

from rstcheck import checker, config, runner, types
from tests.conftest import EXAMPLES_DIR


class TestRstcheckMainRunnerInit:
    """Test ``RstcheckMainRunner.__init__`` method."""

    @staticmethod
    def test_load_config_file_if_set(mocker: pytest_mock.MockerFixture) -> None:
        """Test config file is loaded if set."""
        mocked_loader = mocker.patch.object(runner.RstcheckMainRunner, "load_config_file")
        config_file_path = pathlib.Path("some-file")
        init_config = config.RstcheckConfig(config_path=config_file_path)

        runner.RstcheckMainRunner([], init_config)  # act

        mocked_loader.assert_called_once_with(config_file_path)

    @staticmethod
    def test_no_load_config_file_if_unset(mocker: pytest_mock.MockerFixture) -> None:
        """Test no config file is loaded if unset."""
        mocked_loader = mocker.patch.object(runner.RstcheckMainRunner, "load_config_file")
        init_config = config.RstcheckConfig()

        runner.RstcheckMainRunner([], init_config)  # act

        mocked_loader.assert_not_called()

    @staticmethod
    @pytest.mark.skipif(sys.platform != "win32", reason="Windows specific test.")
    @pytest.mark.parametrize("pool_size", [0, 1, 60, 61, 62, 100])
    def test_max_pool_size_on_windows(pool_size: int, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test pool size is 61 at max on windows."""
        monkeypatch.setattr(multiprocessing, "cpu_count", lambda: pool_size)
        init_config = config.RstcheckConfig()

        result = runner.RstcheckMainRunner([], init_config)._pool_size

        assert result <= 61


class TestRstcheckMainRunnerConfigFileLoader:
    """Test ``RstcheckMainRunner.load_config_file`` method."""

    @staticmethod
    def test_no_config_update_on_no_file_config(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config is not updated when no file config is found."""
        monkeypatch.setattr(config, "load_config_file_from_path", lambda _: None)
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)

        _runner.load_config_file(pathlib.Path())  # act

        assert _runner.config == init_config

    @staticmethod
    def test_config_update_on_found_file_config(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config is updated when file config is found."""
        file_config = config.RstcheckConfigFile(report_level=config.ReportLevel.SEVERE)
        monkeypatch.setattr(config, "load_config_file_from_path", lambda _: file_config)
        init_config = config.RstcheckConfig(report_level=config.ReportLevel.INFO)
        _runner = runner.RstcheckMainRunner([], init_config, overwrite_config=True)

        _runner.load_config_file(pathlib.Path())  # act

        assert _runner.config.report_level == config.ReportLevel.SEVERE


class TestRstcheckMainRunnerFileListUpdater:
    """Test ``RstcheckMainRunner.update_file_list`` method."""

    @staticmethod
    def test_empty_file_list() -> None:
        """Test empty file list results in no changes."""
        file_list: typing.List[pathlib.Path] = []
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        _runner.update_file_list()  # act

        assert not _runner.files_to_check

    @staticmethod
    def test_single_file_in_list() -> None:
        """Test single file in list results in only this file in the list."""
        file_list = [EXAMPLES_DIR / "good" / "code_blocks.rst"]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        _runner.update_file_list()  # act

        assert _runner.files_to_check == file_list

    @staticmethod
    def test_multiple_files_in_list() -> None:
        """Test multiple files in list results in only these files in the list."""
        file_list = [
            EXAMPLES_DIR / "good" / "code_blocks.rst",
            EXAMPLES_DIR / "bad" / "rst.rst",
        ]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        _runner.update_file_list()  # act

        assert _runner.files_to_check == file_list

    @staticmethod
    def test_non_rst_files() -> None:
        """Test non rst files are filtered out."""
        file_list = [
            EXAMPLES_DIR / "good" / "code_blocks.rst",
            EXAMPLES_DIR / "good" / "foo.h",
            EXAMPLES_DIR / "bad" / "rst.rst",
        ]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        _runner.update_file_list()  # act

        assert len(_runner.files_to_check) == 2

    @staticmethod
    def test_directory_without_recursive() -> None:
        """Test directory without recusrive results in empty file list."""
        file_list = [EXAMPLES_DIR / "good"]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        _runner.update_file_list()  # act

        assert not _runner.files_to_check

    @staticmethod
    def test_directory_with_recursive() -> None:
        """Test directory with recusrive results in directories files in file list."""
        file_list = [EXAMPLES_DIR / "good"]
        init_config = config.RstcheckConfig(recursive=True)
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        _runner.update_file_list()  # act

        assert len(_runner.files_to_check) == 5
        assert EXAMPLES_DIR / "good" / "code_blocks.rst" in _runner.files_to_check

    @staticmethod
    def test_dash_as_file() -> None:
        """Test dash as file."""
        file_list = [pathlib.Path("-")]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        _runner.update_file_list()  # act

        assert file_list == _runner.files_to_check

    @staticmethod
    def test_dash_as_file_with_others() -> None:
        """Test dash as file with other files gets ignored."""
        file_list = [pathlib.Path("-"), EXAMPLES_DIR / "good" / "code_blocks.rst"]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        _runner.update_file_list()  # act

        assert len(_runner.files_to_check) == 1
        assert EXAMPLES_DIR / "good" / "code_blocks.rst" in _runner.files_to_check


@pytest.mark.parametrize(
    "lint_errors",
    [[], [types.LintError(source_origin="<string>", line_number=0, message="message")]],
)
def test__run_checks_sync_method(
    lint_errors: typing.List[types.LintError], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test ``RstcheckMainRunner._run_checks_sync`` method.

    Test results are returned.
    """
    monkeypatch.setattr(checker, "check_file", lambda _0, _1, _2: lint_errors)
    file_list = [
        EXAMPLES_DIR / "good" / "code_blocks.rst",
        EXAMPLES_DIR / "bad" / "rst.rst",
    ]
    init_config = config.RstcheckConfig()
    _runner = runner.RstcheckMainRunner(file_list, init_config)

    result = _runner._run_checks_sync()

    assert len(result) == 2
    assert len(result[0]) == len(lint_errors)
    assert len(result[1]) == len(lint_errors)


@pytest.mark.parametrize(
    "lint_errors",
    [[], [types.LintError(source_origin="<string>", line_number=0, message="message")]],
)
def test__run_checks_parallel_method(
    lint_errors: typing.List[types.LintError], monkeypatch: pytest.MonkeyPatch
) -> None:  # noqa: AAA05
    """Test ``RstcheckMainRunner._run_checks_parallel`` method.

    Test results are returned.
    The multiprocessing.Pool needs to be mocked, because it interferes with pytest-xdist.
    """

    class MockedPool:  # pylint: disable=too-few-public-methods
        """Mocked instance of ``multiprocessing.Pool``."""

        # noqa: AAA05
        @staticmethod
        def starmap(_0, _1) -> typing.List[typing.List[types.LintError]]:  # noqa: ANN001
            """Mock for ``multiprocessing.Pool.starmap`` method."""
            return [lint_errors, lint_errors]

    # noqa: AAA05
    @contextlib.contextmanager
    def mock_pool(_) -> typing.Generator[MockedPool, None, None]:  # noqa: ANN001
        """Mock context manager for ``multiprocessing.Pool``."""
        yield MockedPool()

    # noqa: AAA05
    monkeypatch.setattr(multiprocessing, "Pool", mock_pool)
    file_list = [
        EXAMPLES_DIR / "good" / "code_blocks.rst",
        EXAMPLES_DIR / "bad" / "rst.rst",
    ]
    init_config = config.RstcheckConfig()
    _runner = runner.RstcheckMainRunner(file_list, init_config)

    result = _runner._run_checks_parallel()  # act

    assert len(result) == 2
    assert len(result[0]) == len(lint_errors)
    assert len(result[1]) == len(lint_errors)


@pytest.mark.parametrize(
    ("results", "error_count"),
    [([], 0), ([[types.LintError(source_origin="<string>", line_number=0, message="message")]], 1)],
)
def test__update_results_method(
    results: typing.List[typing.List[types.LintError]], error_count: int
) -> None:
    """Test ``RstcheckMainRunner._update_results`` method.

    Test results are set.
    """
    init_config = config.RstcheckConfig()
    _runner = runner.RstcheckMainRunner([], init_config)

    _runner._update_results(results)  # act

    assert len(_runner.errors) == error_count


def test_check_method_sync_with_1_file(mocker: pytest_mock.MockerFixture) -> None:
    """Test ``RstcheckMainRunner.check`` method.

    Test checks are run in sync for 1 file.
    """
    mocked_sync_runner = mocker.patch.object(runner.RstcheckMainRunner, "_run_checks_sync")
    mocked_parallel_runner = mocker.patch.object(runner.RstcheckMainRunner, "_run_checks_parallel")
    init_config = config.RstcheckConfig()
    _runner = runner.RstcheckMainRunner([], init_config)
    _runner.files_to_check = [pathlib.Path("file")]

    _runner.check()  # act

    mocked_sync_runner.assert_called_once()
    mocked_parallel_runner.assert_not_called()


def test_check_method_parallel_with_more_files(mocker: pytest_mock.MockerFixture) -> None:
    """Test ``RstcheckMainRunner.check`` method.

    Test checks are run in parallel for more file.
    """
    mocked_sync_runner = mocker.patch.object(runner.RstcheckMainRunner, "_run_checks_sync")
    mocked_parallel_runner = mocker.patch.object(runner.RstcheckMainRunner, "_run_checks_parallel")
    init_config = config.RstcheckConfig()
    _runner = runner.RstcheckMainRunner([], init_config)
    _runner.files_to_check = [pathlib.Path("file"), pathlib.Path("file2")]

    _runner.check()  # act

    mocked_sync_runner.assert_not_called()
    mocked_parallel_runner.assert_called_once()


class TestRstcheckMainRunnerResultPrinter:
    """Test ``RstcheckMainRunner.get_result`` method."""

    @staticmethod
    def test_exit_code_on_success() -> None:
        """Test exit code 0 is returned on no erros."""
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)

        result = _runner.get_result()

        assert result == 0

    @staticmethod
    def test_success_message_on_success(capsys: pytest.CaptureFixture[str]) -> None:
        """Test succes message is printed on no erros."""
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)

        _runner.get_result()  # act

        assert "Success! No issues detected." in capsys.readouterr().out

    @staticmethod
    def test_exit_code_on_error() -> None:
        """Test exit code 1 is returned when erros were found."""
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)
        _runner.errors = [
            types.LintError(source_origin="<string>", line_number=0, message="message")
        ]

        result = _runner.get_result()

        assert result == 1

    @staticmethod
    def test_no_success_message_on_error(capsys: pytest.CaptureFixture[str]) -> None:
        """Test no succuess message is printed when erros were found."""
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)
        _runner.errors = [
            types.LintError(source_origin="<string>", line_number=0, message="message")
        ]

        _runner.get_result()  # act

        assert "Success! No issues detected." not in capsys.readouterr()

    @staticmethod
    def test_error_category_prepend(capsys: pytest.CaptureFixture[str]) -> None:
        """Test ``(ERROR/3)`` is prepended when no category is present."""
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)
        _runner._update_results(
            [[types.LintError(source_origin="<string>", line_number=0, message="Some error.")]]
        )

        exit_code = _runner.get_result()  # act

        assert exit_code == 1
        assert "(ERROR/3) Some error." in capsys.readouterr().err

    @staticmethod
    def test_error_message_format(capsys: pytest.CaptureFixture[str]) -> None:
        """Test error message format."""
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)
        _runner._update_results(
            [
                [
                    types.LintError(
                        source_origin="<string>", line_number=0, message="(ERROR/3) Some error."
                    )
                ]
            ]
        )

        exit_code = _runner.get_result()  # act

        assert exit_code == 1
        assert "<string>:0: (ERROR/3) Some error." in capsys.readouterr().err
