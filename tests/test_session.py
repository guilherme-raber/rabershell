from __future__ import annotations

import threading

import pytest

from conftest import FakeSweepBackend
from rabershell.shell.models import CommandResult, ResultAction
from rabershell.shell.session import ShellSession


@pytest.mark.parametrize("command", ["ajuda", "help", "?"])
def test_help_aliases(session: ShellSession, command: str) -> None:
    result = session.execute(command)
    assert "Comandos disponíveis" in result.text
    assert "varredura <rede-cidr>" in result.text
    assert "ping" not in result.text
    assert "icmp" not in result.text


def test_command_help_comes_from_registry(session: ShellSession) -> None:
    result = session.execute("ajuda varredura")
    assert "VARREDURA" in result.text
    assert "varredura <rede-cidr>" in result.text


@pytest.mark.parametrize("command", ["limpar", "clear"])
def test_clear_aliases(session: ShellSession, command: str) -> None:
    assert session.execute(command).action is ResultAction.CLEAR


@pytest.mark.parametrize("command", ["versao", "version"])
def test_version_aliases(session: ShellSession, command: str) -> None:
    assert session.execute(command).text.startswith("rabershell ")


@pytest.mark.parametrize("command", ["sair", "exit"])
def test_exit_aliases(session: ShellSession, command: str) -> None:
    assert session.execute(command).action is ResultAction.EXIT


def test_removed_ping_and_icmp_are_unknown(session: ShellSession) -> None:
    assert session.prompt == "raber>"
    assert session.execute("ping 127.0.0.1").is_error
    assert session.execute("icmp").is_error
    assert session.prompt == "raber>"


def test_varredura_help_uses_canonical_name_and_reports_alias(
    session: ShellSession,
) -> None:
    result = session.execute("ajuda varredura")
    assert result.text.startswith("VARREDURA")
    assert "varredura <rede-cidr>" in result.text
    assert "Aliases: sweep" in result.text


def test_unknown_removed_command_does_not_suggest_ping(session: ShellSession) -> None:
    result = session.execute("pign")
    assert result.is_error
    assert 'Comando "pign" não encontrado' in result.text
    assert "Você quis dizer" not in result.text


def test_empty_input_is_ignored(session: ShellSession) -> None:
    assert session.execute("   ").text == ""


def test_varredura_uses_sweep_engine(
    session: ShellSession, backend: FakeSweepBackend
) -> None:
    result = session.execute("varredura 192.0.2.0/30")
    assert not result.is_error
    assert "Verificados: 2/2" in result.text
    assert {host for host, _ in backend.probe_calls} == {"192.0.2.1", "192.0.2.2"}


def test_varredura_validates_arguments_and_safe_limit(session: ShellSession) -> None:
    assert session.execute("varredura").is_error
    result = session.execute("varredura 10.0.0.0/19")
    assert result.is_error
    assert "4.096" in result.text


def test_sweep_alias_keeps_existing_behavior(
    session: ShellSession, backend: FakeSweepBackend
) -> None:
    result = session.execute("sweep 192.0.2.0/30")
    assert not result.is_error
    assert {host for host, _ in backend.probe_calls} == {"192.0.2.1", "192.0.2.2"}


def test_cancel_without_active_operation_is_informative(session: ShellSession) -> None:
    assert session.is_control_command("cancelar")
    assert not session.is_control_command("varredura 127.0.0.1/32")
    result = session.execute("cancelar")
    assert not result.is_error
    assert "Não há operação" in result.text


def test_cancel_command_stops_active_sweep(
    session: ShellSession, backend: FakeSweepBackend, monkeypatch: pytest.MonkeyPatch
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
        target=lambda: results.append(session.execute("varredura 192.0.2.0/24"))
    )
    worker.start()
    assert started.wait(timeout=1)
    cancel_result = session.execute("cancelar")
    release.set()
    worker.join(timeout=2)

    assert "Cancelamento solicitado" in cancel_result.text
    assert not worker.is_alive()
    assert "Varredura cancelada" in results[0].text
