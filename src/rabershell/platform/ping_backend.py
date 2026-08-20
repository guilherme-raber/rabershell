from __future__ import annotations

import locale
import math
import platform
import subprocess
import threading
from collections.abc import Callable
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
    def ping(
        self,
        destination: str,
        count: int,
        on_output: Callable[[str], None] | None = None,
    ) -> BackendPingResult: ...


class SweepProbeBackend(Protocol):
    def probe(self, destination: str, timeout_seconds: float) -> bool: ...


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

    def ping(
        self,
        destination: str,
        count: int,
        on_output: Callable[[str], None] | None = None,
    ) -> BackendPingResult:
        arguments = self.build_arguments(destination, count)
        try:
            process = subprocess.Popen(
                arguments,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding=locale.getpreferredencoding(False),
                errors="replace",
                shell=False,
                bufsize=1,
            )
        except FileNotFoundError as exc:
            raise PingToolUnavailableError(
                "A ferramenta ping não foi encontrada no sistema."
            ) from exc
        except OSError as exc:
            raise PingToolUnavailableError(
                f"Não foi possível iniciar a ferramenta ping: {exc}"
            ) from exc

        if process.stdout is None:
            process.kill()
            process.wait()
            raise PingToolUnavailableError("Não foi possível capturar a saída da ferramenta ping.")

        timed_out = threading.Event()

        def stop_on_timeout() -> None:
            if process.poll() is None:
                timed_out.set()
                try:
                    process.kill()
                except OSError:
                    pass

        timer = threading.Timer(max(8, count * 5), stop_on_timeout)
        timer.daemon = True
        timer.start()
        chunks: list[str] = []
        try:
            for line in process.stdout:
                chunk = line.rstrip("\r\n") + "\n"
                chunks.append(chunk)
                if on_output is not None:
                    on_output(chunk)
            return_code = process.wait()
        except Exception:
            if process.poll() is None:
                try:
                    process.kill()
                except OSError:
                    pass
            process.wait()
            raise
        finally:
            timer.cancel()
            process.stdout.close()

        if timed_out.is_set():
            raise PingExecutionTimeoutError("A execução do ping excedeu o tempo limite.")
        output = "".join(chunks).strip()
        return BackendPingResult(successful=return_code == 0, output=output)

    def build_probe_arguments(self, destination: str, timeout_seconds: float) -> list[str]:
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
        raise PingToolUnavailableError(
            "A varredura ainda não possui backend para "
            f"{self._system_name or 'esta plataforma'}."
        )

    def probe(self, destination: str, timeout_seconds: float) -> bool:
        arguments = self.build_probe_arguments(destination, timeout_seconds)
        try:
            process = subprocess.run(
                arguments,
                capture_output=True,
                check=False,
                shell=False,
                timeout=timeout_seconds + 2,
            )
        except FileNotFoundError as exc:
            raise PingToolUnavailableError(
                "A ferramenta ping não foi encontrada no sistema."
            ) from exc
        except subprocess.TimeoutExpired:
            return False
        return process.returncode == 0
