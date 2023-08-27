[![Makefile CI](https://github.com/rzuckerm/unicat-esolang/actions/workflows/makefile.yml/badge.svg)](https://github.com/rzuckerm/unicat-esolang/actions/workflows/makefile.yml)
[![Coverage](https://rzuckerm.github.io/unicat-esolang/badge.svg)](https://rzuckerm.github.io/unicat-esolang/html_cov)
[![PyPI version](https://img.shields.io/pypi/v/unicat-esolang)](https://pypi.org/project/unicat-esolang)
[![Python versions](https://img.shields.io/pypi/pyversions/unicat-esolang)](https://pypi.org/project/unicat-esolang)
[![Python wheel](https://img.shields.io/pypi/wheel/unicat-esolang)](https://pypi.org/project/unicat-esolang)

# unicat-esolang

Python 3 Port of Unicat Esoteric Language created by [gemdude64](https://github.com/gemdude46/unicat).
See TBD for a description of the language.

## Prerequisites

Python 3.8 or later

## Installing

```
pip install --user esocat-lang
```

## Usage

Use this 
```
unicat [-d/--debug] FILENAME
```

where:

* `-d` or `--debug` enables debugging
* `FILENAME` is the path to the Unicat program

## Debugging

When `unicat` is run with `-d` or `--debug`, the python debugger is entered
before each instruction. The first time, a welcome screen is displayed:

```
Welcome to the Unicat debugger

Here are the commands:

- ins      - Show instructions
- mem      - Show all memory
- mem[<n>] - Show memory address <n>
- c        - Execute next instruction

Everything else is just a pdb command.
See https://docs.python.org/3/library/pdb.html for details.

```

When the debugger is entered, the current instruction and a dump of the
memory is displayed. For example:

```
Current instruction:
Address 0 (0o0): asgnlit 0 (0o0), 72 (0o110 = 'H')
Memory:
-1 (-0o1): 0 (0o0 = '\x00')
> .../unicat.py(167)execute_instructions()
-> if it[0] == "diepgrm":
```

## Examples

Example programs can be found [here](https://github.com/rzuckerm/unicat-esolang/tree/main/examples).
These programs are also used for unit testing the Unicat language
implementation.
