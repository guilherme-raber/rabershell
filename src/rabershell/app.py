from __future__ import annotations

from rabershell.commands.catalog import build_registry
from rabershell.core.sweep import SweepEngine
from rabershell.gui.terminal import TerminalWindow
from rabershell.platform.sweep_backend import SystemSweepProbeBackend
from rabershell.shell.session import ShellSession


def create_session() -> ShellSession:
    backend = SystemSweepProbeBackend()
    return ShellSession(build_registry(), SweepEngine(backend))


def main() -> None:
    TerminalWindow(create_session()).run()
