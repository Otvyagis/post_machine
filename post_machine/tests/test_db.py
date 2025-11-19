import os
import sqlite3
import pytest
from post_machine import db

TEST_DB = "test_post_machine.db"

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    monkeypatch.setattr(db, "DB_NAME", TEST_DB)
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    db.init_db()
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_init_creates_tables():
    conn = sqlite3.connect(TEST_DB)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    conn.close()
    assert "programs" in tables
    assert "inputs" in tables

def test_save_and_load_program():
    db.save_program("prog1", "MARK\nHALT")
    result = db.load_program("prog1")
    assert "MARK" in result

def test_save_and_load_input():
    db.save_input("input1", "101")
    result = db.load_input("input1")
    assert result == "101"

def test_list_programs_and_inputs():
    db.save_program("prog1", "MARK")
    db.save_input("input1", "1")
    progs = db.list_programs()
    inputs = db.list_inputs()
    assert any(name == "prog1" for _, name in progs)
    assert any(name == "input1" for _, name in inputs)

def test_load_nonexistent_program():
    with pytest.raises(ValueError):
        db.load_program("nope")

def test_load_nonexistent_input():
    with pytest.raises(ValueError):
        db.load_input("nope")