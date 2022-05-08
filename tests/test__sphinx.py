"""Tests for ``_sphinx`` module."""
# pylint: disable=protected-access
import typing

import docutils.parsers.rst.directives as docutils_directives
import docutils.parsers.rst.roles as docutils_roles
import pytest

from rstcheck import _extras, _sphinx


if _extras.SPHINX_INSTALLED:
    import sphinx.application


class TestContextManager:
    """Test ``load_sphinx_if_available`` context manager."""

    @staticmethod  # noqa: AAA01
    @pytest.mark.skipif(_extras.SPHINX_INSTALLED, reason="Test without sphinx extra.")
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_yield_nothing_with_sphinx_missing() -> None:
        """Test for ``None`` yield and no action when sphinx is missing."""
        with _sphinx.load_sphinx_if_available() as ctx_manager:

            assert ctx_manager is None
            assert not docutils_directives._directives
            assert not docutils_roles._roles

    @staticmethod  # noqa: AAA01
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_yield_nothing_with_sphinx_installed() -> None:
        """Test for ``None`` yield but action when sphinx is installed."""
        with _sphinx.load_sphinx_if_available() as ctx_manager:

            assert ctx_manager is None
            assert docutils_directives._directives
            assert docutils_roles._roles


class TestSphinxDirectiveAndRoleGetter:
    """Test ``get_sphinx_directives_and_roles`` function."""

    @staticmethod
    @pytest.mark.skipif(_extras.SPHINX_INSTALLED, reason="Test without sphinx extra.")
    def test_exception_on_missing_sphinx() -> None:
        """Test that the install guard triggers."""
        with pytest.raises(ModuleNotFoundError):
            _sphinx.get_sphinx_directives_and_roles()

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_c_domain_is_loaded() -> None:
        """Test C domain is loaded."""
        (result_directives, result_roles) = _sphinx.get_sphinx_directives_and_roles()  # act

        assert "function" in result_directives
        assert "c:function" in result_directives
        assert "member" in result_roles
        assert "c:member" in result_roles

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_cpp_domain_is_loaded() -> None:
        """Test C++ domain is loaded."""
        (result_directives, result_roles) = _sphinx.get_sphinx_directives_and_roles()  # act

        assert "function" in result_directives
        assert "cpp:function" in result_directives
        assert "member" in result_roles
        assert "cpp:member" in result_roles

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_javascript_domain_is_loaded() -> None:
        """Test JavaScript domain is loaded."""
        (result_directives, result_roles) = _sphinx.get_sphinx_directives_and_roles()  # act

        assert "function" in result_directives
        assert "js:function" in result_directives
        assert "func" in result_roles
        assert "js:func" in result_roles

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_python_domain_is_loaded() -> None:
        """Test Python domain is loaded."""
        (result_directives, result_roles) = _sphinx.get_sphinx_directives_and_roles()  # act

        assert "function" in result_directives
        assert "py:function" in result_directives
        assert "func" in result_roles
        assert "py:func" in result_roles

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_docutils_state_dict_is_loaded(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test docutils' state is loaded."""
        test_dict_directives: typing.Dict[str, typing.Any] = {"test-directive": "test-directive"}
        monkeypatch.setattr(
            sphinx.application.docutils.directives, "_directives", test_dict_directives
        )
        test_dict_roles: typing.Dict[str, typing.Any] = {"test-role": "test-role"}
        monkeypatch.setattr(sphinx.application.docutils.roles, "_roles", test_dict_roles)

        (result_directives, result_roles) = _sphinx.get_sphinx_directives_and_roles()  # act

        assert "test-directive" in result_directives
        assert "test-role" in result_roles


class TestDirectiveAndRoleFilter:
    """Test ``filter_whitelisted_directives_and_roles`` function."""

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_directives_are_filtered(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test directives are filtered."""
        monkeypatch.setattr(_sphinx, "_DIRECTIVE_WHITELIST", ["test-directive"])
        unfiltered_directives = ["test-directive", "test-directive2"]

        (result_directives, _) = _sphinx.filter_whitelisted_directives_and_roles(
            unfiltered_directives, []
        )  # act

        assert "test-directive" not in result_directives
        assert "test-directive2" in result_directives

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_roles_are_filtered(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test roles are filtered."""
        monkeypatch.setattr(_sphinx, "_ROLE_WHITELIST", ["test-role"])
        unfiltered_roles = ["test-role", "test-role2"]

        (_, result_roles) = _sphinx.filter_whitelisted_directives_and_roles(
            [], unfiltered_roles
        )  # act

        assert "test-role" not in result_roles
        assert "test-role2" in result_roles
