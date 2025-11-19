import tkinter as tk
from tkinter import ttk, messagebox
from .db import init_db, save_program, save_input, list_programs, list_inputs, load_program, load_input
from .machine import PostMachine, tape_from_str, normalize_and_build_str, tape_str_to_int


class PostMachineGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Машина Поста")
        self.geometry("900x650")
        self.resizable(False, False)

        init_db()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self._build_program_tab()
        self._build_input_tab()
        self._build_run_tab()

    # --- Программы ---
    def _build_program_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Программы")

        ttk.Label(frame, text="Имя программы:").pack(pady=5)
        self.prog_name_entry = ttk.Entry(frame, width=30)
        self.prog_name_entry.pack()

        ttk.Label(frame, text="Код программы:").pack(pady=5)
        self.prog_text = tk.Text(frame, height=20, width=80)
        self.prog_text.pack()

        ttk.Button(frame, text="Сохранить", command=self.save_program_action).pack(pady=5)
        ttk.Button(frame, text="Загрузить", command=self.load_program_action).pack(pady=5)

        self.prog_list = ttk.Combobox(frame, values=[n for _, n in list_programs()], width=40)
        self.prog_list.pack(pady=10)

    # --- Входные данные ---
    def _build_input_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Входные данные")

        ttk.Label(frame, text="Имя набора данных:").pack(pady=5)
        self.input_name_entry = ttk.Entry(frame, width=30)
        self.input_name_entry.pack()

        ttk.Label(frame, text="Бинарная строка (0/1):").pack(pady=5)
        self.input_entry = ttk.Entry(frame, width=50)
        self.input_entry.pack()

        ttk.Button(frame, text="Сохранить", command=self.save_input_action).pack(pady=5)
        ttk.Button(frame, text="Загрузить", command=self.load_input_action).pack(pady=5)

        self.input_list = ttk.Combobox(frame, values=[n for _, n in list_inputs()], width=40)
        self.input_list.pack(pady=10)

    # --- Запуск ---
    def _build_run_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Запуск")

        ttk.Label(frame, text="Выберите программу:").pack(pady=5)
        self.run_prog_combo = ttk.Combobox(frame, values=[n for _, n in list_programs()], width=40)
        self.run_prog_combo.pack()

        ttk.Label(frame, text="Выберите вход:").pack(pady=5)
        self.run_input_combo = ttk.Combobox(frame, values=[n for _, n in list_inputs()], width=40)
        self.run_input_combo.pack()

        ttk.Button(frame, text="Запустить", command=self.run_program_action).pack(pady=10)
        self.result_text = tk.Text(frame, height=20, width=100, state="disabled", wrap="word")
        self.result_text.pack(pady=5)

    # --- Сохранение/загрузка ---
    def save_program_action(self):
        name = self.prog_name_entry.get().strip()
        code = self.prog_text.get("1.0", "end").strip()
        if not name or not code:
            messagebox.showerror("Ошибка", "Имя и код программы не могут быть пустыми.")
            return
        save_program(name, code)
        messagebox.showinfo("Успех", f"Программа '{name}' сохранена.")
        self.prog_list["values"] = [n for _, n in list_programs()]
        self.run_prog_combo["values"] = self.prog_list["values"]

    def load_program_action(self):
        name = self.prog_list.get()
        if not name:
            messagebox.showwarning("Ошибка", "Выберите программу для загрузки.")
            return
        code = load_program(name)
        self.prog_text.delete("1.0", "end")
        self.prog_text.insert("1.0", code)
        self.prog_name_entry.delete("0", "end")
        self.prog_name_entry.insert("0", name)

    def save_input_action(self):
        name = self.input_name_entry.get().strip()
        data = self.input_entry.get().strip()
        if not name or not all(ch in "01" for ch in data):
            messagebox.showerror("Ошибка", "Введите корректные бинарные данные и имя.")
            return
        save_input(name, data)
        messagebox.showinfo("Успех", f"Вход '{name}' сохранён.")
        self.input_list["values"] = [n for _, n in list_inputs()]
        self.run_input_combo["values"] = self.input_list["values"]

    def load_input_action(self):
        name = self.input_list.get()
        if not name:
            messagebox.showwarning("Ошибка", "Выберите вход для загрузки.")
            return
        data = load_input(name)
        self.input_entry.delete("0", "end")
        self.input_entry.insert("0", data)
        self.input_name_entry.delete("0", "end")
        self.input_name_entry.insert("0", name)

    # --- Запуск программы ---
    def run_program_action(self):
        prog_name = self.run_prog_combo.get()
        input_name = self.run_input_combo.get()

        if not prog_name or not input_name:
            messagebox.showerror("Ошибка", "Выберите программу и входные данные.")
            return

        try:
            code = load_program(prog_name)
            data = load_input(input_name)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return

        if any(ch not in "01" for ch in data) or data == "":
            messagebox.showerror("Ошибка", "Входные данные должны быть двоичной строкой (например, 1011).")
            return

        try:
            tape = tape_from_str(data, left_index=0)
            pm = PostMachine(code, tape=tape, head=len(data) - 1)

            pm.run()

            orig_left = 0
            orig_right = len(data) - 1

            left, right = pm.get_tape_span()
            # если лента пустая (нет 1), get_tape_span вернёт (0,0) в текущей реализации,
            # но на всякий случай корректируем:
            if not pm.tape:
                left = orig_left
                right = orig_right

            # расширяем границы так, чтобы захватить исходную длину и возможное расширение
            left_bound = min(left, orig_left)
            right_bound = max(right, orig_right)

            # получаем полную строку в этом расширенном диапазоне
            raw_full = pm.tape_as_str_range(left_bound, right_bound)

            # Смещённая нормализация: offset = left_bound, позиция головки нормализована относительно offset
            offset = left_bound
            head_norm = pm.head - offset

            # человекочитаемая: убираем только ведущие нули слева, но сохраняем все биты справа
            readable = raw_full.lstrip('0') or '0'
            decimal_value = tape_str_to_int(readable)

            # также сохраним "физическую" ленту по реальным границам (для отладки)
            raw_tape = pm.tape_as_str_range(left, right)

            self.result_text.configure(state="normal")
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", f"Результат выполнения программы:\n\n")
            self.result_text.insert("end", f"Исходные данные: {data} (десятичное: {int(data, 2)})\n")
            self.result_text.insert("end", f"Шагов выполнено: {pm.steps}\n\n")

            self.result_text.insert("end", "Лента (физическая, слева-направо) — расширенный диапазон:\n")
            self.result_text.insert("end", f"  [{left_bound} .. {right_bound}]: {raw_full}\n\n")

            self.result_text.insert("end", "Лента (физическая, где есть 1):\n")
            self.result_text.insert("end", f"  [{left} .. {right}]: {raw_tape}\n\n")

            self.result_text.insert("end", "Человекочитаемый результат (нормализованная лента):\n")
            self.result_text.insert("end", f"  Бинарно: {readable}\n")
            self.result_text.insert("end", f"  Десятично: {decimal_value}\n")

            self.result_text.insert("end", f"\nСмещение (offset): {offset}\n")
            self.result_text.insert("end", f"Позиция головки (внутренняя): {pm.head}\n")
            self.result_text.insert("end", f"Позиция головки (нормализованная): {head_norm}\n")

            self.result_text.configure(state="disabled")


        except Exception as e:
            messagebox.showerror("Ошибка выполнения", str(e))


def main():
    app = PostMachineGUI()
    app.mainloop()
