from __future__ import annotations

import threading
import tkinter as tk

import pytest

from conftest import FakePingBackend
from rabershell.gui.terminal import TerminalWindow
from rabershell.shell.models import CommandEvent, CommandEventType, CommandResult
from rabershell.shell.session import ShellSession


def test_session_emits_ordered_output_then_completion(
    session: ShellSession, backend: FakePingBackend
) -> None:
    backend.result = backend.result.__class__(True, "linha 1\nlinha 2")
    events: list[CommandEvent] = []
    session.execute_events("ping 127.0.0.1 --count 2", events.append)

    assert [event.type for event in events] == [
        CommandEventType.OUTPUT,
        CommandEventType.OUTPUT,
        CommandEventType.COMPLETED,
    ]
    assert [event.text for event in events[:-1]] == ["linha 1\n", "linha 2\n"]
    assert events[-1].result == CommandResult()


@pytest.mark.parametrize(
    ("setup_commands", "ping_command"),
    [
        ((), "ping 127.0.0.1"),
        ((), "icmp ping 127.0.0.1"),
        (("icmp",), "ping 127.0.0.1"),
    ],
)
def test_all_ping_routes_use_same_streaming_implementation(
    session: ShellSession,
    backend: FakePingBackend,
    setup_commands: tuple[str, ...],
    ping_command: str,
) -> None:
    for command in setup_commands:
        session.execute(command)
    events: list[CommandEvent] = []
    session.execute_events(ping_command, events.append)
    assert backend.calls == [("127.0.0.1", 4)]
    assert events[0] == CommandEvent.output("Resposta simulada\n")
    assert events[-1].type is CommandEventType.COMPLETED


def test_streamed_stdout_is_not_duplicated_in_completion(
    session: ShellSession, backend: FakePingBackend
) -> None:
    backend.result = backend.result.__class__(True, "resposta única")
    events: list[CommandEvent] = []
    session.execute_events("ping 127.0.0.1", events.append)
    output = "".join(event.text for event in events if event.type is CommandEventType.OUTPUT)
    completed = events[-1].result
    assert output == "resposta única\n"
    assert completed is not None
    assert "resposta única" not in completed.text


def test_nonzero_ping_completes_with_friendly_error(
    session: ShellSession, backend: FakePingBackend
) -> None:
    backend.result = backend.result.__class__(False, "tempo esgotado")
    events: list[CommandEvent] = []
    session.execute_events("ping 192.0.2.1", events.append)
    completed = events[-1].result
    assert completed is not None
    assert completed.is_error
    assert "Não houve resposta" in completed.text
    assert "tempo esgotado" not in completed.text


def test_varredura_outputs_host_before_completion_and_does_not_duplicate_it(
    session: ShellSession, backend: FakePingBackend, monkeypatch: pytest.MonkeyPatch
) -> None:
    release = threading.Event()
    host_output = threading.Event()
    events: list[CommandEvent] = []

    def controlled_probe(destination: str, timeout_seconds: float) -> bool:
        del timeout_seconds
        if destination == "192.0.2.1":
            return True
        release.wait(timeout=1)
        return False

    def receive(event: CommandEvent) -> None:
        events.append(event)
        if event.type is CommandEventType.OUTPUT and "192.0.2.1" in event.text:
            host_output.set()

    monkeypatch.setattr(backend, "probe", controlled_probe)
    worker = threading.Thread(
        target=lambda: session.execute_events("varredura 192.0.2.0/29", receive)
    )
    worker.start()
    assert host_output.wait(timeout=1)
    assert worker.is_alive()
    assert all(event.type is not CommandEventType.COMPLETED for event in events)
    release.set()
    worker.join(timeout=2)

    assert not worker.is_alive()
    output = "".join(event.text for event in events if event.type is CommandEventType.OUTPUT)
    completed = events[-1]
    assert "Iniciando varredura de 192.0.2.0/29" in output
    assert output.count("192.0.2.1") == 1
    assert completed.type is CommandEventType.COMPLETED
    assert completed.result is not None
    assert "192.0.2.1" not in completed.result.text
    assert "Verificados: 6/6" in completed.result.text
    assert "Responsivos: 1" in completed.result.text


def test_terminal_queue_preserves_stream_order_and_current_input(
    session: ShellSession,
) -> None:
    try:
        window = TerminalWindow(session)
    except tk.TclError:
        pytest.skip("tkinter sem display disponível")
    window._root.withdraw()
    try:
        window._input.insert("aju")
        window._render_input()
        window._results.put(CommandEvent.output("linha 1\n"))
        window._results.put(CommandEvent.output("linha 2\n"))
        window._results.put(CommandEvent.completed(CommandResult()))
        window._drain_results()

        transcript = window._terminal.get("1.0", "end-1c")
        assert transcript.index("linha 1") < transcript.index("linha 2")
        assert transcript.count("linha 1") == 1
        assert transcript.endswith("raber> aju")
        assert window._input.text == "aju"
    finally:
        window._close()
