from __future__ import annotations

from rabershell.commands.builtins import (
    back_command,
    cancel_command,
    clear_command,
    enter_icmp_command,
    exit_command,
    help_command,
    ping_command,
    sweep_command,
    version_command,
)
from rabershell.shell.models import CommandSpec
from rabershell.shell.registry import CommandRegistry


def build_registry() -> CommandRegistry:
    registry = CommandRegistry()
    registry.add_context("icmp", "Contexto ICMP.")
    registry.register(
        CommandSpec(
            "ajuda", "Exibe ajuda contextual", "ajuda [comando]",
            ("ajuda", "ajuda ping"), help_command, aliases=("help", "?"),
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
            "icmp", "Abre as ferramentas ICMP", "icmp [comando]",
            ("icmp", "icmp ping 8.8.8.8"), enter_icmp_command,
        )
    )
    registry.register(
        CommandSpec(
            "ping", "Testa a conectividade com um destino",
            "ping <destino> [--quantidade N]", ("ping 8.8.8.8", "ping google.com"),
            ping_command, context="icmp", root_exposed=True,
        )
    )
    registry.register(
        CommandSpec(
            "varredura", "Verifica quais endereços de uma rede respondem a ICMP",
            "varredura <rede-cidr>", ("varredura 192.168.1.0/24",), sweep_command,
            aliases=("sweep",), context="icmp", root_exposed=True,
        )
    )
    registry.register(
        CommandSpec(
            "voltar", "Retorna ao contexto principal", "voltar", ("voltar",),
            back_command, aliases=("back",), context="icmp",
        )
    )
    return registry
