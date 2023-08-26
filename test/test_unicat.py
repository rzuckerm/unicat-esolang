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
        ("512786", 0o5127),
        ("345685", 0o3456),
        ("654384", 0o6543),
        ("453183", 0o4531),
        ("5377382", 0o53773),
        ("4781", 0o47),
        ("616480", 0o6164),
    ],
)
def test_parse_number(byte_code, expected_number):
    number = unicat.parse_number(iter(byte_code))
    assert number == expected_number


@pytest.mark.parametrize(
    "byte_code,expected_instruction",
    [
        pytest.param("", (), id="empty"),
        pytest.param("2", ("asgnlit", -1, -1), id="too-short"),
        pytest.param("85", ("asgnlit", -1, -1), id="invalid"),
        pytest.param("3152882187", ("asgnlit", 0o52, -0o21), id="asgnlit"),
        pytest.param("574882388", ("jumpif>", 0o4, 0o23), id="jumpif>"),
        pytest.param("5462188", ("echovar", 0o621), id="echovar"),
        pytest.param("44288", ("echoval", 0o2), id="echoval"),
        pytest.param("4610488", ("pointer", 0o104), id="pointer"),
        pytest.param("8353088", ("randomb", 0o530), id="randomb"),
        pytest.param("2412388", ("inputst", 0o123), id="inputst"),
        pytest.param("7801548820288", ("applop+", 0o154, 0o202), id="applop+0"),
        pytest.param("78127884688", ("applop+", 0o27, 0o46), id="applop+1"),
        pytest.param("78245886188", ("applop-", 0o45, 0o61), id="applop-"),
        pytest.param("7836128821588", ("applop+", 0o612, 0o215), id="applop+3"),
        pytest.param("78453885788", ("applop+", 0o53, 0o57), id="applop+4"),
        pytest.param("785378843288", ("applop+", 0o37, 0o432), id="applop+5"),
        pytest.param("78661886388", ("applop+", 0o61, 0o63), id="applop+6"),
        pytest.param("7871628821588", ("applop/", 0o162, 0o215), id="applop/"),
        pytest.param("78853886788", ("applop*", 0o53, 0o67), id="applop*"),
    ],
)
def test_parse_statement(byte_code, expected_instruction):
    instruction = unicat.parse_statement(iter(byte_code))
    assert instruction == expected_instruction


def test_bad_args():
    with patch.object(sys, "argv", ["unicat"]), pytest.raises(SystemExit):
        unicat.main()


def test_hello_world(capsys):
    verify_unicat(capsys, "hello-world.cat", "Hello, World!\n")


def test_math(capsys):
    expected_output = """\
42+23=65
27-72=-45
61*18=1098
107/13=8
"""
    verify_unicat(capsys, "math.cat", expected_output)


@patch("unicat_esolang.unicat.random.choice")
def test_random(mock_randint, capsys):
    mock_randint.side_effect = [1, 0, 0, 1]
    verify_unicat(capsys, "random.cat", "TFFT\n")


def verify_unicat(capsys, filename, expected_output):
    output = run_unicat(capsys, filename)
    assert output == expected_output


def run_unicat(capsys, filename):
    with patch.object(sys, "argv", ["unicat", f"examples/{filename}"]):
        unicat.main()

    return capsys.readouterr().out
