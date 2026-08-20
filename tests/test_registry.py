import pytest

from rabershell.commands.catalog import build_registry
from rabershell.shell.models import CommandResult, CommandSpec
from rabershell.shell.registry import CommandRegistry


def _noop(runtime: object, args: tuple[str, ...]) -> CommandResult:
    del runtime, args
    return CommandResult()


def test_ping_is_same_spec_in_root_and_icmp() -> None:
    registry = build_registry()
    assert registry.resolve("ping", "root") is registry.resolve("ping", "icmp")


def test_sweep_is_same_spec_in_root_and_icmp() -> None:
    registry = build_registry()
    assert registry.resolve("sweep", "root") is registry.resolve("sweep", "icmp")


def test_alias_resolves_to_same_command() -> None:
    registry = build_registry()
    assert registry.resolve("ajuda", "root") is registry.resolve("help", "root")
    assert registry.resolve("ajuda", "root") is registry.resolve("?", "root")


def test_cancel_is_registered_as_control_command() -> None:
    registry = build_registry()
    command = registry.resolve("cancelar", "root")
    assert command is not None
    assert command.control_command


def test_duplicate_name_in_context_is_rejected() -> None:
    registry = CommandRegistry()
    spec = CommandSpec("teste", "Teste", "teste", ("teste",), _noop)
    registry.register(spec)
    with pytest.raises(ValueError, match="duplicado"):
        registry.register(spec)
