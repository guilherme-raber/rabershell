from __future__ import annotations

import tkinter as tk
from concurrent.futures import Future, ThreadPoolExecutor
from tkinter import font as tkfont

from rabershell import __version__
from rabershell.shell.models import CommandResult, ResultAction
from rabershell.shell.session import ShellSession


class TerminalWindow:
    def __init__(self, session: ShellSession) -> None:
        self._session = session
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="rabershell")
        self._control_executor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="rabershell-control"
        )
        self._closing = False
        self._history: list[str] = []
        self._history_index = 0

        self._root = tk.Tk()
        self._root.title(f"rabershell {__version__}")
        self._root.geometry("900x580")
        self._root.minsize(620, 380)
        self._root.configure(bg="#101418")
        self._root.protocol("WM_DELETE_WINDOW", self._close)

        mono = tkfont.Font(family="Consolas", size=11)
        self._output = tk.Text(
            self._root, bg="#101418", fg="#d7e0e7", insertbackground="#d7e0e7",
            font=mono, relief="flat", padx=14, pady=14, state="disabled", wrap="word",
        )
        scrollbar = tk.Scrollbar(self._root, command=self._output.yview)
        self._output.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self._output.pack(fill="both", expand=True)

        input_frame = tk.Frame(self._root, bg="#192027", padx=12, pady=10)
        input_frame.pack(fill="x")
        self._prompt = tk.Label(input_frame, bg="#192027", fg="#6ee7b7", font=mono)
        self._prompt.pack(side="left")
        self._entry = tk.Entry(
            input_frame, bg="#192027", fg="#f1f5f9", insertbackground="#f1f5f9",
            font=mono, relief="flat", disabledbackground="#192027",
        )
        self._entry.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self._entry.bind("<Return>", self._submit)
        self._entry.bind("<Up>", self._history_up)
        self._entry.bind("<Down>", self._history_down)

        self._write(
            "rabershell\nToolkit de diagnóstico de redes\n\n"
            'Digite "ajuda" ou "?" para visualizar os comandos disponíveis.\n'
        )
        self._refresh_prompt()
        self._entry.focus_set()

    def run(self) -> None:
        self._root.mainloop()

    def _submit(self, event: tk.Event[tk.Misc] | None = None) -> str:
        del event
        line = self._entry.get().strip()
        self._entry.delete(0, "end")
        if not line:
            return "break"
        self._history.append(line)
        self._history_index = len(self._history)
        self._write(f"\n{self._session.prompt} {line}\n")
        executor = (
            self._control_executor if self._session.is_control_command(line) else self._executor
        )
        future = executor.submit(self._session.execute, line)
        future.add_done_callback(self._command_finished)
        self._entry.focus_set()
        return "break"

    def _command_finished(self, future: Future[CommandResult]) -> None:
        if self._closing:
            return
        try:
            result = future.result()
        except Exception as exc:  # boundary: impede que falhas encerrem a GUI
            result = CommandResult(f"Erro interno inesperado: {exc}", is_error=True)
        self._root.after(0, self._apply_result, result)

    def _apply_result(self, result: CommandResult) -> None:
        if self._closing:
            return
        if result.action is ResultAction.CLEAR:
            self._output.configure(state="normal")
            self._output.delete("1.0", "end")
            self._output.configure(state="disabled")
        elif result.text:
            self._write(result.text + "\n")
        if result.action is ResultAction.EXIT:
            self._close()
            return
        self._refresh_prompt()
        self._entry.focus_set()

    def _write(self, text: str) -> None:
        self._output.configure(state="normal")
        self._output.insert("end", text)
        self._output.see("end")
        self._output.configure(state="disabled")

    def _refresh_prompt(self) -> None:
        self._prompt.configure(text=self._session.prompt)

    def _history_up(self, event: tk.Event[tk.Misc]) -> str:
        del event
        if self._history and self._history_index > 0:
            self._history_index -= 1
            self._set_entry(self._history[self._history_index])
        return "break"

    def _history_down(self, event: tk.Event[tk.Misc]) -> str:
        del event
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self._set_entry(self._history[self._history_index])
        elif self._history_index < len(self._history):
            self._history_index = len(self._history)
            self._set_entry("")
        return "break"

    def _set_entry(self, value: str) -> None:
        self._entry.delete(0, "end")
        self._entry.insert(0, value)

    def _close(self) -> None:
        if self._closing:
            return
        self._closing = True
        self._session.cancel_active_operation()
        self._executor.shutdown(wait=False, cancel_futures=True)
        self._control_executor.shutdown(wait=False, cancel_futures=True)
        self._root.destroy()
