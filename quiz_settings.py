import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import subprocess
import sys
import pygame
import threading


pygame.mixer.init()


def load_settings():
    settings_path = os.path.join("resources", "settings.json")
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    else:
        return {}


def save_settings():
    settings_path = os.path.join("resources", "settings.json")
    os.makedirs("resources", exist_ok=True)
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "theme": theme_var.get(),
                "game_mode": game_mode_var.get(),
                "timer_duration": timer_entry.get(),
                "sound_enabled": sound_var.get(),
                "encouragement_enabled": encouragement_var.get(),  # Добавляем сохранение настройки поощрения
            },
            f,
            indent=4,
        )


def load_themes():
    themes_path = os.path.join("resources", "themes.json")
    if os.path.exists(themes_path):
        with open(themes_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    else:
        return {}


def load_scenarios():
    scenarios_path = "scenarios"
    scenario_files = [f for f in os.listdir(scenarios_path) if f.endswith(".json")]

    scenario_titles = []
    for file in scenario_files:
        try:
            with open(os.path.join(scenarios_path, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                if data and "question" in data[0]:
                    scenario_titles.append((file, data[0]["question"]))
        except json.JSONDecodeError:
            if messagebox.askyesno("Ошибка", f"Файл сценария '{file}' поврежден. Удалить его?"):
                try:
                    os.remove(os.path.join(scenarios_path, file))
                    print(f"Файл '{file}' удален.")
                except OSError as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить файл '{file}': {e}")
            else:
                print(f"Файл '{file}' пропущен.")

    return scenario_titles


def play_sound(sound_path):
    pygame.mixer.music.load(sound_path)
    pygame.mixer.music.play()


def start_quiz():
    selected_scenario = scenario_var.get()
    game_mode = game_mode_var.get()
    sound_enabled = sound_var.get()
    encouragement_enabled = encouragement_var.get()  # Получаем значение настройки поощрения
    timer_duration = timer_entry.get() if game_mode == "На время" else 60

    correct_sound = os.path.join("resources", "sounds", "correct.wav")
    incorrect_sound = os.path.join("resources", "sounds", "incorrect.wav")

    if not selected_scenario:
        messagebox.showwarning("Ошибка", "Пожалуйста, выберите сценарий.")
        return

    try:
        timer_duration = int(timer_duration)
        if not 5 <= timer_duration <= 300:
            raise ValueError
    except ValueError:
        messagebox.showwarning(
            "Ошибка", "Введите корректное время таймера (от 5 до 300 секунд)."
        )
        return

    settings = {
        "scenario": selected_scenario,
        "mode": game_mode,
        "sound_enabled": sound_enabled,
        "encouragement_enabled": encouragement_enabled,  # Передаем настройку поощрения в quiz_game.py
        "correct_sound": correct_sound,
        "incorrect_sound": incorrect_sound,
        "timer_duration": timer_duration,
        "theme": theme_var.get(),
    }

    try:
        subprocess.Popen([sys.executable, "quiz_game.py", json.dumps(settings)])
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось запустить викторину: {e}")


def open_converter():
    try:
        subprocess.Popen([sys.executable, "Converts.py"])
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось запустить конвертор: {e}")


def open_scenario_editor():
    try:
        subprocess.Popen([sys.executable, "quiz_creator.py"])
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось запустить редактор сценариев: {e}")


def toggle_timer_entry():
    if game_mode_var.get() == "На время":
        timer_frame.pack()
    else:
        timer_frame.pack_forget()


app = tk.Tk()
app.title("Настройки викторины")
app.geometry("500x500")

scenarios = load_scenarios()

# Загружаем настройки
settings = load_settings()

themes = load_themes()
default_theme = list(themes.keys())[0] if themes else "dark"
# Применяем загруженные настройки
theme_var = tk.StringVar(value=settings.get("theme", default_theme))
game_mode_var = tk.StringVar(value=settings.get("game_mode", "Обычный"))
sound_var = tk.BooleanVar(value=settings.get("sound_enabled", True))
encouragement_var = tk.BooleanVar(value=settings.get("encouragement_enabled", True))  # Загружаем настройку поощрения
scenario_var = tk.StringVar(value=settings.get("scenario", ""))


def toggle_theme():
    selected_theme = themes.get(theme_var.get())
    if selected_theme:
        app.configure(bg=selected_theme["background"])
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TCombobox",
            fieldbackground=selected_theme["background"],
            selectbackground=selected_theme["button_active_background"],
            background=selected_theme["button_background"],
            foreground=selected_theme["foreground"],
            borderwidth=2,
            relief="flat",
        )
        style.configure(
            "TButton",
            background=selected_theme["button_background"],
            foreground=selected_theme["foreground"],
            activebackground=selected_theme["button_active_background"],
            borderwidth=2,
            relief="flat",
        )
        style.map(
            "TCombobox",
            background=[("active", selected_theme["button_active_background"])],
            foreground=[("active", selected_theme["foreground"])],
            bordercolor=[("active", selected_theme["foreground"])],
        )

        style.configure(
            "TRadiobutton",
            background=selected_theme["background"],
            foreground=selected_theme["foreground"],
            relief="flat",
            borderwidth=2,
        )
        style.map(
            "TRadiobutton",
            relief=[("active", "solid")],
            background=[("active", selected_theme["background"])],
            foreground=[("active", selected_theme["foreground"])],
            bordercolor=[("active", selected_theme["foreground"])],
        )

        style.configure(
            "TLabel",
            background=selected_theme["background"],
            foreground=selected_theme["foreground"],
        )
        style.configure(
            "TCheckbutton",
            background=selected_theme["background"],
            foreground=selected_theme["foreground"],
        )

        for widget in app.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=selected_theme["background"])
            elif isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
                widget.configure(
                    bg=selected_theme["background"], fg=selected_theme["foreground"]
                )
            elif (
                    isinstance(widget, ttk.Combobox)
                    or isinstance(widget, ttk.Button)
                    or isinstance(widget, ttk.Label)
                    or isinstance(widget, ttk.Radiobutton)
                    or isinstance(widget, ttk.Checkbutton)
            ):
                widget.configure(
                    style="TCombobox"
                    if isinstance(widget, ttk.Combobox)
                    else "TButton"
                    if isinstance(widget, ttk.Button)
                    else "TLabel"
                    if isinstance(widget, ttk.Label)
                    else "TRadiobutton"
                    if isinstance(widget, ttk.Radiobutton)
                    else "TCheckbutton"
                )

    save_settings()


ttk.Label(app, text="Выберите тему").pack()

theme_combobox = ttk.Combobox(app, textvariable=theme_var, values=list(themes.keys()))
theme_combobox.pack()
theme_combobox.bind("<<ComboboxSelected>>", lambda event: toggle_theme())

ttk.Label(app, text="Выберите сценарий").pack()
scenario_var = tk.StringVar()
scenario_combobox = ttk.Combobox(app, textvariable=scenario_var)
scenario_combobox["values"] = [s[0] for s in scenarios]
scenario_combobox.pack()

ttk.Label(app, text="Выберите режим игры").pack()
game_mode_var = tk.StringVar(value=settings.get("game_mode", "Обычный"))
game_mode_frame = tk.Frame(app)
game_mode_frame.pack()
modes = ["Обычный", "На время", "Режим выживания"]
for mode in modes:
    ttk.Radiobutton(
        game_mode_frame,
        text=mode,
        variable=game_mode_var,
        value=mode,
        command=toggle_timer_entry
    ).pack(anchor=tk.W)

# Загружаем настройку звука из файла настроек
sound_var = tk.BooleanVar(value=settings.get("sound_enabled", True))
ttk.Checkbutton(app, text="Включить звук", variable=sound_var, command=save_settings).pack()

# Добавляем настройку поощрения
ttk.Checkbutton(app, text="Включить поощрение", variable=encouragement_var, command=save_settings).pack()

timer_frame = tk.Frame(app)
ttk.Label(timer_frame, text="Время таймера (в секундах):").pack(side=tk.LEFT)
timer_entry = ttk.Entry(timer_frame, width=5)
timer_entry.pack(side=tk.LEFT)
# Применяем загруженные настройки к полю ввода таймера
timer_entry.insert(0, settings.get("timer_duration", "60"))
toggle_timer_entry()  # Скрываем или показываем поле ввода в зависимости от загруженного режима

if scenario_var.get() in scenario_combobox["values"]:
    scenario_combobox.current(scenario_combobox["values"].index(scenario_var.get()))

tk.Button(app, text="Запустить конвертор", command=open_converter).pack()
tk.Button(app, text="Создать/изменить сценарий", command=open_scenario_editor).pack()


def start_quiz_and_save_settings():
    start_quiz()
    save_settings()


tk.Button(app, text="Начать викторину", command=start_quiz_and_save_settings).pack()

toggle_theme()
app.mainloop()

pygame.mixer.quit()