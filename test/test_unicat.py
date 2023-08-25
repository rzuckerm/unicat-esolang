from unittest.mock import patch
import sys

from unicat_esolang.unicat import main


def test_hello_world(capsys):
    with patch.object(sys, "argv", ["unicat", "examples/hello-world.cat"]):
        main()

    output = capsys.readouterr().out
    assert output == "Hello, World!\n"
