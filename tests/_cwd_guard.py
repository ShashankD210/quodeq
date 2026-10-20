"""Autouse guard against tests that leave the process in another directory."""
from __future__ import annotations

import os
from collections.abc import Iterator

import pytest


@pytest.fixture(autouse=True)
def _cwd_leak_guard() -> Iterator[None]:
    """Fail any test that leaves the process in a different working directory.

    Use ``monkeypatch.chdir`` (undone before this teardown runs). A leaked
    chdir breaks every later test that resolves paths or spawns
    ``python -c`` from the repository root.
    """
    before = os.getcwd()
    yield
    after = os.getcwd()
    if after != before:
        os.chdir(before)
    assert after == before, (
        "Test leaked a working-directory change; use monkeypatch.chdir.\n"
        f"  before: {before}\n  after: {after}"
    )
