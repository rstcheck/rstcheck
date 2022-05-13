"""Tests for ``_extras`` module."""
import pytest

from rstcheck import _compat, _extras


class TestInstallChecker:
    """Test ``is_installed_with_supported_version``."""

    @staticmethod
    @pytest.mark.skipif(_extras.SPHINX_INSTALLED, reason="Test without sphinx extra.")
    def test_false_on_missing_sphinx_package() -> None:
        """Test install-checker returns ``False`` when ``sphinx`` is missing."""
        result = _extras.is_installed_with_supported_version("sphinx")

        assert result is False

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_true_on_installed_sphinx_package() -> None:
        """Test install-checker returns ``True`` when ``sphinx`` is installed with good version."""
        result = _extras.is_installed_with_supported_version("sphinx")

        assert result is True

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_false_on_installed_sphinx_package_too_old(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test install-checker returns ``False`` when ``sphinx`` is installed with bad version."""
        monkeypatch.setattr(_compat, "version", lambda _: "0.0")

        result = _extras.is_installed_with_supported_version("sphinx")

        assert result is False


class TestInstallGuard:
    """Test ``install_guard``."""

    @staticmethod
    @pytest.mark.skipif(_extras.SPHINX_INSTALLED, reason="Test without sphinx extra.")
    def test_false_on_missing_sphinx_package() -> None:
        """Test install-guard raises exception when ``sphinx`` is missing."""
        with pytest.raises(ModuleNotFoundError):
            _extras.install_guard("sphinx")  # act

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_true_on_installed_sphinx_package() -> None:
        """Test install-guard doesn't raise when ``sphinx`` is installed."""
        _extras.install_guard("sphinx")  # act
