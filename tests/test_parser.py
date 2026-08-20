import pytest

from rabershell.shell.parser import ParseError, parse_line


def test_empty_input_has_no_tokens() -> None:
    assert parse_line("   ") == ()


def test_parser_preserves_quoted_argument() -> None:
    assert parse_line('ping "host.example" --count 2') == (
        "ping", "host.example", "--count", "2"
    )


def test_unclosed_quote_is_friendly_error() -> None:
    with pytest.raises(ParseError, match="Verifique as aspas"):
        parse_line('ping "example.com')

