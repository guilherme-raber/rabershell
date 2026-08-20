from __future__ import annotations

import locale
import platform
import subprocess
from dataclasses import dataclass
from typing import Protocol


class PingToolUnavailableError(RuntimeError):
    pass


class PingExecutionTimeoutError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class BackendPingResult:
    successful: bool
    output: str


class PingBackend(Protocol):
    def ping(self, destination: str, count: int) -> BackendPingResult: ...


class SystemPingBackend:
    def __init__(self, system_name: str | None = None) -> None:
        self._system_name = system_name or platform.system()

    def build_arguments(self, destination: str, count: int) -> list[str]:
        if self._system_name == "Windows":
            return ["ping", "-n", str(count), destination]
        if self._system_name in {"Linux", "Darwin"}:
            return ["ping", "-c", str(count), destination]
        raise PingToolUnavailableError(
            "O ping ainda não possui backend para "
            f"{self._system_name or 'esta plataforma'}."
        )

    def ping(self, destination: str, count: int) -> BackendPingResult:
        arguments = self.build_arguments(destination, count)
        try:
            process = subprocess.run(
                arguments,
                capture_output=True,
                check=False,
                encoding=locale.getpreferredencoding(False),
                errors="replace",
                shell=False,
                timeout=max(8, count * 5),
            )
        except FileNotFoundError as exc:
            raise PingToolUnavailableError(
                "A ferramenta ping não foi encontrada no sistema."
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise PingExecutionTimeoutError("A execução do ping excedeu o tempo limite.") from exc
        output = (process.stdout or process.stderr).strip()
        return BackendPingResult(successful=process.returncode == 0, output=output)
