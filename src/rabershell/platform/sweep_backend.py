from __future__ import annotations

import math
import platform
import subprocess
from typing import Protocol


class SweepToolUnavailableError(RuntimeError):
    pass


class SweepProbeBackend(Protocol):
    def probe(self, destination: str, timeout_seconds: float) -> bool: ...


class SystemSweepProbeBackend:
    def __init__(self, system_name: str | None = None) -> None:
        self._system_name = system_name or platform.system()

    def build_arguments(self, destination: str, timeout_seconds: float) -> list[str]:
        timeout_milliseconds = max(1, math.ceil(timeout_seconds * 1000))
        if self._system_name == "Windows":
            return ["ping", "-n", "1", "-w", str(timeout_milliseconds), destination]
        if self._system_name == "Linux":
            return [
                "ping",
                "-c",
                "1",
                "-W",
                str(max(1, math.ceil(timeout_seconds))),
                destination,
            ]
        if self._system_name == "Darwin":
            return ["ping", "-c", "1", "-W", str(timeout_milliseconds), destination]
        raise SweepToolUnavailableError(
            "A varredura ainda não possui backend para "
            f"{self._system_name or 'esta plataforma'}."
        )

    def probe(self, destination: str, timeout_seconds: float) -> bool:
        arguments = self.build_arguments(destination, timeout_seconds)
        try:
            process = subprocess.run(
                arguments,
                capture_output=True,
                check=False,
                shell=False,
                timeout=timeout_seconds + 2,
            )
        except FileNotFoundError as exc:
            raise SweepToolUnavailableError(
                "A ferramenta ping necessária à varredura não foi encontrada no sistema."
            ) from exc
        except subprocess.TimeoutExpired:
            return False
        return process.returncode == 0
