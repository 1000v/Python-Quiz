import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import json
import re
import os
from unidecode import unidecode

# Константы для валидации
MAX_OPTIONS = 6
MAX_QUESTIONS = 20

def excel_to_json(file_path):
    """
    Конвертирует Excel таблицу в JSON формат для сценария.

    Args:
        file_path (str): Путь к Excel файлу.

    Returns:
        tuple: JSON строка, имя сценария, список ошибок (или пустой список, если ошибок нет).
    """
    try:
        df = pd.read_excel(file_path, header=None)
    except Exception as e:
        return "", "", [f"Ошибка при чтении файла Excel: {e}"]

    scenarios = []
    current_scenario = None
    errors = []

    i = 0
    while i < len(df):
        row = df.iloc[i]
        title_cell = row[row.astype(str).str.contains('Название', na=False, case=False)].first_valid_index()

        if title_cell is not None:
            if current_scenario:
                if len(current_scenario["questions"]) > MAX_QUESTIONS:
                    errors.append(f"Сценарий '{current_scenario['name']}': Превышено максимальное количество вопросов ({MAX_QUESTIONS}).")
                scenarios.append(current_scenario)

            scenario_name = str(row.get(title_cell + 1, "")).strip()

            if not scenario_name:  # Проверка на пустое имя сценария
                errors.append("Ошибка: Найден сценарий без названия.")
                scenario_name = "untitled"  # Присваиваем имя по умолчанию

            if any(s["name"] == scenario_name for s in scenarios):
                errors.append(f"Ошибка: Дублирующееся название сценария '{scenario_name}'.")
                scenario_name = f"{scenario_name}_copy"

            current_scenario = {"name": scenario_name, "questions": []}
            i += 1
        elif current_scenario is not None:
            question_cell = row[row.astype(str).str.contains(r'Вопрос\s*', na=False, case=False, regex=True)].first_valid_index()

            if question_cell is not None:
                question = str(row.get(question_cell + 1, "")).strip()

                if not question: # Проверка на пустой вопрос
                    errors.append(f"Сценарий '{current_scenario['name']}': Найден пустой вопрос.")
                    i += 1
                    continue # Переходим к следующей строке

                options = []
                answer = ""

                j = i + 1
                while j < len(df):
                    next_row = df.iloc[j]
                    options_cell = next_row[next_row.astype(str).str.contains(r'Вариант\s*ответ\w*\s*', na=False, case=False, regex=True)].first_valid_index()
                    answer_cell = next_row[next_row.astype(str).str.contains(r'Ответ\s*', na=False, case=False, regex=True)].first_valid_index()

                    if options_cell is not None:
                        options = [str(cell).strip() for cell in next_row.iloc[options_cell + 1: options_cell + 7] if pd.notna(cell)]
                        if len(options) > MAX_OPTIONS:
                            errors.append(f"Сценарий '{current_scenario['name']}': Вопрос '{question}': Превышено максимальное количество вариантов ответа ({MAX_OPTIONS}).")
                            
                        if not all(options): # Проверка на пустые варианты ответа
                            errors.append(f"Сценарий '{current_scenario['name']}': Вопрос '{question}': Найдены пустые варианты ответа.")

                    if answer_cell is not None:
                        answer_value = str(next_row.get(answer_cell + 1, "")).strip()

                        if not answer_value: # Проверка на пустой ответ
                            errors.append(f"Сценарий '{current_scenario['name']}': Вопрос '{question}':  Не указан ответ.")

                        try:
                            answer_index = int(answer_value) - 1
                            if 0 <= answer_index < len(options):
                                answer = options[answer_index]
                            else:
                                errors.append(f"Сценарий '{current_scenario['name']}': Вопрос '{question}':  Номер ответа не соответствует количеству вариантов.")
                                answer = ""
                        except ValueError:
                            # Если не число, то ищем ответ в списке вариантов
                            if answer_value in options:
                                answer = answer_value
                            else:
                                errors.append(f"Сценарий '{current_scenario['name']}': Вопрос '{question}':  Ответ не найден в списке вариантов.")
                                answer = ""

                        i = j + 1
                        break

                    j += 1

                current_scenario["questions"].append({
                    "question": question,
                    "options": options,
                    "answer": answer
                })
            else:
                i += 1
        else:
            i += 1

    if current_scenario:
        if len(current_scenario["questions"]) > MAX_QUESTIONS:
            errors.append(f"Сценарий '{current_scenario['name']}': Превышено максимальное количество вопросов ({MAX_QUESTIONS}).")
        scenarios.append(current_scenario)

    return json.dumps(scenarios, ensure_ascii=False, indent=2), scenarios[0]['name'] if scenarios else "untitled", errors

class ExcelToJsonGUI:
    def __init__(self, master):
        self.master = master
        master.title("Excel to JSON Converter")
        master.geometry("400x200")
        master.configure(bg="#e8f5e9")

        self.label = tk.Label(master, text="Выберите Excel файл:", bg="#e8f5e9", fg="#1b5e20")
        self.label.pack(pady=10)

        self.select_button = tk.Button(master, text="Выбрать файл", command=self.select_file, bg="#4caf50", fg="white")
        self.select_button.pack(pady=10)

        self.convert_button = tk.Button(master, text="Конвертировать", command=self.convert_file, bg="#2e7d32", fg="white")
        self.convert_button.pack(pady=10)

        self.file_path = None

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if self.file_path:
            self.label.config(text=f"Выбранный файл: {self.file_path.split('/')[-1]}")

    def convert_file(self):
        if not self.file_path:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите файл")
            return

        try:
            json_output, scenario_name, errors = excel_to_json(self.file_path)

            if errors:
                error_message = "\n".join(errors)
                messagebox.showerror("Ошибки валидации", error_message)
                return

            if not os.path.exists("scenarios"):
                os.makedirs("scenarios")

            scenario_name = unidecode(scenario_name)
            scenario_name = "".join(c for c in scenario_name if c not in '<>:"/\\|?*')

            with open(os.path.join("scenarios", f"{scenario_name}.json"), 'w', encoding='utf-8') as f:
                f.write(json_output)

            messagebox.showinfo("Успех", f"Файл успешно конвертирован и сохранен как scenarios/{scenario_name}.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при конвертации: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    gui = ExcelToJsonGUI(root)
    root.mainloop()