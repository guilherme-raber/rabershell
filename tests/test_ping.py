from __future__ import annotations

import socket
import subprocess
import threading
from collections.abc import Callable, Iterator
from queue import Queue

import pytest

from conftest import FakePingBackend
from rabershell.core.ping import HostResolutionError, InvalidDestinationError, PingEngine
from rabershell.platform.ping_backend import (
    BackendPingResult,
    PingExecutionTimeoutError,
    SystemPingBackend,
)


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

    process = FakeProcess(["ok\n"])

    def fake_popen(arguments: list[str], **options: object) -> FakeProcess:
        captured["arguments"] = arguments
        captured.update(options)
        return process

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    result = SystemPingBackend("Windows").ping("127.0.0.1", 1)
    assert result.successful
    assert captured["arguments"] == ["ping", "-n", "1", "127.0.0.1"]
    assert captured["shell"] is False


class FakeStdout:
    def __init__(self, lines: list[str]) -> None:
        self._lines = iter(lines)
        self.closed = False

    def __iter__(self) -> Iterator[str]:
        return self

    def __next__(self) -> str:
        return next(self._lines)

    def close(self) -> None:
        self.closed = True


class FakeProcess:
    def __init__(self, lines: list[str], return_code: int = 0) -> None:
        self.stdout = FakeStdout(lines)
        self._return_code = return_code
        self.wait_called = False
        self.killed = False

    def wait(self) -> int:
        self.wait_called = True
        return self._return_code

    def poll(self) -> int | None:
        return self._return_code if self.wait_called else None

    def kill(self) -> None:
        self.killed = True


class BlockingStdout:
    def __init__(self) -> None:
        self.lines: Queue[str | None] = Queue()

    def __iter__(self) -> Iterator[str]:
        return self

    def __next__(self) -> str:
        line = self.lines.get(timeout=2)
        if line is None:
            raise StopIteration
        return line

    def close(self) -> None:
        pass


class BlockingProcess:
    def __init__(self, return_code: int = 0) -> None:
        self.stdout = BlockingStdout()
        self._return_code = return_code
        self.wait_called = False
        self.killed = False

    def wait(self) -> int:
        self.wait_called = True
        return self._return_code

    def poll(self) -> int | None:
        return self._return_code if self.wait_called else None

    def kill(self) -> None:
        self.killed = True
        self.stdout.lines.put(None)


def test_ping_streams_first_line_before_process_finishes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process = BlockingProcess()
    monkeypatch.setattr(subprocess, "Popen", lambda *args, **options: process)
    received: list[str] = []
    first_received = threading.Event()
    result: list[BackendPingResult] = []

    def on_output(text: str) -> None:
        received.append(text)
        first_received.set()

    worker = threading.Thread(
        target=lambda: result.append(
            SystemPingBackend("Windows").ping("127.0.0.1", 2, on_output=on_output)
        )
    )
    worker.start()
    process.stdout.lines.put("linha 1\r\n")

    assert first_received.wait(timeout=1)
    assert worker.is_alive()
    assert not process.wait_called

    process.stdout.lines.put("linha 2\r\n")
    process.stdout.lines.put(None)
    worker.join(timeout=2)

    assert not worker.is_alive()
    assert received == ["linha 1\n", "linha 2\n"]
    assert result[0].output == "linha 1\nlinha 2"


def test_ping_stream_preserves_nonzero_return_code(monkeypatch: pytest.MonkeyPatch) -> None:
    process = FakeProcess(["falha\n"], return_code=1)
    monkeypatch.setattr(subprocess, "Popen", lambda *args, **options: process)
    received: list[str] = []
    result = SystemPingBackend("Windows").ping("192.0.2.1", 1, received.append)
    assert not result.successful
    assert received == ["falha\n"]


def test_ping_reports_process_start_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_start(*args: object, **options: object) -> None:
        del args, options
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "Popen", fail_start)
    with pytest.raises(RuntimeError, match="não foi encontrada"):
        SystemPingBackend("Windows").ping("127.0.0.1", 1)


def test_ping_timeout_kills_process(monkeypatch: pytest.MonkeyPatch) -> None:
    process = FakeProcess([])

    class ImmediateTimer:
        daemon = False

        def __init__(self, interval: float, function: Callable[[], None]) -> None:
            del interval
            self._function = function

        def start(self) -> None:
            self._function()

        def cancel(self) -> None:
            pass

    monkeypatch.setattr(subprocess, "Popen", lambda *args, **options: process)
    monkeypatch.setattr(threading, "Timer", ImmediateTimer)
    with pytest.raises(PingExecutionTimeoutError, match="tempo limite"):
        SystemPingBackend("Windows").ping("127.0.0.1", 1)
    assert process.killed


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
