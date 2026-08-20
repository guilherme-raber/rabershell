from __future__ import annotations

import queue
import tkinter as tk
from concurrent.futures import Future, ThreadPoolExecutor
from tkinter import font as tkfont

from rabershell import __version__
from rabershell.gui.input_model import TerminalInputModel
from rabershell.shell.models import CommandResult, ResultAction
from rabershell.shell.session import ShellSession


class TerminalWindow:
    def __init__(self, session: ShellSession) -> None:
        self._session = session
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="rabershell")
        self._control_executor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="rabershell-control"
        )
        self._results: queue.SimpleQueue[CommandResult] = queue.SimpleQueue()
        self._input = TerminalInputModel()
        self._closing = False

        self._root = tk.Tk()
        self._root.title(f"rabershell {__version__}")
        self._root.geometry("900x580")
        self._root.minsize(620, 380)
        self._root.configure(bg="#101418")
        self._root.protocol("WM_DELETE_WINDOW", self._close)

        mono = tkfont.Font(family="Consolas", size=11)
        self._terminal = tk.Text(
            self._root,
            bg="#101418",
            fg="#d7e0e7",
            insertbackground="#f1f5f9",
            insertwidth=2,
            font=mono,
            relief="flat",
            padx=14,
            pady=14,
            wrap="word",
            undo=False,
        )
        scrollbar = tk.Scrollbar(self._root, command=self._terminal.yview)
        self._terminal.configure(yscrollcommand=scrollbar.set)
        self._terminal.tag_configure("prompt", foreground="#6ee7b7")
        scrollbar.pack(side="right", fill="y")
        self._terminal.pack(fill="both", expand=True)

        self._prompt_start = "prompt_start"
        self._input_start = "input_start"
        self._bind_terminal_events()
        self._terminal.insert(
            "end",
            "rabershell\nToolkit de diagnóstico de redes\n\n"
            'Digite "ajuda" ou "?" para visualizar os comandos disponíveis.\n\n',
        )
        self._show_prompt()
        self._terminal.focus_set()
        self._root.after(50, self._drain_results)

    def run(self) -> None:
        self._root.mainloop()

    def _bind_terminal_events(self) -> None:
        self._terminal.bind("<KeyPress>", self._on_keypress)
        self._terminal.bind("<ButtonRelease-1>", self._on_mouse_release)
        self._terminal.bind("<Control-v>", self._paste)
        self._terminal.bind("<Control-V>", self._paste)
        self._terminal.bind("<<Paste>>", self._paste)
        self._terminal.bind("<Button-2>", self._paste)
        self._terminal.bind("<ButtonRelease-2>", lambda event: "break")
        self._terminal.bind("<Control-x>", lambda event: "break")
        self._terminal.bind("<Control-X>", lambda event: "break")

    def _on_keypress(self, event: tk.Event[tk.Misc]) -> str | None:
        state = event.state if isinstance(event.state, int) else 0
        control_pressed = bool(state & 0x4)
        key = event.keysym

        if control_pressed and key.lower() == "c":
            return None
        if control_pressed and key.lower() == "a":
            self._terminal.tag_add("sel", "1.0", "end-1c")
            return "break"
        if control_pressed and not (event.char and event.char.isprintable()):
            return "break"

        actions = {
            "BackSpace": self._input.backspace,
            "Delete": self._input.delete,
            "Home": self._input.move_home,
            "End": self._input.move_end,
            "Left": self._input.move_left,
            "Right": self._input.move_right,
            "Up": self._input.history_up,
            "Down": self._input.history_down,
        }
        if key in actions:
            actions[key]()
            self._render_input()
            return "break"
        if key in {"Return", "KP_Enter"}:
            self._submit()
            return "break"
        if key == "Tab":
            self._autocomplete()
            return "break"
        if event.char and event.char.isprintable():
            self._input.insert(event.char)
            self._render_input()
        return "break"

    def _on_mouse_release(self, event: tk.Event[tk.Misc]) -> None:
        index = self._terminal.index(f"@{event.x},{event.y}")
        if self._terminal.compare(index, ">=", self._input_start):
            count = self._terminal.count(self._input_start, index, "chars")
            self._input.cursor = min(len(self._input.text), int(count[0]) if count else 0)
            self._place_cursor()

    def _paste(self, event: tk.Event[tk.Misc] | None = None) -> str:
        del event
        try:
            value = self._root.clipboard_get()
        except tk.TclError:
            return "break"
        self._input.paste(value)
        self._render_input()
        return "break"

    def _submit(self) -> None:
        self._render_input()
        self._terminal.insert("end-1c", "\n")
        command = self._input.submit()
        self._show_prompt()
        if not command:
            return
        executor = (
            self._control_executor
            if self._session.is_control_command(command)
            else self._executor
        )
        future = executor.submit(self._session.execute, command)
        future.add_done_callback(self._command_finished)

    def _command_finished(self, future: Future[CommandResult]) -> None:
        if self._closing:
            return
        try:
            result = future.result()
        except Exception as exc:  # boundary: impede que falhas encerrem a GUI
            result = CommandResult(f"Erro interno inesperado: {exc}", is_error=True)
        self._results.put(result)

    def _drain_results(self) -> None:
        if self._closing:
            return
        while True:
            try:
                result = self._results.get_nowait()
            except queue.Empty:
                break
            self._apply_result(result)
            if self._closing:
                return
        self._root.after(50, self._drain_results)

    def _apply_result(self, result: CommandResult) -> None:
        self._remove_active_prompt()
        if result.action is ResultAction.CLEAR:
            self._terminal.delete("1.0", "end")
        elif result.text:
            self._terminal.insert("end", result.text + "\n")
        if result.action is ResultAction.EXIT:
            self._close()
            return
        self._show_prompt()

    def _autocomplete(self) -> None:
        completion = self._session.complete(self._input.text)
        self._input.replace(completion.line)
        if len(completion.matches) > 1:
            self._render_input()
            self._terminal.insert("end-1c", "\n")
            self._terminal.insert("end", "    ".join(completion.matches) + "\n")
            self._show_prompt()
        else:
            self._render_input()

    def _show_prompt(self) -> None:
        self._terminal.mark_set(self._prompt_start, "end-1c")
        self._terminal.mark_gravity(self._prompt_start, "left")
        self._terminal.insert("end-1c", self._session.prompt + " ", "prompt")
        self._terminal.mark_set(self._input_start, "end-1c")
        self._terminal.mark_gravity(self._input_start, "left")
        self._terminal.insert("end-1c", self._input.text)
        self._place_cursor()

    def _remove_active_prompt(self) -> None:
        self._terminal.delete(self._prompt_start, "end-1c")

    def _render_input(self) -> None:
        self._terminal.tag_remove("sel", "1.0", "end")
        self._terminal.delete(self._input_start, "end-1c")
        self._terminal.insert("end-1c", self._input.text)
        self._place_cursor()

    def _place_cursor(self) -> None:
        self._terminal.mark_set("insert", f"{self._input_start}+{self._input.cursor}c")
        self._terminal.see("insert")
        self._terminal.focus_set()

    def _close(self) -> None:
        if self._closing:
            return
        self._closing = True
        self._session.cancel_active_operation()
        self._executor.shutdown(wait=False, cancel_futures=True)
        self._control_executor.shutdown(wait=False, cancel_futures=True)
        self._root.destroy()
