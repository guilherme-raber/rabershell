from __future__ import annotations

import tkinter as tk
from collections.abc import Iterator

import pytest

from rabershell.gui.terminal import TerminalWindow
from rabershell.shell.models import CommandEvent
from rabershell.shell.session import ShellSession


@pytest.fixture
def window(session: ShellSession) -> Iterator[TerminalWindow]:
    try:
        terminal = TerminalWindow(session)
    except tk.TclError:
        pytest.skip("tkinter sem display disponível")
    terminal._root.withdraw()
    yield terminal
    terminal._close()


def test_copy_selection_preserves_terminal_and_input(window: TerminalWindow) -> None:
    window._input.insert("rascunho")
    window._render_input()
    before = window._terminal.get("1.0", "end-1c")
    window._terminal.tag_add("sel", "1.0", "1.10")

    assert window._copy_selection() == "break"

    assert window._root.clipboard_get() == before[:10]
    assert window._terminal.get("1.0", "end-1c") == before
    assert window._input.text == "rascunho"


def test_external_paste_after_history_click_only_changes_active_input(
    window: TerminalWindow,
) -> None:
    protected_before = window._terminal.get("1.0", window._input_start)
    window._terminal.mark_set("insert", "1.0")
    window._terminal.tag_add("sel", "1.0", "1.10")
    window._root.clipboard_clear()
    window._root.clipboard_append("ping 1.1.1.1")

    assert window._paste_clipboard() == "break"

    assert window._terminal.get("1.0", window._input_start) == protected_before
    assert window._input.text == "ping 1.1.1.1"
    assert window._terminal.index("insert") == window._terminal.index("end-1c")


def test_multiline_clipboard_is_rejected_and_preserves_draft(
    window: TerminalWindow,
) -> None:
    window._input.insert("ping 192.")
    window._render_input()
    window._root.clipboard_clear()
    window._root.clipboard_append("ping 1.1.1.1\r\najuda\nversao")

    window._paste_clipboard()

    transcript = window._terminal.get("1.0", "end-1c")
    assert "Colagem com múltiplas linhas não é suportada" in transcript
    assert window._input.text == "ping 192."
    assert transcript.endswith("raber> ping 192.")
    assert window._session.prompt == "raber>"


def test_all_paste_sources_share_multiline_policy(window: TerminalWindow) -> None:
    for value in ("ping 1.1.1.1\najuda", "varredura 127.0.0.1/32\r\nversao"):
        before = window._input.text
        assert window._paste_value(value) == "break"
        assert window._input.text == before


def test_streaming_preserves_selected_history_and_current_input(
    window: TerminalWindow,
) -> None:
    window._input.insert("aju")
    window._render_input()
    window._terminal.tag_add("sel", "1.0", "1.10")
    selected = window._terminal.get("sel.first", "sel.last")

    window._apply_event(CommandEvent.output("resposta incremental\n"))

    assert window._terminal.get("sel.first", "sel.last") == selected
    assert window._input.text == "aju"
    assert window._terminal.get("1.0", "end-1c").endswith("raber> aju")
