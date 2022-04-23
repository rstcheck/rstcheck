"""Central place for install-checker and guards for 'extras' dependencies.

The ``*_INSTALLED`` constansts reveal wether the dependency is installed with a supported version.
The ``install_guard`` guard function is intended for use inside functions which need specific
extra packages installed.

Example usage:

.. code-block:: python

    from rstcheck import _extras

    if _extras.SPHINX_INSTALLED:
        import sphinx


    def print_sphinx_version():
        _extras.install_guard("sphinx")
        print(sphinx.version_info)
"""
import importlib
import typing

from . import _compat


ExtraDependencies = _compat.Literal["sphinx", "tomli"]
"""List of all dependencies installable through extras."""


class DependencyInfos(_compat.TypedDict):
    """Information about a dependency."""

    min_version: typing.Tuple[int, ...]
    extra: str


ExtraDependenciesInfos: typing.Dict[ExtraDependencies, DependencyInfos] = {
    "sphinx": DependencyInfos(min_version=(2, 0), extra="sphinx"),
    "tomli": DependencyInfos(min_version=(2, 0), extra="toml"),
}
"""Dependency map with their min. supported version and extra by which they can be installed."""


def is_installed_with_supported_version(package: ExtraDependencies) -> bool:
    """Check if the package is installed and has the minimum required version.

    :param package: Name of packge to check
    :return: Bool if package is installed with supported version
    """
    try:
        importlib.import_module(package)
    except ImportError:
        return False

    version: str = _compat.metadata(package).get("Version", "")
    version_tuple = tuple(int(v) for v in version.split(".")[:3])

    return version_tuple >= ExtraDependenciesInfos[package]["min_version"]


SPHINX_INSTALLED = is_installed_with_supported_version("sphinx")
TOMLI_INSTALLED = is_installed_with_supported_version("tomli")


ExtraDependenciesInstalled: typing.Dict[ExtraDependencies, bool] = {
    "sphinx": SPHINX_INSTALLED,
    "tomli": TOMLI_INSTALLED,
}


def install_guard(package: ExtraDependencies) -> None:
    """Guard code that needs the ``package`` installed and throw ModuleNotFoundError.

    See example in module docstring.

    :param package: Name of packge to check
    :raises ModuleNotFoundError: When the package is not installed.
    """
    if ExtraDependenciesInstalled[package] is True:
        return

    extra = ExtraDependenciesInfos[package]

    raise ModuleNotFoundError(
        f"No supported version of {package} installed. "
        f"Install rstcheck with {extra} extra (rstcheck[{extra}]) or "
        f"install a supported version of {package} yourself."
    )
