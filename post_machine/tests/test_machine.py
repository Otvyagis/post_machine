import pytest
from post_machine.machine import PostMachine, tape_from_str

BASIC_PROGRAM = """
start:
    MARK
    RIGHT
    MARK
    LEFT
    IF1 end
    GOTO start
end:
    HALT
"""

def test_basic_execution():
    tape = {}
    pm = PostMachine(BASIC_PROGRAM, tape)
    pm.run()
    assert pm.halted
    assert pm.steps > 0
    assert 0 in pm.tape
    assert 1 in pm.tape

def test_mark_and_erase():
    code = """
start:
    MARK
    ERASE
    HALT
"""
    pm = PostMachine(code, {})
    pm.run()
    assert len(pm.tape) == 0

def test_left_and_right_moves():
    code = """
start:
    RIGHT
    RIGHT
    LEFT
    MARK
    HALT
"""
    pm = PostMachine(code)
    pm.run()
    assert pm.head == 1
    assert pm.tape.get(1) == 1

def test_if0_and_if1():
    code = """
start:
    IF0 label0
    IF1 label1
label0:
    MARK
    GOTO end
label1:
    ERASE
end:
    HALT
"""
    pm0 = PostMachine(code, tape_from_str("0"))
    pm0.run()
    assert 0 in pm0.tape.values() or 1 in pm0.tape.values()

    pm1 = PostMachine(code, tape_from_str("1"))
    pm1.run()
    assert pm1.halted

def test_goto_and_halt():
    code = """
a:
    GOTO b
b:
    HALT
"""
    pm = PostMachine(code)
    pm.run()
    assert pm.halted

def test_increment_program():
    code = """
start:
    RIGHT
find_end:
    IF0 at_end
    RIGHT
    GOTO find_end
at_end:
    LEFT
add:
    IF0 set1
    ERASE
    LEFT
    GOTO add
set1:
    MARK
    HALT
"""
    tape = tape_from_str("1011")
    pm = PostMachine(code, tape=tape)
    pm.run()
    left, right = pm.get_tape_span()
    res = pm.tape_as_str_range(left, right)
    assert int(res, 2) == int("10011", 2)