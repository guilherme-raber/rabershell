from __future__ import annotations

import shlex


class ParseError(ValueError):
    """Entrada não pôde ser separada em tokens."""


def parse_line(line: str) -> tuple[str, ...]:
    if not line.strip():
        return ()
    try:
        return tuple(shlex.split(line, posix=True))
    except ValueError as exc:
        raise ParseError("Não foi possível interpretar a entrada. Verifique as aspas.") from exc

