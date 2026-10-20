"""A job must start even when the API server's stdin is a revoked terminal.

A server launched from a terminal keeps that terminal as fd 0. Once the
terminal closes, macOS revokes the descriptor, and a Python child that
inherits it dies in ``init_sys_streams`` before running any code.
"""

from __future__ import annotations

import ctypes
import os
import sys

import pytest

from quodeq.core.run.job_status import JobStatus
from quodeq.services.jobs import InMemoryJobStore, JobManager
from tests.services.test_job_manager import _wait_for_job

# glibc exports revoke() as an ENOSYS stub, so only macOS really revokes.
_LIBC = ctypes.CDLL(None) if sys.platform == "darwin" else None


@pytest.mark.skipif(_LIBC is None, reason="revoke(2) works on macOS only")
def test_job_starts_when_server_stdin_is_revoked():
    master, slave = os.openpty()
    saved_stdin = os.dup(0)
    os.dup2(slave, 0)
    try:
        assert _LIBC.revoke(os.ttyname(slave).encode()) == 0
        mgr = JobManager(job_store=InMemoryJobStore())
        snap = mgr.start_job([sys.executable, "-c", "print('ok')"])
        done = _wait_for_job(mgr, snap.job_id)
    finally:
        os.dup2(saved_stdin, 0)
        for fd in (saved_stdin, slave, master):
            os.close(fd)

    assert done is not None and done.status == JobStatus.DONE, done
