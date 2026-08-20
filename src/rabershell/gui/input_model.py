from __future__ import annotations


class TerminalInputModel:
    """Estado editável da linha atual, independente dos widgets tkinter."""

    def __init__(self) -> None:
        self.text = ""
        self.cursor = 0
        self._history: list[str] = []
        self._history_index = 0
        self._draft = ""

    def insert(self, value: str) -> None:
        if not value:
            return
        self.text = self.text[: self.cursor] + value + self.text[self.cursor :]
        self.cursor += len(value)

    def paste(self, value: str) -> bool:
        non_empty_lines = [line for line in value.splitlines() if line.strip()]
        if len(non_empty_lines) > 1:
            return False
        self.insert(non_empty_lines[0] if non_empty_lines else "")
        return True

    def backspace(self) -> None:
        if self.cursor == 0:
            return
        self.text = self.text[: self.cursor - 1] + self.text[self.cursor :]
        self.cursor -= 1

    def delete(self) -> None:
        if self.cursor >= len(self.text):
            return
        self.text = self.text[: self.cursor] + self.text[self.cursor + 1 :]

    def move_left(self) -> None:
        self.cursor = max(0, self.cursor - 1)

    def move_right(self) -> None:
        self.cursor = min(len(self.text), self.cursor + 1)

    def move_home(self) -> None:
        self.cursor = 0

    def move_end(self) -> None:
        self.cursor = len(self.text)

    def replace(self, value: str) -> None:
        self.text = value
        self.cursor = len(value)

    def submit(self) -> str:
        command = self.text.strip()
        if command:
            self._history.append(command)
        self._history_index = len(self._history)
        self._draft = ""
        self.replace("")
        return command

    def history_up(self) -> None:
        if not self._history or self._history_index == 0:
            return
        if self._history_index == len(self._history):
            self._draft = self.text
        self._history_index -= 1
        self.replace(self._history[self._history_index])

    def history_down(self) -> None:
        if self._history_index >= len(self._history):
            return
        self._history_index += 1
        value = (
            self._draft
            if self._history_index == len(self._history)
            else self._history[self._history_index]
        )
        self.replace(value)
