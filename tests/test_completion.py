from __future__ import annotations

from rabershell.shell.session import ShellSession


def test_unique_root_completion(session: ShellSession) -> None:
    result = session.complete("pi")
    assert result.line == "ping"
    assert result.matches == ("ping",)


def test_alias_is_considered_for_completion(session: ShellSession) -> None:
    result = session.complete("he")
    assert result.line == "help"
    assert result.matches == ("help",)


def test_multiple_matches_are_not_chosen_arbitrarily(session: ShellSession) -> None:
    result = session.complete("c")
    assert result.line == "c"
    assert result.matches == ("cancelar", "clear")


def test_no_completion_keeps_input_unchanged(session: ShellSession) -> None:
    result = session.complete("naoexiste")
    assert result.line == "naoexiste"
    assert result.matches == ()


def test_empty_root_completion_uses_visible_registry_names(session: ShellSession) -> None:
    result = session.complete("")
    assert {"ajuda", "icmp", "ping", "sweep"} <= set(result.matches)


def test_contextual_completion_uses_icmp_commands(session: ShellSession) -> None:
    session.execute("icmp")
    result = session.complete("sw")
    assert result.line == "sweep"
    assert result.matches == ("sweep",)


def test_explicit_context_completion_uses_subcommands(session: ShellSession) -> None:
    result = session.complete("icmp sw")
    assert result.line == "icmp sweep"
    assert result.matches == ("sweep",)


def test_arguments_are_not_completed(session: ShellSession) -> None:
    result = session.complete("ping 1.1")
    assert result.line == "ping 1.1"
    assert result.matches == ()

