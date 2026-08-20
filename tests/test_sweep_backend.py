from __future__ import annotations

import subprocess

import pytest

from rabershell.platform.sweep_backend import (
    SweepToolUnavailableError,
    SystemSweepProbeBackend,
)


def test_windows_probe_uses_single_packet_and_timeout() -> None:
    backend = SystemSweepProbeBackend("Windows")
    assert backend.build_arguments("192.0.2.1", 1.0) == [
        "ping",
        "-n",
        "1",
        "-w",
        "1000",
        "192.0.2.1",
    ]


def test_linux_probe_uses_single_packet_and_timeout() -> None:
    backend = SystemSweepProbeBackend("Linux")
    assert backend.build_arguments("192.0.2.1", 1.0) == [
        "ping",
        "-c",
        "1",
        "-W",
        "1",
        "192.0.2.1",
    ]


def test_probe_never_uses_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(arguments: list[str], **options: object) -> subprocess.CompletedProcess[bytes]:
        captured["arguments"] = arguments
        captured.update(options)
        return subprocess.CompletedProcess(arguments, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert SystemSweepProbeBackend("Windows").probe("192.0.2.1", 1.0)
    assert captured["arguments"] == ["ping", "-n", "1", "-w", "1000", "192.0.2.1"]
    assert captured["shell"] is False


def test_missing_probe_tool_has_friendly_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_run(*args: object, **options: object) -> None:
        del args, options
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", fail_run)
    with pytest.raises(SweepToolUnavailableError, match="não foi encontrada"):
        SystemSweepProbeBackend("Windows").probe("192.0.2.1", 1.0)
