from typing import List, Iterable, Dict, Optional
import sys
import random
import argparse
from bdb import BdbQuit

UNICAT_EMOJIS = {
    "😸": "0",
    "😹": "1",
    "😺": "2",
    "😻": "3",
    "😼": "4",
    "😽": "5",
    "😾": "6",
    "😿": "7",
    "🙀": "8",
}
MNEMONICS = {
    "31": ("asgnlit", 2),
    "57": ("jumpif>", 2),
    "54": ("echovar", 1),
    "44": ("echoval", 1),
    "46": ("pointer", 1),
    "83": ("randomb", 1),
    "24": ("inputst", 1),
    "78": ("applop", 0),
    "88": ("diepgrm", 0),
}
APPLOPS = {
    "2": "-",
    "8": "*",
    "7": "/",
}
DISASSEMBLY = {
    "asgnlit": (False, True),
    "jumpif>": (False, False),
    "echovar": (False,),
    "echoval": (False,),
    "pointer": (False,),
    "randomb": (False,),
    "inputst": (False,),
    "applop+": (False, False),
    "applop-": (False, False),
    "applop*": (False, False),
    "applop/": (False, False),
    "diepgrm": (),
}


class Debug:
    def __init__(self):
        self.ins: List[tuple] = {}
        self.mem: Dict[int, int]

    def show_ins(self):
        for address, it in enumerate(self.ins):
            print(f"{decode_value(address)}: {disassemble_instruction(it)}")

    def show_mem(self, start: Optional[int] = None, end: Optional[int] = None):
        if start is None:
            for address, value in sorted(self.mem.items()):
                _show_value(address, value)
        elif end is None:
            _show_value(start, self.mem.get(start, 0))
        else:
            for address in range(start, end + 1):
                if address in self.mem:
                    _show_value(address, self.mem[address])


def _show_value(address: int, value: int):
    print(f"{decode_value(address)}: {decode_value(value, show_ascii=True)}")


DEBUG = Debug()
show_ins = DEBUG.show_ins
show_mem = DEBUG.show_mem


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help="Debug")
    parser.add_argument("filename", help="Name of unicat file to execute")
    parsed_args = parser.parse_args(argv)

    instructions = compile_instructions(parsed_args.filename)
    execute_instructions(instructions, parsed_args.debug)


def compile_instructions(filename: str) -> List[tuple]:
    with open(filename, "r", encoding="utf-8") as f:
        program = f.read()

    byte_code = convert_to_byte_code(program)
    return parse_statements(byte_code)


def convert_to_byte_code(program: str) -> str:
    return "".join(UNICAT_EMOJIS.get(ch, "") for ch in program)


def parse_statements(byte_code: str) -> List[tuple]:
    instructions: List[tuple] = []
    byte_code_iter: Iterable[str] = iter(byte_code)
    while instruction := parse_statement(byte_code_iter):
        instructions.append(instruction)

    return instructions


def parse_statement(byte_code_iter: Iterable[str]) -> tuple:
    try:
        instruction_code = next(byte_code_iter)
    except StopIteration:
        return ()

    instruction = ("asgnlit", -1, -1)
    try:
        instruction_code += next(byte_code_iter)
        mnemonic, num_numbers = MNEMONICS.get(instruction_code, ("", 0))
        numbers = tuple(parse_number(byte_code_iter) for _ in range(num_numbers))
        if not mnemonic:
            pass
        elif mnemonic == "applop":
            opcode = next(byte_code_iter)
            mnemonic += APPLOPS.get(opcode, "+")
            instruction = (
                mnemonic,
                parse_number(byte_code_iter),
                parse_number(byte_code_iter),
            )
        else:
            instruction = (mnemonic,) + numbers
    except StopIteration:
        pass

    return instruction


def parse_number(byte_code_iter: Iterable[str]) -> int:
    value = ""
    try:
        while (digit := next(byte_code_iter)) != "8":
            value += digit

        digit = next(byte_code_iter)
        if digit == "7":
            value = f"-{value}"

        if value in ("", "-"):
            value = "0"

        return int(value, 8)
    except StopIteration:
        return 1337


def execute_instructions(ins: List[tuple], debug: bool = False):
    mem: Dict[int, int] = {-1: -1}
    if debug:
        print(
            """\
Welcome to the Unicat debugger

Here are the commands:

- show_ins()           - Show instructions
- show_mem()           - Show all memory
- show_mem(start)      - Show memory address <start>
- show_mem(start, end) - Show memory address <start> to <end>
- c                    - Execute next instruction

Everything else is just a pdb command.
See https://docs.python.org/3/library/pdb.html for details.
"""
        )

        DEBUG.mem = mem
        DEBUG.ins = ins

    while True:
        try:
            mem[-1] += 1
            try:
                it = ins[mem[-1]]
            except IndexError:
                it = ("asgnlit", -1, -1)

            if debug:
                print(
                    f"Current instruction:\nAddress {decode_value(mem[-1])}: "
                    + disassemble_instruction(it)
                )
                breakpoint()  # pylint: disable=forgotten-debug-statement

            if it[0] == "diepgrm":
                return

            if it[0] == "pointer":
                mem[it[1]] = mem.get(mem.get(it[1], 0), 0)
            elif it[0] == "randomb":
                mem[it[1]] = random.choice([0, 1])
            elif it[0] == "asgnlit":
                mem[it[1]] = it[2]
            elif it[0] == "jumpif>" and mem.get(it[1], 0) > 0:
                mem[-1] = it[2]
            elif it[0] == "applop+":
                mem[it[1]] = mem.get(it[1], 0) + mem.get(it[2], 0)
            elif it[0] == "applop-":
                mem[it[1]] = mem.get(it[1], 0) - mem.get(it[2], 0)
            elif it[0] == "applop/":
                mem[it[1]] = mem.get(it[1], 0) // mem.get(it[2], 0)
            elif it[0] == "applop*":
                mem[it[1]] = mem.get(it[1], 0) * mem.get(it[2], 0)
            elif it[0] == "echovar":
                sys.stdout.write(chr(mem.get(it[1], 0)))
            elif it[0] == "echoval":
                sys.stdout.write(str(mem.get(it[1], 0)))
            elif it[0] == "inputst":
                inp = sys.stdin.readline()
                for k, ch in enumerate(inp, start=it[1]):
                    mem[k] = ord(ch)

                mem[it[1] + len(inp)] = 0
        except BdbQuit:
            return


def decode_value(value: int, show_ascii=False):
    value_str = f"{value} ({oct(value)}"
    if show_ascii:
        try:
            value_str += f" = {repr(chr(value))}"
        except ValueError:
            pass

    return f"{value_str})"


def disassemble_instruction(instruction: tuple):
    instruction_list = [instruction[0]]
    instruction_list += [
        decode_value(operand, show_ascii=show_ascii)
        for operand, show_ascii in zip(instruction[1:], DISASSEMBLY[instruction[0]])
    ] or []
    return ", ".join(instruction_list).replace(",", "", 1)
