from unittest.mock import patch
from bdb import BdbQuit
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
    with pytest.raises(SystemExit):
        unicat.main([])


def test_hello_world(capsys):
    verify_unicat(capsys, "hello-world.cat", "Hello, World!")


def test_fizz_buzz(capsys):
    expected_output = ""
    for n in range(1, 101):
        line = "Fizz" if n % 3 == 0 else ""
        line += "Buzz" if n % 5 == 0 else ""
        line += "" if line else str(n)
        expected_output += f"{line}\n"

    verify_unicat(capsys, "fizz-buzz.cat", expected_output)


def test_baklava(capsys):
    expected_output = ""
    for n in range(-10, 11):
        num_spaces = abs(n)
        num_stars = 21 - 2 * num_spaces
        expected_output += " " * num_spaces + "*" * num_stars + "\n"

    verify_unicat(capsys, "baklava.cat", expected_output)


@pytest.mark.parametrize(
    "input_string,expected_output",
    [
        ("\n", "0"),
        ("1234567890\n", "1234567890"),
        ("357/\n", "357"),
        ("1248:\n", "1248"),
    ],
)
def test_input_number(input_string, expected_output, mock_readline, capsys):
    mock_readline.return_value = input_string
    verify_unicat(capsys, "input-number.cat", expected_output)


@patch("unicat_esolang.unicat.random.choice")
def test_random(mock_randint, capsys):
    mock_randint.side_effect = [1, 0, 0, 1]
    verify_unicat(capsys, "random.cat", "TFFT")


@pytest.mark.parametrize(
    "input_string,expected_output",
    [
        ("", ""),
        ("Hello, World!\n", "!dlroW ,olleH"),
        ("\n", ""),
        ("Meow, World", "dlroW ,woeM"),
    ],
)
def test_reverse_string(input_string, expected_output, mock_readline, capsys):
    mock_readline.return_value = input_string
    verify_unicat(capsys, "reverse-string.cat", expected_output)


def test_bad_jump(capsys):
    verify_unicat(capsys, "bad-jump.cat", "x")


@pytest.mark.parametrize(
    "value,show_ascii,expected_output",
    [
        (-1, False, "-1 (-0o1)"),
        (-1, True, "-1 (-0o1)"),
        (0, False, "0 (0o0)"),
        (0, True, "0 (0o0 = '\\x00')"),
        (1, False, "1 (0o1)"),
        (1, True, "1 (0o1 = '\\x01')"),
        (8, False, "8 (0o10)"),
        (8, True, "8 (0o10 = '\\x08')"),
        (9, False, "9 (0o11)"),
        (9, True, "9 (0o11 = '\\t')"),
        (10, False, "10 (0o12)"),
        (10, True, "10 (0o12 = '\\n')"),
        (13, False, "13 (0o15)"),
        (13, True, "13 (0o15 = '\\r')"),
        (72, False, "72 (0o110)"),
        (72, True, "72 (0o110 = 'H')"),
        (127, False, "127 (0o177)"),
        (127, True, "127 (0o177 = '\\x7f')"),
        (128576, False, "128576 (0o373100)"),
        (128576, True, "128576 (0o373100 = '🙀')"),
        (
            sys.maxunicode + 1,
            False,
            f"{sys.maxunicode + 1} ({oct(sys.maxunicode + 1)})",
        ),
        (
            sys.maxunicode + 1,
            True,
            f"{sys.maxunicode + 1} ({oct(sys.maxunicode + 1)})",
        ),
    ],
)
def test_decode_value(value, show_ascii, expected_output):
    output = unicat.decode_value(value, show_ascii=show_ascii)
    assert output == expected_output


@pytest.mark.parametrize(
    "instruction,expected_output",
    [
        pytest.param(
            ("asgnlit", 13, 55), "asgnlit 13 (0o15), 55 (0o67 = '7')", id="asgnlit"
        ),
        pytest.param(("jumpif>", 5, 101), "jumpif> 5 (0o5), 101 (0o145)", id="jumpif>"),
        pytest.param(("echovar", 33), "echovar 33 (0o41)", id="echovar"),
        pytest.param(("echoval", 92), "echoval 92 (0o134)", id="echoval"),
        pytest.param(("pointer", 18), "pointer 18 (0o22)", id="pointer"),
        pytest.param(("randomb", 37), "randomb 37 (0o45)", id="randomb"),
        pytest.param(("inputst", 19), "inputst 19 (0o23)", id="inputst"),
        pytest.param(("applop+", 1, 5), "applop+ 1 (0o1), 5 (0o5)", id="applop+"),
        pytest.param(("applop-", 7, 14), "applop- 7 (0o7), 14 (0o16)", id="applop-"),
        pytest.param(("applop*", 23, 45), "applop* 23 (0o27), 45 (0o55)", id="applop*"),
        pytest.param(("applop/", 6, 3), "applop/ 6 (0o6), 3 (0o3)", id="applop/"),
        pytest.param(("diepgrm",), "diepgrm", id="diepgrm"),
    ],
)
def test_disassemble_instruction(instruction, expected_output):
    output = unicat.disassemble_instruction(instruction)
    assert output == expected_output


@pytest.mark.parametrize("option", ["-d", "--debug"])
@patch("builtins.breakpoint")
def test_debug(mock_breakpoint, option, capsys):
    with open("examples/hello-world.cat", "r", encoding="utf-8") as f:
        contents = f.read()

    num_lines = len(
        [
            line
            for line in contents.splitlines()
            if line.strip() and not line.startswith("#")
        ]
    )
    mock_breakpoint.side_effect = [None] * (num_lines - 1) + [BdbQuit()]

    output = run_unicat(capsys, "hello-world.cat", [option])

    assert "Welcome" in output
    assert "asgnlit 0 (0o0), 72 (0o110 = 'H')" in output
    assert "echovar 0 (0o0)" in output
    assert "diepgrm" in output


def verify_unicat(capsys, filename, expected_output):
    output = run_unicat(capsys, filename)
    if not expected_output.endswith("\n"):
        expected_output += "\n"

    assert output == expected_output


def run_unicat(capsys, filename, options=None):
    if not options:
        options = []

    unicat.main([f"examples/{filename}"] + options)
    return capsys.readouterr().out


@pytest.fixture()
def mock_readline():
    with patch("unicat_esolang.unicat.sys.stdin.readline") as mock:
        yield mock
