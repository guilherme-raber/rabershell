from __future__ import annotations

import difflib
import os.path
import threading

from rabershell.core.ping import (
    HostResolutionError,
    InvalidDestinationError,
    PingEngine,
    PingExecutionTimeoutError,
    PingToolUnavailableError,
)
from rabershell.core.sweep import (
    InvalidNetworkError,
    NetworkTooLargeError,
    SweepEngine,
)
from rabershell.shell.models import CompletionResult, CommandResult, CommandRuntime, CommandSpec
from rabershell.shell.parser import ParseError, parse_line
from rabershell.shell.registry import CommandRegistry


class ShellSession(CommandRuntime):
    def __init__(
        self, registry: CommandRegistry, ping_engine: PingEngine, sweep_engine: SweepEngine
    ) -> None:
        self.registry = registry
        self.ping_engine = ping_engine
        self.sweep_engine = sweep_engine
        self._current_context = "root"
        self._operation_lock = threading.Lock()
        self._active_cancel_event: threading.Event | None = None

    @property
    def current_context(self) -> str:
        return self._current_context

    @property
    def prompt(self) -> str:
        suffix = "" if self.current_context == "root" else f"/{self.current_context}"
        return f"raber{suffix}>"

    def enter_context(self, name: str) -> str:
        if not self.registry.is_context(name):
            raise ValueError(f"Contexto desconhecido: {name}")
        self._current_context = name
        return self.registry.context_description(name)

    def leave_context(self) -> None:
        self._current_context = "root"

    def execute(self, line: str) -> CommandResult:
        try:
            tokens = parse_line(line)
        except ParseError as exc:
            return CommandResult(str(exc), is_error=True)
        if not tokens:
            return CommandResult()

        command_name, args = tokens[0], tokens[1:]
        command: CommandSpec | None
        if self.current_context == "root" and self.registry.is_context(command_name) and args:
            command = self.registry.resolve_in_context(args[0], command_name)
            if command is None:
                return self._unknown(args[0], command_name)
            args = args[1:]
        else:
            command = self.registry.resolve(command_name, self.current_context)
        if command is None:
            return self._unknown(command_name, self.current_context)

        return command.handler(self, args)

    def is_control_command(self, line: str) -> bool:
        try:
            tokens = parse_line(line)
        except ParseError:
            return False
        if not tokens:
            return False
        command = self.registry.resolve(tokens[0], self.current_context)
        return command is not None and command.control_command

    def complete(self, line: str) -> CompletionResult:
        trailing_space = bool(line) and line[-1].isspace()
        tokens = line.split()
        partial = "" if trailing_space else (tokens[-1] if tokens else "")

        completion_context: str | None = None
        if self.current_context != "root":
            if len(tokens) <= 1 and not trailing_space:
                completion_context = self.current_context
            elif not tokens:
                completion_context = self.current_context
        elif len(tokens) <= 1 and not trailing_space:
            completion_context = "root"
        elif len(tokens) == 1 and trailing_space and self.registry.is_context(tokens[0]):
            completion_context = tokens[0]
        elif len(tokens) == 2 and not trailing_space and self.registry.is_context(tokens[0]):
            completion_context = tokens[0]

        if completion_context is None:
            return CompletionResult(line)

        matches = tuple(
            name
            for name in self.registry.completion_names(completion_context)
            if name.startswith(partial)
        )
        if not matches:
            return CompletionResult(line)

        replacement = matches[0] if len(matches) == 1 else os.path.commonprefix(matches)
        completed_line = line[: len(line) - len(partial)] + replacement
        return CompletionResult(completed_line, matches)

    def _unknown(self, name: str, context: str) -> CommandResult:
        suggestions = difflib.get_close_matches(
            name, self.registry.suggestion_names(context), n=3, cutoff=0.6
        )
        text = f'Comando "{name}" não encontrado.'
        if suggestions:
            text += "\n\nVocê quis dizer:\n" + "\n".join(f"  {item}" for item in suggestions)
        text += '\n\nDigite "ajuda" para visualizar os comandos disponíveis.'
        return CommandResult(text, is_error=True)

    def render_help(self, command_name: str | None = None) -> CommandResult:
        if command_name:
            command = self.registry.resolve(command_name, self.current_context)
            if command is None and self.current_context == "root":
                command = self.registry.resolve_in_context(command_name, "icmp")
            if command is None:
                return self._unknown(command_name, self.current_context)
            aliases = f"\nAliases: {', '.join(command.aliases)}" if command.aliases else ""
            examples = "\n".join(f"  {example}" for example in command.examples)
            return CommandResult(
                f"{command.name.upper()}\n\n{command.description}.\n\nUso:\n"
                f"  {command.usage}{aliases}\n\nExemplos:\n{examples}"
            )

        commands = self.registry.visible_commands(self.current_context)
        width = max(len(command.usage) for command in commands)
        rows = "\n".join(
            f"  {command.usage:<{width}}  {command.description}" for command in commands
        )
        return CommandResult(
            "Comandos disponíveis:\n\n"
            f"{rows}\n\nDigite \"ajuda <comando>\" para mais informações.\n\n"
            "Exemplo:\n  ajuda ping"
        )

    def run_ping(self, args: tuple[str, ...]) -> CommandResult:
        parsed = self._parse_ping_arguments(args)
        if isinstance(parsed, CommandResult):
            return parsed
        destination, count = parsed
        try:
            report = self.ping_engine.execute(destination, count)
        except (InvalidDestinationError, HostResolutionError) as exc:
            return CommandResult(str(exc), is_error=True)
        except (PingToolUnavailableError, PingExecutionTimeoutError) as exc:
            return CommandResult(f"Não foi possível executar o ping: {exc}", is_error=True)
        heading = (
            f'Ping para "{report.destination}" concluído.'
            if report.successful
            else f'Não houve resposta bem-sucedida de "{report.destination}".'
        )
        output = report.output or "A ferramenta ping não produziu saída."
        return CommandResult(f"{heading}\n\n{output}", is_error=not report.successful)

    def run_sweep(self, args: tuple[str, ...]) -> CommandResult:
        if len(args) != 1:
            return CommandResult("Uso: sweep <rede-cidr>", is_error=True)

        cancel_event = threading.Event()
        with self._operation_lock:
            if self._active_cancel_event is not None:
                return CommandResult(
                    'Já existe um sweep em andamento. Use "cancelar" ou aguarde a conclusão.',
                    is_error=True,
                )
            self._active_cancel_event = cancel_event

        try:
            report = self.sweep_engine.execute(args[0], cancel_event)
        except (InvalidNetworkError, NetworkTooLargeError) as exc:
            return CommandResult(str(exc), is_error=True)
        except PingToolUnavailableError as exc:
            return CommandResult(f"Não foi possível executar o sweep: {exc}", is_error=True)
        finally:
            with self._operation_lock:
                if self._active_cancel_event is cancel_event:
                    self._active_cancel_event = None

        status = "cancelado" if report.cancelled else "concluído"
        hosts = (
            "\n".join(f"  {host}" for host in report.responsive_hosts)
            if report.responsive_hosts
            else "  Nenhum endereço respondeu."
        )
        return CommandResult(
            f"Sweep {status}.\n\n"
            f"Rede: {report.network}\n"
            f"Verificados: {report.checked_hosts}/{report.total_hosts}\n"
            f"Responderam: {len(report.responsive_hosts)}\n"
            f"Duração: {report.elapsed_seconds:.2f} s\n\n"
            f"Endereços responsivos:\n{hosts}"
        )

    def cancel_active_operation(self) -> bool:
        with self._operation_lock:
            if self._active_cancel_event is None:
                return False
            self._active_cancel_event.set()
            return True

    @staticmethod
    def _parse_ping_arguments(args: tuple[str, ...]) -> tuple[str, int] | CommandResult:
        usage = "Uso: ping <destino> [--quantidade N]"
        if not args:
            return CommandResult(f"Destino obrigatório.\n\n{usage}", is_error=True)
        destination = args[0]
        count = 4
        remaining = list(args[1:])
        if remaining:
            if len(remaining) != 2 or remaining[0] not in {"--quantidade", "--count"}:
                return CommandResult(usage, is_error=True)
            try:
                count = int(remaining[1])
            except ValueError:
                return CommandResult(
                    "A quantidade deve ser um número inteiro entre 1 e 20.", is_error=True
                )
            if not 1 <= count <= 20:
                return CommandResult("A quantidade deve estar entre 1 e 20.", is_error=True)
        return destination, count
