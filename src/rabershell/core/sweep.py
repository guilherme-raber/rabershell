from __future__ import annotations

import ipaddress
import threading
import time
from collections.abc import Iterator
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass

from rabershell.platform.ping_backend import SweepProbeBackend

MAX_SWEEP_ADDRESSES = 4096
DEFAULT_SWEEP_WORKERS = 32
DEFAULT_PROBE_TIMEOUT_SECONDS = 1.0


class InvalidNetworkError(ValueError):
    pass


class NetworkTooLargeError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class SweepReport:
    network: str
    total_hosts: int
    checked_hosts: int
    responsive_hosts: tuple[str, ...]
    cancelled: bool
    elapsed_seconds: float


class SweepEngine:
    def __init__(
        self,
        backend: SweepProbeBackend,
        *,
        max_workers: int = DEFAULT_SWEEP_WORKERS,
        probe_timeout_seconds: float = DEFAULT_PROBE_TIMEOUT_SECONDS,
    ) -> None:
        self._backend = backend
        self._max_workers = max_workers
        self._probe_timeout_seconds = probe_timeout_seconds

    def execute(self, value: str, cancel_event: threading.Event) -> SweepReport:
        network = self._parse_network(value)
        hosts = tuple(str(host) for host in network.hosts())
        started_at = time.monotonic()
        responsive: list[str] = []
        checked = 0
        host_iterator = iter(hosts)
        worker_count = min(self._max_workers, max(1, len(hosts)))
        executor = ThreadPoolExecutor(max_workers=worker_count, thread_name_prefix="sweep-probe")
        pending: dict[Future[bool], str] = {}

        try:
            self._fill_window(executor, pending, host_iterator, cancel_event, worker_count)
            while pending and not cancel_event.is_set():
                completed, _ = wait(tuple(pending), timeout=0.1, return_when=FIRST_COMPLETED)
                for future in completed:
                    host = pending.pop(future)
                    checked += 1
                    if future.result():
                        responsive.append(host)
                self._fill_window(executor, pending, host_iterator, cancel_event, worker_count)
        finally:
            if cancel_event.is_set():
                for future in pending:
                    future.cancel()
            executor.shutdown(wait=True, cancel_futures=True)
            if cancel_event.is_set():
                for future, host in pending.items():
                    if not future.cancelled():
                        checked += 1
                        if future.result():
                            responsive.append(host)

        responsive.sort(key=ipaddress.IPv4Address)
        return SweepReport(
            network=str(network),
            total_hosts=len(hosts),
            checked_hosts=checked,
            responsive_hosts=tuple(responsive),
            cancelled=cancel_event.is_set(),
            elapsed_seconds=time.monotonic() - started_at,
        )

    def _fill_window(
        self,
        executor: ThreadPoolExecutor,
        pending: dict[Future[bool], str],
        hosts: Iterator[str],
        cancel_event: threading.Event,
        worker_count: int,
    ) -> None:
        while len(pending) < worker_count and not cancel_event.is_set():
            try:
                host = next(hosts)
            except StopIteration:
                return
            pending[
                executor.submit(self._backend.probe, host, self._probe_timeout_seconds)
            ] = host

    def _parse_network(self, value: str) -> ipaddress.IPv4Network:
        if "/" not in value:
            raise InvalidNetworkError("Rede inválida. Informe uma rede IPv4 em formato CIDR.")
        try:
            network = ipaddress.ip_network(value, strict=False)
        except ValueError as exc:
            raise InvalidNetworkError(
                "Rede inválida. Informe uma rede IPv4 em formato CIDR."
            ) from exc
        if not isinstance(network, ipaddress.IPv4Network):
            raise InvalidNetworkError("A primeira versão do sweep aceita somente redes IPv4.")
        if network.num_addresses > MAX_SWEEP_ADDRESSES:
            raise NetworkTooLargeError(
                "Rede muito grande para esta versão. O limite é 4.096 endereços (IPv4 /20)."
            )
        return network
