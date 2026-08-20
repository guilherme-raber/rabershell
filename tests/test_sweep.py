from __future__ import annotations

import threading
from dataclasses import dataclass, field

import pytest

from rabershell.core.sweep import (
    InvalidNetworkError,
    NetworkTooLargeError,
    SweepEngine,
    SweepReport,
)


@dataclass
class FakeProbeBackend:
    responsive: set[str] = field(default_factory=set)
    calls: list[str] = field(default_factory=list)

    def probe(self, destination: str, timeout_seconds: float) -> bool:
        del timeout_seconds
        self.calls.append(destination)
        return destination in self.responsive


def test_sweep_checks_hosts_concurrently_and_sorts_responses() -> None:
    backend = FakeProbeBackend({"192.0.2.2", "192.0.2.1"})
    report = SweepEngine(backend, max_workers=2).execute(
        "192.0.2.0/30", threading.Event()
    )
    assert report.network == "192.0.2.0/30"
    assert report.total_hosts == 2
    assert report.checked_hosts == 2
    assert report.responsive_hosts == ("192.0.2.1", "192.0.2.2")
    assert not report.cancelled


def test_sweep_normalizes_network_address() -> None:
    report = SweepEngine(FakeProbeBackend(), max_workers=1).execute(
        "192.0.2.42/30", threading.Event()
    )
    assert report.network == "192.0.2.40/30"


@pytest.mark.parametrize("value", ["192.0.2.1", "not-a-network", "2001:db8::/126"])
def test_sweep_rejects_invalid_or_unsupported_network(value: str) -> None:
    with pytest.raises(InvalidNetworkError):
        SweepEngine(FakeProbeBackend()).execute(value, threading.Event())


def test_sweep_rejects_network_larger_than_slash_20() -> None:
    with pytest.raises(NetworkTooLargeError, match="/20"):
        SweepEngine(FakeProbeBackend()).execute("10.0.0.0/19", threading.Event())


def test_sweep_cancellation_stops_scheduling_new_hosts() -> None:
    started = threading.Event()
    release = threading.Event()

    class BlockingBackend:
        def __init__(self) -> None:
            self.calls = 0

        def probe(self, destination: str, timeout_seconds: float) -> bool:
            del destination, timeout_seconds
            self.calls += 1
            started.set()
            release.wait(timeout=1)
            return False

    backend = BlockingBackend()
    cancel_event = threading.Event()
    result: list[SweepReport] = []
    worker = threading.Thread(
        target=lambda: result.append(
            SweepEngine(backend, max_workers=2).execute("192.0.2.0/24", cancel_event)
        )
    )
    worker.start()
    assert started.wait(timeout=1)
    cancel_event.set()
    release.set()
    worker.join(timeout=2)

    assert not worker.is_alive()
    assert len(result) == 1
    assert result[0].cancelled
    assert backend.calls <= 2
