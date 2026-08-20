from __future__ import annotations

import socket
import threading

import pytest

from conftest import FakePingBackend
from rabershell.shell.models import CommandResult, ResultAction
from rabershell.shell.session import ShellSession


@pytest.mark.parametrize("command", ["ajuda", "help", "?"])
def test_help_aliases(session: ShellSession, command: str) -> None:
    result = session.execute(command)
    assert "Comandos disponíveis" in result.text
    assert "ping <destino>" in result.text


def test_command_help_comes_from_registry(session: ShellSession) -> None:
    result = session.execute("ajuda ping")
    assert "PING" in result.text
    assert "ping <destino> [--quantidade N]" in result.text


@pytest.mark.parametrize("command", ["limpar", "clear"])
def test_clear_aliases(session: ShellSession, command: str) -> None:
    assert session.execute(command).action is ResultAction.CLEAR


@pytest.mark.parametrize("command", ["versao", "version"])
def test_version_aliases(session: ShellSession, command: str) -> None:
    assert session.execute(command).text.startswith("rabershell ")


@pytest.mark.parametrize("command", ["sair", "exit"])
def test_exit_aliases(session: ShellSession, command: str) -> None:
    assert session.execute(command).action is ResultAction.EXIT


def test_icmp_context_entry_and_back_aliases(session: ShellSession) -> None:
    assert session.prompt == "raber>"
    assert "Contexto ICMP" in session.execute("icmp").text
    assert session.prompt == "raber/icmp>"
    session.execute("back")
    assert session.prompt == "raber>"
    session.execute("icmp")
    session.execute("voltar")
    assert session.prompt == "raber>"


def test_icmp_help_is_contextual(session: ShellSession) -> None:
    session.execute("icmp")
    result = session.execute("ajuda")
    assert "ping <destino>" in result.text
    assert "voltar" in result.text
    assert "sweep <rede-cidr>" in result.text


def test_unknown_command_suggests_ping(session: ShellSession) -> None:
    result = session.execute("pign")
    assert result.is_error
    assert 'Comando "pign" não encontrado' in result.text
    assert "ping" in result.text


def test_empty_input_is_ignored(session: ShellSession) -> None:
    assert session.execute("   ").text == ""


def test_ping_requires_destination(session: ShellSession) -> None:
    result = session.execute("ping")
    assert result.is_error
    assert "Destino obrigatório" in result.text


def test_ping_rejects_bad_count(session: ShellSession) -> None:
    assert session.execute("ping 127.0.0.1 --count nope").is_error
    assert session.execute("ping 127.0.0.1 --quantidade 21").is_error


@pytest.mark.parametrize(
    "commands",
    [
        ("ping 127.0.0.1 --count 2",),
        ("icmp ping 127.0.0.1 --quantidade 2",),
        ("icmp", "ping 127.0.0.1 --count 2"),
    ],
)
def test_all_ping_routes_use_same_backend(
    session: ShellSession, backend: FakePingBackend, commands: tuple[str, ...]
) -> None:
    for command in commands:
        result = session.execute(command)
    assert not result.is_error
    assert backend.calls == [("127.0.0.1", 2)]


def test_syntactically_valid_hostname_fails_as_resolution_not_validation(
    session: ShellSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_resolution(host: str, port: None) -> None:
        del host, port
        raise socket.gaierror

    monkeypatch.setattr(socket, "getaddrinfo", fail_resolution)
    result = session.execute("ping valid.example")
    assert result.is_error
    assert "resolver o hostname" in result.text
    assert "Destino inválido" not in result.text


def test_invalid_destination_is_rejected_before_resolution(session: ShellSession) -> None:
    result = session.execute("ping bad_host!")
    assert result.is_error
    assert "Destino inválido" in result.text


@pytest.mark.parametrize(
    "commands",
    [
        ("sweep 192.0.2.0/30",),
        ("icmp sweep 192.0.2.0/30",),
        ("icmp", "sweep 192.0.2.0/30"),
    ],
)
def test_all_sweep_routes_use_same_engine(
    session: ShellSession, backend: FakePingBackend, commands: tuple[str, ...]
) -> None:
    for command in commands:
        result = session.execute(command)
    assert not result.is_error
    assert "Verificados: 2/2" in result.text
    assert {host for host, _ in backend.probe_calls} == {"192.0.2.1", "192.0.2.2"}


def test_sweep_validates_arguments_and_safe_limit(session: ShellSession) -> None:
    assert session.execute("sweep").is_error
    result = session.execute("sweep 10.0.0.0/19")
    assert result.is_error
    assert "4.096" in result.text


def test_cancel_without_active_operation_is_informative(session: ShellSession) -> None:
    assert session.is_control_command("cancelar")
    assert not session.is_control_command("ping 127.0.0.1")
    result = session.execute("cancelar")
    assert not result.is_error
    assert "Não há operação" in result.text


def test_cancel_command_stops_active_sweep(
    session: ShellSession, backend: FakePingBackend, monkeypatch: pytest.MonkeyPatch
) -> None:
    started = threading.Event()
    release = threading.Event()

    def blocking_probe(destination: str, timeout_seconds: float) -> bool:
        del destination, timeout_seconds
        started.set()
        release.wait(timeout=1)
        return False

    monkeypatch.setattr(backend, "probe", blocking_probe)
    results: list[CommandResult] = []
    worker = threading.Thread(
        target=lambda: results.append(session.execute("sweep 192.0.2.0/24"))
    )
    worker.start()
    assert started.wait(timeout=1)
    cancel_result = session.execute("cancelar")
    release.set()
    worker.join(timeout=2)

    assert "Cancelamento solicitado" in cancel_result.text
    assert not worker.is_alive()
    assert "Sweep cancelado" in results[0].text
