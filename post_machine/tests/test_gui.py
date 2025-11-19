import pytest
from post_machine.gui import PostMachineGUI

@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr("tkinter.Tk.mainloop", lambda self: None)
    app = PostMachineGUI()
    yield app
    app.destroy()

def test_program_save_and_load(app):
    app.prog_name_entry.insert(0, "test_prog")
    app.prog_text.insert("1.0", "MARK\nHALT")

    app.save_program_action()
    assert "test_prog" in app.prog_list["values"]

    app.prog_list.set("test_prog")
    app.load_program_action()
    text = app.prog_text.get("1.0", "end").strip()
    assert "MARK" in text

def test_input_save_and_load(app):
    app.input_name_entry.insert(0, "input1")
    app.input_entry.insert(0, "101")

    app.save_input_action()
    assert "input1" in app.input_list["values"]

    app.input_list.set("input1")
    app.load_input_action()
    val = app.input_entry.get()
    assert val == "101"