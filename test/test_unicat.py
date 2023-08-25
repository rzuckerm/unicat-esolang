from unittest.mock import patch
import sys

import pytest

from unicat_esolang import unicat


def test_convert_to_byte_code():
    program = """\
😸 This is 0
😹 This is 1
😺 This is 2
😻 This is 3
😼 This is 4
😽 This is 5
😾 This is 6
😿 This is 7
🙀 This is 8
"""
    byte_code = unicat.convert_to_byte_code(program)
    assert byte_code == "012345678"


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


def test_bad_args():
    with patch.object(sys, "argv", ["unicat"]), pytest.raises(SystemExit):
        unicat.main()


def test_hello_world(capsys):
    with patch.object(sys, "argv", ["unicat", "examples/hello-world.cat"]):
        unicat.main()

    output = capsys.readouterr().out
    assert output == "Hello, World!\n"
