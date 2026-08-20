from __future__ import annotations

from collections.abc import Iterable

from rabershell.shell.models import CommandSpec


class CommandRegistry:
    """Catálogo único de comandos, aliases e exposição por contexto."""

    def __init__(self) -> None:
        self._commands: list[CommandSpec] = []
        self._contexts: dict[str, str] = {}

    def add_context(self, name: str, description: str) -> None:
        if name in self._contexts:
            raise ValueError(f"Contexto duplicado: {name}")
        self._contexts[name] = description

    def register(self, command: CommandSpec) -> None:
        for existing in self._commands:
            duplicate_names = set(existing.all_names) & set(command.all_names)
            if existing.context == command.context and duplicate_names:
                raise ValueError(f"Nome ou alias duplicado no contexto {command.context}")
        self._commands.append(command)

    def is_context(self, name: str) -> bool:
        return name in self._contexts

    def context_description(self, name: str) -> str:
        return self._contexts[name]

    def resolve(self, name: str, context: str) -> CommandSpec | None:
        for command in self._commands:
            visible = (
                command.context == context
                or command.global_command
                or (context == "root" and command.root_exposed)
            )
            if visible and name in command.all_names:
                return command
        return None

    def resolve_in_context(self, name: str, context: str) -> CommandSpec | None:
        for command in self._commands:
            if command.context == context and name in command.all_names:
                return command
        return None

    def visible_commands(self, context: str) -> tuple[CommandSpec, ...]:
        commands = (
            command
            for command in self._commands
            if command.context == context
            or command.global_command
            or (context == "root" and command.root_exposed)
        )
        return tuple(self._unique(commands))

    def suggestion_names(self, context: str) -> tuple[str, ...]:
        names = {name for command in self.visible_commands(context) for name in command.all_names}
        if context == "root":
            names.update(self._contexts)
        return tuple(sorted(names))

    def completion_names(self, context: str) -> tuple[str, ...]:
        return self.suggestion_names(context)

    @staticmethod
    def _unique(commands: Iterable[CommandSpec]) -> Iterable[CommandSpec]:
        seen: set[tuple[str, str]] = set()
        for command in commands:
            key = (command.context, command.name)
            if key not in seen:
                seen.add(key)
                yield command
