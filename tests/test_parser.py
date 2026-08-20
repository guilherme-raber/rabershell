import pytest

from rabershell.shell.parser import ParseError, parse_line


def test_empty_input_has_no_tokens() -> None:
    assert parse_line("   ") == ()


def test_parser_preserves_quoted_argument() -> None:
    assert parse_line('varredura "192.0.2.0/24"') == ("varredura", "192.0.2.0/24")


def test_unclosed_quote_is_friendly_error() -> None:
    with pytest.raises(ParseError, match="Verifique as aspas"):
        parse_line('varredura "192.0.2.0/24')
