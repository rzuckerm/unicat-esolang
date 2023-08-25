from typing import List, Iterable, Dict
import sys
import random

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
    "7": "-",
}


def main():
    if len(sys.argv) != 2:
        sys.exit(-1)

    instructions = compile(sys.argv[1])
    execute(instructions)



def compile(filename: str) -> List[tuple]:
    with open(filename, "r", encoding="utf-8") as f:
        program = f.read()

    byte_code = convert_to_byte_code(program)
    return parse_statements(byte_code)

def convert_to_byte_code(program: str) -> str:
    return "".join(UNICAT_EMOJIS.get(ch, "") for ch in program)


def parse_statements(byte_code: str) -> List[tuple]:
    instructions: List[tuple] = []
    byte_code_iter: Iterable[str] = iter(byte_code)
    while (instruction := parse_statement(byte_code_iter)):
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


def execute(ins: List[tuple]):
    mem: Dict[int, int] = {}
    while True:
        mem[-1] = mem.get(-1, -1) + 1
        try:
            it = ins[mem[-1]]
        except IndexError:
            it = ("asgnlit", -1, -1)

        if it[0] == "diepgrm":
            return

        if it[0] == "pointer":
            mem[it[1]] = mem.get(mem.get(it[1], 0), 0)
        elif it[0] == "randomb":
            mem[it[1]] = random.randint(True, False)
        elif it[0] == "asgnlit":
            mem[it[1]] = it[2]
        elif it[0] == "jumpif>" and mem.get(it[1], 0) > 0:
            mem[-1] = it[2]
        elif it[0] == "applop+":
            mem[it[1]] = mem.get(it[1], 0) + mem.get(it[2], 0)
        elif it[0] == "applop-":
            mem[it[1]] = mem.get(it[1], 0) - mem.get(it[2], 0)
        elif it[0] == "applop/":
            mem[it[1]] = mem.get(it[1], 0) / mem.get(it[2], 0)
        elif it[0] == "applop*":
            mem[it[1]] = mem.get(it[1], 0) * mem.get(it[2], 0)
        elif it[0] == "echovar":
            sys.stdout.write(chr(mem.get(it[1], 0)))
        elif it[0] == "echoval":
            sys.stdout.write(str(mem.get(it[1], 0)))
        elif it[0] == "inputst":
            inp = sys.stdin.readline()
            for k in range(it[1], it[1] + len(inp)):
                mem[k] = ord(inp[k - it[1]])
            mem[k + 1] = 0
