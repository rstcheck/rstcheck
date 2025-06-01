"""Script for preparing the repo for a new release."""

from __future__ import annotations

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

PATCH = ("patch", "bugfix")
MINOR = ("minor", "feature")
MAJOR = ("major", "breaking")

REPO_URL = "https://github.com/rstcheck/rstcheck"


#: -- MAIN -----------------------------------------------------------------------------
def bump_version(current_version: str, release_type: str = "patch") -> str:
    """Bump the current version for the next release.

    :param release_type: type of release;
        allowed values are: patch | minor/feature | major/breaking;
        defaults to "patch"
    :raises ValueError: when an invalid release_type is given.
    :raises ValueError: when the version string from pyproject.toml is not parsable.
    :return: new version string
    """
    if release_type not in PATCH + MINOR + MAJOR:
        msg = f"Invalid version increase type: {release_type}"
        raise ValueError(msg)

    version_parts = re.match(r"v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)", current_version)
    if not version_parts:
        msg = f"Unparsable version: {current_version}"
        raise ValueError(msg)

    if release_type in MAJOR:
        version = f"{int(version_parts.group('major')) + 1}.0.0"
    elif release_type in MINOR:
        version = f"{version_parts.group('major')}.{int(version_parts.group('minor')) + 1}.0"
    elif release_type in PATCH:
        version = (
            f"{version_parts.group('major')}"
            f".{version_parts.group('minor')}"
            f".{int(version_parts.group('patch')) + 1}"
        )
    else:
        print("Given `RELEASE TYPE` is invalid.")  # noqa: T201
        sys.exit(1)

    return f"v{version}"


def update_changelog(new_version: str, last_version: str, *, first_release: bool) -> None:
    """Update CHANGELOG.md to be release ready.

    :param new_version: new version string
    :param last_version: current version string
    :first_release: if this is the first release
    """
    with Path("CHANGELOG.md").open(encoding="utf8") as changelog_file:
        changelog_lines = changelog_file.read().split("\n")

    release_line = 0

    for idx, line in enumerate(changelog_lines):
        if line.startswith("## Unreleased"):
            release_line = idx

    if release_line:
        today = datetime.datetime.now(tz=datetime.UTC).date().isoformat()
        compare = f"{'' if first_release else ''}{last_version}...{new_version}"  # noqa: RUF034
        changelog_lines[release_line] = (
            "## Unreleased\n"
            "\n"
            f"[diff {new_version}...main]"
            f"({REPO_URL}/compare/{new_version}...main)\n"
            "\n"
            f"## [{new_version} ({today})]({REPO_URL}/releases/{new_version})\n"
            "\n"
            f"[diff {compare}]({REPO_URL}/compare/{compare})"
        )

    if len(changelog_lines) - 1 >= release_line + 2:
        changelog_lines.pop(release_line + 1)  # Remove blank line
        changelog_lines.pop(release_line + 1)  # Remove [diff ...] link line

    with Path("CHANGELOG.md").open("w", encoding="utf8") as changelog_file:
        changelog_file.write("\n".join(changelog_lines))


def commit_and_tag(version: str) -> None:
    """Git commit and tag the new release."""
    subprocess.run(  # noqa: S603
        [  # noqa: S607
            "git",
            "commit",
            "--no-verify",
            f'--message="release {version} [skip ci]"',
            "--include",
            "pyproject.toml",
            "CHANGELOG.md",
        ],
        check=True,
    )
    subprocess.run(  # noqa: S603
        ["git", "tag", "-am", f"'{version}'", version],  # noqa: S607
        check=True,
    )


def _parser() -> argparse.Namespace:
    """Create parser and return parsed args."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "increase_type",
        metavar="RELEASE TYPE",
        default="patch",
        nargs="?",
        help=(
            "Release type: patch/bugfix | minor/feature | major/breaking; "
            "gets ignored on `--first-release`; "
            "defaults to patch"
        ),
    )
    parser.add_argument(
        "--first-release",
        action="store_true",
        help="Flag for first release to prevent version bumping.",
    )
    return parser.parse_args()


def _main() -> int:
    """Prepare release main routine."""
    args = _parser()

    if args.first_release:
        release_version = "v1.0.0"
        #: Get first commit
        current_version = subprocess.run(  # noqa: S603
            ["git", "rev-list", "--max-parents=0", "HEAD"],  # noqa: S607
            check=True,
            capture_output=True,
        ).stdout.decode()[0:7]
    else:
        git_tags = (
            subprocess.run(  # noqa: S603
                ["git", "tag", "--list"],  # noqa: S607
                check=True,
                capture_output=True,
                cwd=Path(__file__).parent,
            )
            .stdout.decode()
            .split("\n")
        )
        git_tags = [t for t in git_tags if t.startswith("v")]
        git_tags.sort()
        current_version = git_tags[-1]
        release_version = bump_version(current_version, args.increase_type)
    update_changelog(
        release_version,
        current_version,
        first_release=args.first_release,
    )
    commit_and_tag(release_version)
    return 0


if __name__ == "__main__":
    sys.exit(_main())
