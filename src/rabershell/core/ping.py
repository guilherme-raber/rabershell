from __future__ import annotations

import socket
from dataclasses import dataclass

from rabershell.core.validation import is_ipv4, is_valid_destination
from rabershell.platform.ping_backend import (
    PingBackend,
    PingExecutionTimeoutError,
    PingToolUnavailableError,
)


class InvalidDestinationError(ValueError):
    pass


class HostResolutionError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class PingReport:
    destination: str
    count: int
    successful: bool
    output: str


class PingEngine:
    def __init__(self, backend: PingBackend) -> None:
        self._backend = backend

    def execute(self, destination: str, count: int) -> PingReport:
        if not is_valid_destination(destination):
            raise InvalidDestinationError(
                "Destino inválido. Informe um endereço IPv4 ou hostname válido."
            )
        if not is_ipv4(destination):
            try:
                socket.getaddrinfo(destination, None)
            except socket.gaierror as exc:
                raise HostResolutionError(
                    f'Não foi possível resolver o hostname "{destination}".'
                ) from exc
        result = self._backend.ping(destination, count)
        return PingReport(destination, count, result.successful, result.output)


__all__ = [
    "HostResolutionError",
    "InvalidDestinationError",
    "PingEngine",
    "PingExecutionTimeoutError",
    "PingReport",
    "PingToolUnavailableError",
]
