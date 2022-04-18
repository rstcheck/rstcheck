"""Test suite for rstcheck as CLI tool."""
import pathlib
import subprocess  # noqa: S404
import sys
import typing

import pytest

import rstcheck


REPO_DIR = pathlib.Path(__file__).resolve().parents[1]


def get_good_example_files() -> typing.List[pathlib.Path]:
    """Get all files from examples/good."""
    return list(REPO_DIR.glob("examples/good/*.rst"))


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
@pytest.mark.parametrize("test_file", get_good_example_files())
def test_good_examples(test_file: pathlib.Path) -> None:
    """Test all files from examples/good."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        ["rstcheck", str(test_file)]
    )

    assert result.returncode == 0


def get_bad_example_files() -> typing.List[pathlib.Path]:
    """Get all files from examples/bad."""
    return list(REPO_DIR.glob("examples/bad/*.rst"))


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
@pytest.mark.parametrize("test_file", get_bad_example_files())
def test_bad_examples(test_file: pathlib.Path) -> None:
    """Test all files from examples/bad."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        ["rstcheck", str(test_file)]
    )

    assert result.returncode != 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_multiple_files_with_glob() -> None:
    """Test multiple files via glob."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        "rstcheck examples/good/*.rst", shell=True  # noqa: S602
    )

    assert result.returncode == 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_custom_directive_and_role() -> None:
    """Test file with ignored custom directive and role."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "--ignore-directives=my-directive",
            "--ignore-role=some-custom-thing",
            "examples/custom/good_with_custom.rst",
        ]
    )

    assert result.returncode == 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_custom_directive_and_role_with_pyproject_toml() -> None:
    """Test custom directive and role read from pyproject.toml config file."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "--config",
            "examples/with_configuration/pyproject.toml",
            "examples/custom/good_with_custom.rst",
        ]
    )

    assert result.returncode == 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_bad_cpp_example() -> None:
    """Test bad c++ example."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "--ignore-language=cpp",
            "examples/bad/bad_cpp.rst",
        ]
    )

    assert result.returncode == 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_bad_cpp_with_pyproject_toml() -> None:
    """Test bad c++ example with ignore language read from pyproject.toml config file."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "--config",
            "examples/with_configuration/pyproject.toml",
            "examples/bad/bad_cpp.rst",
        ]
    )

    assert result.returncode == 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_piping_from_file() -> None:
    """Test file piped into rstcheck."""
    with open(REPO_DIR / "examples/good/good.rst", encoding="utf8") as input_file:

        result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
            [
                "rstcheck",
                "-",
            ],
            stdin=input_file,
        )

        assert result.returncode == 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_mix_of_bad_and_good_examples() -> None:
    """Test mix of good and bad examples."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "examples/bad/bad_cpp.rst",
            "examples/good/good.rst",
        ]
    )

    assert result.returncode != 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_dash_is_only_allowed_alone() -> None:
    """Test "-" can only be used alone."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "-",
            "examples/good/good.rst",
        ]
    )

    assert result.returncode != 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_without_report_exits_zero() -> None:
    """Test bad example without report is ok."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "--report=none",
            "examples/bad/bad_rst.rst",
        ]
    )

    assert result.returncode == 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_missing_file_errors() -> None:
    """Test error on non existing file."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "missing_file.rst",
        ]
    )

    assert result.returncode != 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_recurive_with_good_examples() -> None:
    """Test good examples directory recursively."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "--recursive",
            "examples/good",
        ]
    )

    assert result.returncode == 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_recurive_with_bad_examples() -> None:
    """Test bad examples directory recursively."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "--recursive",
            "examples/bad",
        ]
    )

    assert result.returncode != 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_matching_ignore_msg_exits_zero() -> None:
    """Test matching ignore message."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "examples/bad/bad_rst.rst",
            "--ignore-messages",
            r"(Title .verline & underline mismatch\.$)",
        ]
    )

    assert result.returncode == 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_non_matching_ignore_msg_errors() -> None:
    """Test non matching ignore message."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "examples/bad/bad_rst.rst",
            "--ignore-messages",
            r"(No match\.$)",
        ]
    )

    assert result.returncode != 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_good_example_with_config_file() -> None:
    """Test good example with implicit config file."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "examples/with_configuration/good.rst",
        ]
    )

    assert result.returncode == 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_bad_example_with_config_file() -> None:
    """Test bad example with implicit config file."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "examples/with_configuration/bad.rst",
        ]
    )

    assert result.returncode != 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_good_example_with_pyproject_toml() -> None:
    """Test good example with explicit pyproject.toml config file."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "--config",
            "examples/with_configuration/pyproject.toml",
            "examples/with_configuration/good.rst",
        ]
    )

    assert result.returncode == 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_bad_example_with_pyproject_toml() -> None:
    """Test bad example with explicit pyproject.toml config file."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "--config",
            "examples/with_configuration/pyproject.toml",
            "examples/with_configuration/bad.rst",
        ]
    )

    assert result.returncode != 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_matching_ignore_msg_from_config_file_exits_zero() -> None:
    """Test matching ignore message from config file."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "examples/with_configuration/bad-2.rst",
        ]
    )

    assert result.returncode == 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_matching_ignore_msg_from_pyproject_toml_exits_zero() -> None:
    """Test matching ignore message from pyproject.toml config file."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "--config",
            "examples/with_configuration/pyproject.toml",
            "examples/with_configuration/bad-2.rst",
        ]
    )

    assert result.returncode == 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
def test_ignoring_config() -> None:
    """Test ignoring config file."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "--config=/dev/null",
            "examples/with_configuration/good.rst",
        ]
    )

    assert result.returncode != 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
class TestConfigFromOtherDirCanBeUsed:
    """Test that config files from other directories can be used when set via flag."""

    @staticmethod
    @pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
    def test_example_without_config_errors() -> None:
        """Test that example errors by default."""
        result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
            [
                "rstcheck",
                "examples/without_configuration/good.rst",
            ]
        )

        assert result.returncode != 0

    @staticmethod
    @pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
    def test_example_with_config_by_dir_exits_zero() -> None:
        """Test config file from other directory get used by passing a directory."""
        result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
            [
                "rstcheck",
                "--config",
                "examples/with_configuration",
                "examples/without_configuration/good.rst",
            ]
        )

        assert result.returncode == 0

    @staticmethod
    @pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
    def test_example_with_config_by_file_exits_zero() -> None:
        """Test config file from other directory get used by passing a file."""
        result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
            [
                "rstcheck",
                "--config",
                "examples/with_configuration/rstcheck.ini",
                "examples/without_configuration/good.rst",
            ]
        )

        assert result.returncode == 0

    @staticmethod
    @pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
    def test_example_with_config_by_nested_dir_exits_zero() -> None:
        """Test walking up the file tree in another directory gets a config."""
        result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
            [
                "rstcheck",
                "--config",
                "examples/with_configuration/dummydir",
                "examples/without_configuration/good.rst",
            ]
        )

        assert result.returncode == 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
@pytest.mark.skipif(rstcheck.SPHINX_INSTALLED, reason="Run only without sphinx.")
def test_sphinx_role_erros_without_sphinx() -> None:
    """Test sphinx example errors without sphinx."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "examples/sphinx/good.rst",
        ]
    )

    assert result.returncode != 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Buggy on windows and macos.")
@pytest.mark.skipif(not rstcheck.SPHINX_INSTALLED, reason="Run only with sphinx.")
def test_sphinx_role_exits_zero_with_sphinx() -> None:
    """Test sphinx example errors without sphinx."""
    result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603,S607
        [
            "rstcheck",
            "examples/sphinx/good.rst",
        ]
    )

    assert result.returncode == 0
