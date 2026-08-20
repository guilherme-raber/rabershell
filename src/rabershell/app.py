from __future__ import annotations

from rabershell.commands.catalog import build_registry
from rabershell.core.ping import PingEngine
from rabershell.core.sweep import SweepEngine
from rabershell.gui.terminal import TerminalWindow
from rabershell.platform.ping_backend import SystemPingBackend
from rabershell.shell.session import ShellSession


def create_session() -> ShellSession:
    backend = SystemPingBackend()
    return ShellSession(build_registry(), PingEngine(backend), SweepEngine(backend))


def main() -> None:
    TerminalWindow(create_session()).run()
