from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class ResultAction(Enum):
    NONE = "none"
    CLEAR = "clear"
    EXIT = "exit"


class CommandEventType(Enum):
    OUTPUT = "output"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class CommandResult:
    text: str = ""
    action: ResultAction = ResultAction.NONE
    is_error: bool = False


@dataclass(frozen=True, slots=True)
class CommandEvent:
    type: CommandEventType
    text: str = ""
    result: CommandResult | None = None

    @classmethod
    def output(cls, text: str) -> CommandEvent:
        return cls(CommandEventType.OUTPUT, text=text)

    @classmethod
    def completed(cls, result: CommandResult) -> CommandEvent:
        return cls(CommandEventType.COMPLETED, result=result)

    @classmethod
    def error(cls, text: str) -> CommandEvent:
        return cls(CommandEventType.ERROR, text=text)


EventSink = Callable[[CommandEvent], None]


@dataclass(frozen=True, slots=True)
class CompletionResult:
    line: str
    matches: tuple[str, ...] = ()


class CommandRuntime(Protocol):
    @property
    def current_context(self) -> str: ...

    def enter_context(self, name: str) -> str: ...

    def leave_context(self) -> None: ...

    def render_help(self, command_name: str | None = None) -> CommandResult: ...

    def run_ping(self, args: tuple[str, ...], event_sink: EventSink | None) -> CommandResult: ...

    def run_sweep(self, args: tuple[str, ...]) -> CommandResult: ...

    def cancel_active_operation(self) -> bool: ...


CommandHandler = Callable[[CommandRuntime, tuple[str, ...], EventSink | None], CommandResult]


@dataclass(frozen=True, slots=True)
class CommandSpec:
    name: str
    description: str
    usage: str
    examples: tuple[str, ...]
    handler: CommandHandler
    aliases: tuple[str, ...] = ()
    context: str = "root"
    root_exposed: bool = False
    global_command: bool = False
    control_command: bool = False

    @property
    def all_names(self) -> tuple[str, ...]:
        return (self.name, *self.aliases)
