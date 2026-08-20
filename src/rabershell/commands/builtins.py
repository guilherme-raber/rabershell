from __future__ import annotations

from rabershell import __version__
from rabershell.shell.models import CommandResult, CommandRuntime, EventSink, ResultAction


def help_command(
    runtime: CommandRuntime, args: tuple[str, ...], event_sink: EventSink | None
) -> CommandResult:
    del event_sink
    if len(args) > 1:
        return CommandResult('Uso: ajuda [comando]', is_error=True)
    return runtime.render_help(args[0] if args else None)


def clear_command(
    runtime: CommandRuntime, args: tuple[str, ...], event_sink: EventSink | None
) -> CommandResult:
    del runtime, event_sink
    if args:
        return CommandResult('O comando "limpar" não recebe argumentos.', is_error=True)
    return CommandResult(action=ResultAction.CLEAR)


def version_command(
    runtime: CommandRuntime, args: tuple[str, ...], event_sink: EventSink | None
) -> CommandResult:
    del runtime, event_sink
    if args:
        return CommandResult('O comando "versao" não recebe argumentos.', is_error=True)
    return CommandResult(f"rabershell {__version__}")


def exit_command(
    runtime: CommandRuntime, args: tuple[str, ...], event_sink: EventSink | None
) -> CommandResult:
    del runtime, event_sink
    if args:
        return CommandResult('O comando "sair" não recebe argumentos.', is_error=True)
    return CommandResult("Encerrando o rabershell.", action=ResultAction.EXIT)


def enter_icmp_command(
    runtime: CommandRuntime, args: tuple[str, ...], event_sink: EventSink | None
) -> CommandResult:
    del event_sink
    if args:
        return CommandResult('Uso: icmp [comando]', is_error=True)
    description = runtime.enter_context("icmp")
    return CommandResult(
        f'{description}\nDigite "ajuda" para visualizar os comandos disponíveis.'
    )


def back_command(
    runtime: CommandRuntime, args: tuple[str, ...], event_sink: EventSink | None
) -> CommandResult:
    del event_sink
    if args:
        return CommandResult('O comando "voltar" não recebe argumentos.', is_error=True)
    runtime.leave_context()
    return CommandResult()


def ping_command(
    runtime: CommandRuntime, args: tuple[str, ...], event_sink: EventSink | None
) -> CommandResult:
    return runtime.run_ping(args, event_sink)


def sweep_command(
    runtime: CommandRuntime, args: tuple[str, ...], event_sink: EventSink | None
) -> CommandResult:
    del event_sink
    return runtime.run_sweep(args)


def cancel_command(
    runtime: CommandRuntime, args: tuple[str, ...], event_sink: EventSink | None
) -> CommandResult:
    del event_sink
    if args:
        return CommandResult('O comando "cancelar" não recebe argumentos.', is_error=True)
    if runtime.cancel_active_operation():
        return CommandResult("Cancelamento solicitado. Aguardando probes em andamento.")
    return CommandResult("Não há operação cancelável em andamento.")
