from __future__ import annotations

from rabershell.shell.session import ShellSession


def test_removed_commands_are_not_completed(session: ShellSession) -> None:
    result = session.complete("pi")
    assert result.line == "pi"
    assert result.matches == ()
    result = session.complete("ic")
    assert result.line == "ic"
    assert result.matches == ()


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
    assert {"ajuda", "varredura", "sweep"} <= set(result.matches)
    assert "ping" not in result.matches
    assert "icmp" not in result.matches


def test_varredura_is_completed_in_root(session: ShellSession) -> None:
    result = session.complete("var")
    assert result.line == "varredura"
    assert result.matches == ("varredura",)


def test_sweep_alias_remains_available_for_completion(session: ShellSession) -> None:
    result = session.complete("swe")
    assert result.line == "sweep"
    assert result.matches == ("sweep",)


def test_help_completes_canonical_command_argument(session: ShellSession) -> None:
    assert session.complete("ajuda var").line == "ajuda varredura"
    assert session.complete("ajuda lim").line == "ajuda limpar"
    assert session.complete("ajuda can").line == "ajuda cancelar"


def test_help_completes_alias_argument(session: ShellSession) -> None:
    result = session.complete("ajuda swe")
    assert result.line == "ajuda sweep"
    assert result.matches == ("sweep",)


def test_help_keeps_unknown_argument_unchanged(session: ShellSession) -> None:
    result = session.complete("ajuda inexistente")
    assert result.line == "ajuda inexistente"
    assert result.matches == ()


def test_help_displays_multiple_registry_matches_without_arbitrary_choice(
    session: ShellSession,
) -> None:
    result = session.complete("ajuda c")
    assert result.line == "ajuda c"
    assert result.matches == ("cancelar", "clear")


def test_help_never_completes_removed_commands(session: ShellSession) -> None:
    assert session.complete("ajuda pi").matches == ()
    assert session.complete("ajuda ic").matches == ()


def test_arguments_are_not_completed(session: ShellSession) -> None:
    result = session.complete("varredura 192.0")
    assert result.line == "varredura 192.0"
    assert result.matches == ()
