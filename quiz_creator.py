import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import os
import unidecode

# Константы для валидации
MAX_OPTIONS = 6
MIN_OPTIONS = 2
MAX_QUESTIONS = 20

def add_question():
    question = entry_question.get().strip()
    options = [entry_option_1.get().strip(), entry_option_2.get().strip(), entry_option_3.get().strip(),
               entry_option_4.get().strip(), entry_option_5.get().strip(), entry_option_6.get().strip()]
    options = [opt for opt in options if opt]  # Удаляем пустые варианты

    correct_answer = correct_answer_var.get().strip()

    # Валидация 
    if not question:
        messagebox.showwarning("Ошибка", "Пожалуйста, введите вопрос.")
        return
    if not options:
        messagebox.showwarning("Ошибка", "Пожалуйста, введите хотя бы один вариант ответа.")
        return
    if len(options) < MIN_OPTIONS or len(options) > MAX_OPTIONS:
        messagebox.showwarning("Ошибка", f"Количество вариантов ответа должно быть от {MIN_OPTIONS} до {MAX_OPTIONS}.")
        return
    if not correct_answer:
        messagebox.showwarning("Ошибка", "Пожалуйста, укажите правильный ответ.")
        return
    if correct_answer not in options:
        messagebox.showwarning("Ошибка", "Правильный ответ не найден среди вариантов.")
        return

    question_data = {
        "question": question,
        "options": options,
        "answer": correct_answer,
    }

    questions.append(question_data)
    update_question_list()
    messagebox.showinfo("Успешно", "Вопрос добавлен!")
    clear_fields()

def clear_fields():
    entry_question.delete(0, tk.END)
    for i in range(1, MAX_OPTIONS + 1):
        globals()[f"entry_option_{i}"].delete(0, tk.END)
    correct_answer_var.set("")

def save_scenario():
    title = entry_title.get().strip()
    if not title:
        messagebox.showwarning("Ошибка", "Пожалуйста, введите заголовок сценария.")
        return
    if not questions:
        messagebox.showwarning("Ошибка", "Пожалуйста, добавьте хотя бы один вопрос.")
        return
    if len(questions) > MAX_QUESTIONS:
        messagebox.showwarning("Ошибка", f"Количество вопросов не должно превышать {MAX_QUESTIONS}.")
        return

    filename = unidecode.unidecode(title.replace(" ", "_")) + ".json"
    filepath = os.path.join("scenarios", filename)

    os.makedirs("scenarios", exist_ok=True)

    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(questions, file, ensure_ascii=False, indent=4)
        messagebox.showinfo("Успешно", f"Сценарий сохранен как {filename}!")
        questions.clear()
        update_question_list()
        clear_fields()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при сохранении файла: {e}")

def load_settings():
    settings_path = os.path.join("resources", "settings.json")
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}  # Возвращаем пустой словарь, если файл поврежден
    else:
        return {}  # Возвращаем пустой словарь, если файл не найден

def load_themes():
    themes_path = os.path.join("resources", "themes.json")
    if os.path.exists(themes_path):
        with open(themes_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}  # Возвращаем пустой словарь, если файл поврежден
    else:
        return {}  # Возвращаем пустой словарь, если файл не найден

def apply_theme(theme_name):
    selected_theme = themes.get(theme_name)
    if selected_theme:
        app.configure(bg=selected_theme["background"])
        style = ttk.Style()
        style.theme_use("clam")

        # Настройка стилей для различных виджетов
        style.configure("TCombobox", fieldbackground=selected_theme["background"],
                        selectbackground=selected_theme["button_active_background"],
                        background=selected_theme["button_background"],
                        foreground=selected_theme["foreground"],
                        borderwidth=2,
                        relief="flat")
        style.configure("TButton", background=selected_theme["button_background"],
                        foreground=selected_theme["foreground"],
                        activebackground=selected_theme["button_active_background"],
                        borderwidth=2,
                        relief="flat")
        style.configure("TLabel", background=selected_theme["background"],
                        foreground=selected_theme["foreground"])
        style.configure("TEntry", fieldbackground=selected_theme["background"],
                        foreground=selected_theme["foreground"],
                        background=selected_theme["background"],
                        borderwidth=2,
                        relief="flat")
        style.configure("Treeview", background=selected_theme["background"],
                        fieldbackground=selected_theme["background"],
                        foreground=selected_theme["foreground"])

        # Настройка взаимодействия с элементами (active state)
        style.map("TCombobox",
                  background=[('active', selected_theme["button_active_background"])],
                  foreground=[('active', selected_theme["foreground"])],
                  bordercolor=[('active', selected_theme["foreground"])])
        style.map("TButton",
                  background=[('active', selected_theme["button_active_background"])],
                  foreground=[('active', selected_theme["foreground"])],
                  bordercolor=[('active', selected_theme["foreground"])])
        style.map("TEntry",
                  background=[('active', selected_theme["background"])],
                  foreground=[('active', selected_theme["foreground"])],
                  bordercolor=[('active', selected_theme["foreground"])])

        # Применение стиля к виджетам
        for widget in app.winfo_children():
            if isinstance(widget, tk.Label) or isinstance(widget, tk.Button) or isinstance(
                    widget, tk.Frame):
                widget.configure(bg=selected_theme["background"],
                                fg=selected_theme["foreground"])
            elif isinstance(widget, ttk.Combobox) or isinstance(widget,
                                                                ttk.Button) or \
                    isinstance(widget, ttk.Label) or isinstance(widget, ttk.Entry) or \
                    isinstance(widget, ttk.Treeview):
                widget.configure(style="TCombobox" if isinstance(widget,
                                                                ttk.Combobox) else
                                "TButton" if isinstance(widget, ttk.Button) else
                                "TLabel" if isinstance(widget, ttk.Label) else
                                "TEntry" if isinstance(widget, ttk.Entry) else
                                "Treeview")

def edit_question():
    global editing_question_index
    selected_item = question_list.selection()
    if not selected_item:
        return

    editing_question_index = question_list.index(selected_item)
    question_data = questions[editing_question_index]

    clear_fields()
    entry_question.insert(0, question_data["question"])
    for i, option in enumerate(question_data["options"]):
        globals()[f"entry_option_{i + 1}"].insert(0, option)
    correct_answer_var.set(question_data["answer"])

    add_button.config(text="Изменить вопрос", command=update_question)

def update_question():
    global editing_question_index
    if editing_question_index is None:
        return

    question = entry_question.get().strip()
    options = [entry_option_1.get().strip(), entry_option_2.get().strip(), entry_option_3.get().strip(),
               entry_option_4.get().strip(), entry_option_5.get().strip(), entry_option_6.get().strip()]
    options = [opt for opt in options if opt]
    correct_answer = correct_answer_var.get().strip()

    # Валидация (аналогично add_question)
    if not question:
        messagebox.showwarning("Ошибка", "Пожалуйста, введите вопрос.")
        return
    if not options:
        messagebox.showwarning("Ошибка", "Пожалуйста, введите хотя бы один вариант ответа.")
        return
    if len(options) < MIN_OPTIONS or len(options) > MAX_OPTIONS:
        messagebox.showwarning("Ошибка", f"Количество вариантов ответа должно быть от {MIN_OPTIONS} до {MAX_OPTIONS}.")
        return
    if not correct_answer:
        messagebox.showwarning("Ошибка", "Пожалуйста, укажите правильный ответ.")
        return
    if correct_answer not in options:
        messagebox.showwarning("Ошибка", "Правильный ответ не найден среди вариантов.")
        return

    questions[editing_question_index] = {
        "question": question,
        "options": options,
        "answer": correct_answer,
    }
    update_question_list()

    clear_fields()
    add_button.config(text="Добавить вопрос", command=add_question)
    editing_question_index = None

def update_question_list():
    question_list.delete(*question_list.get_children())
    for i, question_data in enumerate(questions):
        question_list.insert("", "end", values=(
            i + 1, question_data["question"]))

def on_question_select(event):
    selected_item = question_list.selection()
    if selected_item:
        edit_question()

def delete_question():
    selected_item = question_list.selection()
    if not selected_item:
        return

    index = question_list.index(selected_item)
    del questions[index]
    update_question_list()

def show_context_menu(event):
    selected_item = question_list.identify_row(event.y)
    if selected_item:
        question_list.selection_set(selected_item)
        context_menu.post(event.x_root, event.y_root)

def load_scenario():
    filepath = filedialog.askopenfilename(
        initialdir="scenarios",
        title="Выберите сценарий",
        filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
    )
    if not filepath:
        return

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            global questions
            questions = json.load(file)
            update_question_list()
            entry_title.delete(0, tk.END)
            entry_title.insert(0, os.path.splitext(
                os.path.basename(filepath))[0])
    except (FileNotFoundError, json.JSONDecodeError):
        messagebox.showerror("Ошибка", "Не удалось загрузить сценарий.")

def create_new_scenario():
    global questions
    questions = []
    update_question_list()
    entry_title.delete(0, tk.END)

def choose_mode():
    global themes  # Объявляем themes как глобальную
    settings = load_settings()
    themes = load_themes()
    selected_theme_name = settings.get("theme", "dark")

    mode_window = tk.Tk()  # Создаем отдельное окно для выбора режима
    mode_window.title("Выберите режим")

    apply_theme_to_window(mode_window, selected_theme_name)  # Применяем тему к окну выбора режима

    def on_mode_select(mode):
        mode_window.destroy()
        global app  # Объявляем app как глобальную переменную
        app = tk.Tk()  # Создаем основное окно после выбора режима
        app.title("Создание сценария викторины")
        app.geometry("900x600")

        # ... (остальной код инициализации приложения и виджетов)

        global questions
        questions = []
        global editing_question_index
        editing_question_index = None

        # --- Тема ---
        global themes # Объявляем themes как глобальную 
        settings = load_settings()
        themes = load_themes() # Загружаем темы
        selected_theme_name = settings.get("theme", "dark")

        apply_theme(selected_theme_name)

        # --- Список вопросов ---
        global question_list # Объявляем question_list как глобальную
        question_frame = tk.Frame(app)
        question_frame.pack(side=tk.LEFT, fill=tk.Y)

        question_list = ttk.Treeview(question_frame, columns=("№", "Вопрос"),
                                     show="headings")
        question_list.heading("№", text="№")
        question_list.heading("Вопрос", text="Вопрос")
        question_list.pack(expand=True, fill=tk.BOTH)
        question_list.bind("<Double-Button-1>", on_question_select)

        global context_menu # Объявляем context_menu как глобальную
        context_menu = tk.Menu(question_list, tearoff=0)
        context_menu.add_command(label="Редактировать", command=edit_question)
        context_menu.add_command(label="Удалить", command=delete_question)

        question_list.bind("<Button-3>", show_context_menu)

        # --- Остальные настройки ---
        global entry_title, entry_question, entry_option_1, entry_option_2, entry_option_3, entry_option_4, entry_option_5, entry_option_6, correct_answer_var, add_button # Объявляем виджеты как глобальные
        entry_frame = tk.Frame(app)
        entry_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(entry_frame, text="Заголовок сценария").pack()
        entry_title = ttk.Entry(entry_frame, width=65)
        entry_title.pack()

        ttk.Label(entry_frame, text="Вопрос").pack()
        entry_question = ttk.Entry(entry_frame, width=50)
        entry_question.pack()

        ttk.Label(entry_frame, text="Варианты ответа (от 2 до 6)").pack()
        entry_option_1 = ttk.Entry(entry_frame)
        entry_option_1.pack()
        entry_option_2 = ttk.Entry(entry_frame)
        entry_option_2.pack()
        entry_option_3 = ttk.Entry(entry_frame)
        entry_option_3.pack()
        entry_option_4 = ttk.Entry(entry_frame)
        entry_option_4.pack()
        entry_option_5 = ttk.Entry(entry_frame)
        entry_option_5.pack()
        entry_option_6 = ttk.Entry(entry_frame)
        entry_option_6.pack()

        ttk.Label(entry_frame, text="Правильный ответ (текст)").pack()
        correct_answer_var = tk.StringVar()
        entry_correct_answer = ttk.Entry(entry_frame, textvariable=correct_answer_var)
        entry_correct_answer.pack()

        ttk.Label(entry_frame, text="").pack()
        add_button = ttk.Button(entry_frame, text="Добавить вопрос",
                           command=add_question)
        add_button.pack()
        ttk.Label(entry_frame, text="").pack()
        ttk.Button(entry_frame, text="Сохранить сценарий",
                  command=save_scenario).pack()
        
        if mode == "create":
            create_new_scenario()
        elif mode == "edit":
            load_scenario()

        app.mainloop()  # Запускаем главный цикл основного окна

    ttk.Button(mode_window, text="Создать новый сценарий",
              command=lambda: on_mode_select("create")).pack(pady=10)
    ttk.Button(mode_window, text="Изменить существующий сценарий",
              command=lambda: on_mode_select("edit")).pack(pady=10)

    mode_window.mainloop()  # Запускаем главный цикл окна выбора режима

def apply_theme_to_window(window, theme_name): 
    """Применяет тему к указанному окну."""
    selected_theme = themes.get(theme_name)
    if selected_theme:
        window.configure(bg=selected_theme["background"])
        style = ttk.Style(window) # Создаем Style для конкретного окна
        style.theme_use("clam")

        # Настройка стилей для различных виджетов
        style.configure("TButton", background=selected_theme["button_background"],
                        foreground=selected_theme["foreground"],
                        activebackground=selected_theme["button_active_background"],
                        borderwidth=2,
                        relief="flat")
        # Настройка взаимодействия с элементами (active state)
        style.map("TButton",
                  background=[('active', selected_theme["button_active_background"])],
                  foreground=[('active', selected_theme["foreground"])],
                  bordercolor=[('active', selected_theme["foreground"])])
        # Применение стиля к виджетам
        for widget in window.winfo_children():
            if isinstance(widget, tk.Label) or isinstance(widget, tk.Button) or isinstance(
                    widget, tk.Frame):
                widget.configure(bg=selected_theme["background"],
                                fg=selected_theme["foreground"])
            elif isinstance(widget, ttk.Combobox) or isinstance(widget,
                                                                ttk.Button) or \
                    isinstance(widget, ttk.Label) or isinstance(widget, ttk.Entry) or \
                    isinstance(widget, ttk.Treeview):
                widget.configure(style="TButton" if isinstance(widget, ttk.Button) else
                                "Treeview")



choose_mode()  # Вызываем функцию выбора режима