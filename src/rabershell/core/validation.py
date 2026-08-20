from __future__ import annotations

import ipaddress
import re

_HOST_LABEL = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")


def is_ipv4(value: str) -> bool:
    try:
        return isinstance(ipaddress.ip_address(value), ipaddress.IPv4Address)
    except ValueError:
        return False


def is_valid_hostname(value: str) -> bool:
    """Valida somente a sintaxe; não tenta resolver o nome via DNS."""
    candidate = value[:-1] if value.endswith(".") else value
    if not candidate or len(candidate) > 253:
        return False
    return all(_HOST_LABEL.fullmatch(label) is not None for label in candidate.split("."))


def is_valid_destination(value: str) -> bool:
    return is_ipv4(value) or is_valid_hostname(value)

