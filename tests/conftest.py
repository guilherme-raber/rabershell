from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from rabershell.commands.catalog import build_registry
from rabershell.core.sweep import SweepEngine
from rabershell.shell.session import ShellSession


@dataclass
class FakeSweepBackend:
    probe_calls: list[tuple[str, float]] = field(default_factory=list)

    def probe(self, destination: str, timeout_seconds: float) -> bool:
        self.probe_calls.append((destination, timeout_seconds))
        return True


@pytest.fixture
def backend() -> FakeSweepBackend:
    return FakeSweepBackend()


@pytest.fixture
def session(backend: FakeSweepBackend) -> ShellSession:
    return ShellSession(build_registry(), SweepEngine(backend, max_workers=2))
