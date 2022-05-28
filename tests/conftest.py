"""Fixtures for tests."""
import pathlib


REPO_DIR = pathlib.Path(__file__).resolve().parents[1].resolve()
TESTING_DIR = REPO_DIR / "testing"
EXAMPLES_DIR = TESTING_DIR / "examples"
