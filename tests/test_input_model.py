from rabershell.gui.input_model import TerminalInputModel


def test_backspace_and_delete_never_cross_input_start() -> None:
    model = TerminalInputModel()
    model.backspace()
    model.delete()
    assert model.text == ""
    assert model.cursor == 0


def test_home_end_and_editing_stay_inside_current_input() -> None:
    model = TerminalInputModel()
    model.insert("ping")
    model.move_home()
    model.backspace()
    model.insert("x")
    assert model.text == "xping"
    assert model.cursor == 1
    model.move_end()
    model.insert("!")
    assert model.text == "xping!"


def test_empty_enter_does_not_create_history_entry() -> None:
    model = TerminalInputModel()
    assert model.submit() == ""
    model.history_up()
    assert model.text == ""


def test_history_navigation_preserves_current_draft() -> None:
    model = TerminalInputModel()
    model.insert("ping 1.1.1.1")
    model.submit()
    model.insert("ajuda")
    model.submit()
    model.insert("rascunho")

    model.history_up()
    assert model.text == "ajuda"
    model.history_up()
    assert model.text == "ping 1.1.1.1"
    model.history_down()
    assert model.text == "ajuda"
    model.history_down()
    assert model.text == "rascunho"


def test_multiline_paste_is_rejected_without_changing_draft() -> None:
    model = TerminalInputModel()
    model.insert("ping ")
    assert not model.paste("1.1.1.1\r\najuda\nversao")
    assert model.text == "ping "


def test_single_non_empty_line_with_empty_lines_is_accepted() -> None:
    model = TerminalInputModel()
    assert model.paste("\r\nping 1.1.1.1\n\n")
    assert model.text == "ping 1.1.1.1"
