from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from rabershell.commands.catalog import build_registry
from rabershell.core.ping import PingEngine
from rabershell.core.sweep import SweepEngine
from rabershell.platform.ping_backend import BackendPingResult
from rabershell.shell.session import ShellSession


@dataclass
class FakePingBackend:
    result: BackendPingResult = field(
        default_factory=lambda: BackendPingResult(True, "Resposta simulada")
    )
    calls: list[tuple[str, int]] = field(default_factory=list)
    probe_calls: list[tuple[str, float]] = field(default_factory=list)

    def ping(self, destination: str, count: int) -> BackendPingResult:
        self.calls.append((destination, count))
        return self.result

    def probe(self, destination: str, timeout_seconds: float) -> bool:
        self.probe_calls.append((destination, timeout_seconds))
        return True


@pytest.fixture
def backend() -> FakePingBackend:
    return FakePingBackend()


@pytest.fixture
def session(backend: FakePingBackend) -> ShellSession:
    return ShellSession(
        build_registry(), PingEngine(backend), SweepEngine(backend, max_workers=2)
    )
