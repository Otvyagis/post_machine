import os
import pytest
from post_machine import db
from post_machine.machine import PostMachine, tape_from_str

TEST_DB = "test_post_machine_integration.db"

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    monkeypatch.setattr(db, "DB_NAME", TEST_DB)
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    db.init_db()
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_full_cycle_run():
    program_code = """
start:
    MARK
    RIGHT
    MARK
    HALT
"""
    db.save_program("double_mark", program_code)
    db.save_input("input_zero", "0")

    code = db.load_program("double_mark")
    data = db.load_input("input_zero")
    pm = PostMachine(code, tape=tape_from_str(data))
    pm.run()

    left, right = pm.get_tape_span()
    result = pm.tape_as_str_range(left, right)
    assert result.count("1") >= 2
    assert pm.halted