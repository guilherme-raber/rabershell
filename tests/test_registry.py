import pytest

from rabershell.commands.catalog import build_registry
from rabershell.shell.models import CommandResult, CommandSpec, EventSink
from rabershell.shell.registry import CommandRegistry


def _noop(
    runtime: object, args: tuple[str, ...], event_sink: EventSink | None
) -> CommandResult:
    del runtime, args, event_sink
    return CommandResult()


def test_removed_ping_and_icmp_are_not_registered() -> None:
    registry = build_registry()
    assert registry.resolve("ping", "root") is None
    assert registry.resolve("icmp", "root") is None
    assert not registry.is_context("icmp")


def test_varredura_and_sweep_alias_share_root_spec_and_handler() -> None:
    registry = build_registry()
    canonical = registry.resolve("varredura", "root")
    assert canonical is not None
    assert canonical is registry.resolve("sweep", "root")


def test_alias_resolves_to_same_command() -> None:
    registry = build_registry()
    assert registry.resolve("ajuda", "root") is registry.resolve("help", "root")
    assert registry.resolve("ajuda", "root") is registry.resolve("?", "root")


def test_cancel_is_registered_as_control_command() -> None:
    registry = build_registry()
    command = registry.resolve("cancelar", "root")
    assert command is not None
    assert command.control_command


def test_generic_context_infrastructure_remains_available() -> None:
    registry = CommandRegistry()
    registry.add_context("futuro", "Contexto futuro.")
    spec = CommandSpec(
        "teste", "Teste", "teste", ("teste",), _noop, context="futuro"
    )
    registry.register(spec)
    assert registry.is_context("futuro")
    assert registry.resolve_in_context("teste", "futuro") is spec


def test_duplicate_name_in_context_is_rejected() -> None:
    registry = CommandRegistry()
    spec = CommandSpec("teste", "Teste", "teste", ("teste",), _noop)
    registry.register(spec)
    with pytest.raises(ValueError, match="duplicado"):
        registry.register(spec)
