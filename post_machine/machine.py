from typing import Dict, List, Tuple, Optional


class PostMachine:
    def __init__(self, program_text: str, tape: Dict[int,int]=None, head:int=0, step_limit:int=10000):
        self.lines = [line.rstrip() for line in program_text.splitlines() if line.strip() and not line.strip().startswith('#')]
        self.instructions: List[Tuple[Optional[str], str]] = []
        self.labels: Dict[str,int] = {}
        self._parse()
        if not self.labels:
            raise ValueError("Программа должна содержать хотя бы одну метку")
        first_label = next(iter(self.labels))
        self.pc = self.labels[first_label]
        self.tape = tape if tape is not None else {}
        self.head = head
        self.step_limit = step_limit
        self.steps = 0
        self.halted = False
        

    def _parse(self):
        current_label = None
        for line in self.lines:
            if line.endswith(':'):
                lbl = line[:-1].strip()
                self.labels[lbl] = len(self.instructions)
                current_label = lbl
            else:
                self.instructions.append((current_label, line.strip()))
                current_label = None

    def _read(self, pos:int)->int:
        return self.tape.get(pos, 0)

    def _write(self, pos:int, val:int):
        if val == 0:
            self.tape.pop(pos, None)
        else:
            self.tape[pos] = 1

    def step(self):
        if self.halted:
            return
        if self.steps >= self.step_limit:
            raise RuntimeError("Превышен лимит шагов")
        if not (0 <= self.pc < len(self.instructions)):
            raise RuntimeError("PC выходит за границы программы")
        _, instr = self.instructions[self.pc]
        parts = instr.split()
        cmd = parts[0].upper()
        arg = parts[1] if len(parts) > 1 else None
        self.steps += 1
        if cmd == 'MARK':
            self._write(self.head, 1)
            self.pc += 1
        elif cmd == 'ERASE':
            self._write(self.head, 0)
            self.pc += 1
        elif cmd == 'LEFT':
            self.head -= 1
            self.pc += 1
        elif cmd == 'RIGHT':
            self.head += 1
            self.pc += 1
        elif cmd == 'IF1':
            if arg is None:
                raise ValueError("IF1 требует метку")
            if self._read(self.head) == 1:
                self.pc = self.labels[arg]
            else:
                self.pc += 1
        elif cmd == 'IF0':
            if arg is None:
                raise ValueError("IF0 требует метку")
            if self._read(self.head) == 0:
                self.pc = self.labels[arg]
            else:
                self.pc += 1
        elif cmd == 'GOTO':
            if arg is None:
                raise ValueError("GOTO требует метку")
            self.pc = self.labels[arg]
        elif cmd == 'HALT':
            self.halted = True
        else:
            raise ValueError(f"Неизвестная команда: {cmd}")

    def run(self):
        while not self.halted and self.steps < self.step_limit:
            self.step()
            # В CLI-версии печатался формат состояния; в GUI это не нужно, но функция оставлена
        return self.halted

    def format_state(self, window: int=10) -> str:
        left = self.head - window
        right = self.head + window
        cells = ''.join(str(self._read(i)) for i in range(left, right+1))
        return f"step={self.steps:4d} pc={self.pc:3d} head={self.head:4d} tape[{left}..{right}]={cells}"

    def get_tape_span(self):
        if not self.tape:
            return (0, 0)
        return (min(self.tape.keys()), max(self.tape.keys()))

    def tape_as_str_range(self, left:int, right:int) -> str:
        # Возвращает строку слева->справа (min_index .. max_index)
        if left > right:
            return ""
        return ''.join(str(self._read(i)) for i in range(left, right+1))


def tape_from_str(s: str, left_index: int=0) -> Dict[int,int]:
    # Прямое соответствие: s[0] помещается на индекс left_index, s[1] -> left_index+1 и т.д.
    t = {}
    for i, ch in enumerate(s):
        if ch == '1':
            t[left_index + i] = 1
    return t


# Утилиты для нормализации/интерпретации ленты (как в CLI-версии)
def normalize_and_build_str(pm: PostMachine):
    if not pm.tape:
        return "0", 0, pm.head

    left, right = pm.get_tape_span()
    raw = pm.tape_as_str_range(left, right)  # физическая лента

    # Найдём первую и последнюю '1'
    first_one = raw.find('1')
    last_one = raw.rfind('1')

    if first_one == -1:
        # На ленте нет единиц, всё нули
        norm = "0"
        offset = left
        head_norm = pm.head - offset
        return norm, offset, head_norm

    # Нормализованный диапазон по первой и последней единице
    norm = raw[first_one:last_one + 1]
    offset = left + first_one
    head_norm = pm.head - offset
    return norm, offset, head_norm



def tape_str_to_int(bin_str: str) -> int:
    try:
        return int(bin_str, 2)
    except ValueError:
        return 0
