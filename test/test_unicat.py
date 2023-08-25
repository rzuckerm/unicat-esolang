from unittest.mock import patch
import sys

import pytest

from unicat_esolang import unicat


@pytest.mark.parametrize(
    "byte_code,expected_number",
    [
        ("", 1337),
        ("1", 1337),
        ("88", 0),
        ("87", 0),
        ("1234567088", 0o12345670),
        ("7654321087", -0o76543210),
    ],
)
def test_parse_number(byte_code, expected_number):
    number = unicat.parse_number(iter(byte_code))
    assert number == expected_number


def test_hello_world(capsys):
    with patch.object(sys, "argv", ["unicat", "examples/hello-world.cat"]):
        unicat.main()

    output = capsys.readouterr().out
    assert output == "Hello, World!\n"
