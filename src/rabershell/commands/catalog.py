from __future__ import annotations

from rabershell.commands.builtins import (
    cancel_command,
    clear_command,
    exit_command,
    help_command,
    sweep_command,
    version_command,
)
from rabershell.shell.models import CommandSpec
from rabershell.shell.registry import CommandRegistry


def build_registry() -> CommandRegistry:
    registry = CommandRegistry()
    registry.register(
        CommandSpec(
            "ajuda", "Exibe ajuda contextual", "ajuda [comando]",
            ("ajuda", "ajuda varredura"), help_command, aliases=("help", "?"),
            global_command=True,
        )
    )
    registry.register(
        CommandSpec(
            "limpar", "Limpa o terminal", "limpar", ("limpar",), clear_command,
            aliases=("clear",), global_command=True,
        )
    )
    registry.register(
        CommandSpec(
            "versao", "Exibe a versão", "versao", ("versao",), version_command,
            aliases=("version",), global_command=True,
        )
    )
    registry.register(
        CommandSpec(
            "sair", "Encerra o rabershell", "sair", ("sair",), exit_command,
            aliases=("exit",), global_command=True,
        )
    )
    registry.register(
        CommandSpec(
            "cancelar", "Cancela a operação em andamento", "cancelar", ("cancelar",),
            cancel_command, global_command=True, control_command=True,
        )
    )
    registry.register(
        CommandSpec(
            "varredura", "Verifica quais endereços de uma rede respondem a ICMP",
            "varredura <rede-cidr>", ("varredura 192.168.1.0/24",), sweep_command,
            aliases=("sweep",),
        )
    )
    return registry
