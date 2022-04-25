"""Sphinx helper functions."""
import contextlib
import pathlib
import tempfile
import typing

from . import _docutils, _extras


if _extras.SPHINX_INSTALLED:
    import sphinx.application
    import sphinx.domains.c
    import sphinx.domains.cpp
    import sphinx.domains.javascript
    import sphinx.domains.python
    import sphinx.domains.std


@contextlib.contextmanager
def load_sphinx_if_available() -> typing.Generator[None, None, None]:
    """Contextmanager to register Sphinx directives and roles if sphinx is available."""
    if _extras.SPHINX_INSTALLED:
        with tempfile.TemporaryDirectory() as temp_dir:
            outdir = pathlib.Path(temp_dir) / "_build"
            sphinx.application.Sphinx(
                srcdir=temp_dir,
                confdir=None,
                outdir=str(outdir),
                doctreedir=str(outdir),
                buildername="dummy",
                status=None,  # type: ignore[arg-type] # NOTE: sphinx type hint is incorrect
            )
            yield
    else:
        yield


def get_sphinx_directives_and_roles() -> typing.Tuple[typing.List[str], typing.List[str]]:
    """Return Sphinx directives and roles loaded from sphinx.

    :return: Tuple of directives and roles
    """
    _extras.install_guard("sphinx")

    sphinx_directives = list(sphinx.domains.std.StandardDomain.directives)
    sphinx_roles = list(sphinx.domains.std.StandardDomain.roles)

    for domain in [
        sphinx.domains.c.CDomain,
        sphinx.domains.cpp.CPPDomain,
        sphinx.domains.javascript.JavaScriptDomain,
        sphinx.domains.python.PythonDomain,
    ]:
        domain_directives = list(domain.directives)
        domain_roles = list(domain.roles)

        sphinx_directives += domain_directives + [
            f"{domain.name}:{item}" for item in domain_directives
        ]

        sphinx_roles += domain_roles + [f"{domain.name}:{item}" for item in domain_roles]

    sphinx_directives += list(
        sphinx.application.docutils.directives._directives  # pylint: disable=protected-access
    )
    sphinx_roles += list(
        sphinx.application.docutils.roles._roles  # pylint: disable=protected-access
    )

    return (sphinx_directives, sphinx_roles)


def filter_whitelisted_directives_and_roles(
    directives: typing.List[str], roles: typing.List[str]
) -> typing.Tuple[typing.List[str], typing.List[str]]:
    """Filter whitelisted directives and roles out of input.

    :param directives: Directives to filter
    :param roles: Roles to filter
    :return: Tuple of fitlered directives and roles
    """
    directive_whitelist = ["code", "code-block", "include"]
    role_whitelist: typing.List[str] = []

    directives = list(filter(lambda d: d not in directive_whitelist, directives))
    roles = list(filter(lambda r: r not in role_whitelist, roles))

    return (directives, roles)


def load_sphinx_ignores() -> None:
    """Register Sphinx directives and roles to ignore."""
    _extras.install_guard("sphinx")

    (directives, roles) = get_sphinx_directives_and_roles()
    (directives, roles) = filter_whitelisted_directives_and_roles(directives, roles)

    _docutils.ignore_directives_and_roles(directives, roles)
