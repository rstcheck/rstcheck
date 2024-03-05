"""Executes CLI application's `main` function.

This module acts as the entry point for the application. When executed as the
main script, it calls the `main` function from the ._cli submodule to start the
application.
"""

from __future__ import annotations

from ._cli import main

if __name__ == "__main__":
    main()
