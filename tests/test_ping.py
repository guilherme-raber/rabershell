from __future__ import annotations

import socket
import subprocess

import pytest

from conftest import FakePingBackend
from rabershell.core.ping import HostResolutionError, InvalidDestinationError, PingEngine
from rabershell.platform.ping_backend import BackendPingResult, SystemPingBackend


def test_engine_returns_backend_report() -> None:
    backend = FakePingBackend(BackendPingResult(False, "Tempo esgotado"))
    report = PingEngine(backend).execute("192.0.2.1", 3)
    assert not report.successful
    assert report.output == "Tempo esgotado"
    assert backend.calls == [("192.0.2.1", 3)]


def test_engine_rejects_invalid_syntax() -> None:
    with pytest.raises(InvalidDestinationError):
        PingEngine(FakePingBackend()).execute("host name", 4)


def test_hostname_resolution_is_separate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_resolution(host: str, port: None) -> None:
        del host, port
        raise socket.gaierror

    monkeypatch.setattr(socket, "getaddrinfo", fail_resolution)
    with pytest.raises(HostResolutionError):
        PingEngine(FakePingBackend()).execute("valid.example", 4)


def test_windows_backend_builds_structured_arguments() -> None:
    backend = SystemPingBackend("Windows")
    assert backend.build_arguments("8.8.8.8", 5) == ["ping", "-n", "5", "8.8.8.8"]


def test_linux_backend_builds_structured_arguments() -> None:
    backend = SystemPingBackend("Linux")
    assert backend.build_arguments("example.com", 2) == ["ping", "-c", "2", "example.com"]


def test_system_backend_never_uses_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(arguments: list[str], **options: object) -> subprocess.CompletedProcess[str]:
        captured["arguments"] = arguments
        captured.update(options)
        return subprocess.CompletedProcess(arguments, 0, "ok", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = SystemPingBackend("Windows").ping("127.0.0.1", 1)
    assert result.successful
    assert captured["arguments"] == ["ping", "-n", "1", "127.0.0.1"]
    assert captured["shell"] is False


def test_windows_probe_uses_single_packet_and_timeout() -> None:
    backend = SystemPingBackend("Windows")
    assert backend.build_probe_arguments("192.0.2.1", 1.0) == [
        "ping",
        "-n",
        "1",
        "-w",
        "1000",
        "192.0.2.1",
    ]


def test_probe_never_uses_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(arguments: list[str], **options: object) -> subprocess.CompletedProcess[bytes]:
        captured["arguments"] = arguments
        captured.update(options)
        return subprocess.CompletedProcess(arguments, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert SystemPingBackend("Windows").probe("192.0.2.1", 1.0)
    assert captured["arguments"] == ["ping", "-n", "1", "-w", "1000", "192.0.2.1"]
    assert captured["shell"] is False
