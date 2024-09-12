import tkinter as tk
from tkinter import messagebox, ttk
import json
import sys
import random
import threading
import os
import pygame
import time
import cv2  # Для воспроизведения видео
from PIL import Image, ImageTk  # Для отображения GIF

# Инициализация модуля микширования звука
pygame.mixer.init()


# Функция для воспроизведения звука
def play_sound(sound_path):
    pygame.mixer.music.load(sound_path)
    pygame.mixer.music.play()


def load_scenario(scenario_file):
    with open(os.path.join("scenarios", scenario_file), "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


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


def check_files():
    """Проверяет наличие необходимых файлов и папок."""
    errors = []

    # Проверка папки resources
    if not os.path.exists("resources"):
        errors.append("Папка 'resources' не найдена.")
    else:
        # Проверка папки sounds
        if not os.path.exists(os.path.join("resources", "sounds")):
            errors.append("Папка 'resources/sounds' не найдена.")
        else:
            # Проверка файлов звуков
            if not os.path.exists(os.path.join("resources", "sounds", "correct.wav")):
                errors.append("Файл 'resources/sounds/correct.wav' не найден.")
            if not os.path.exists(os.path.join("resources", "sounds", "incorrect.wav")):
                errors.append("Файл 'resources/sounds/incorrect.wav' не найден.")

        # Проверка папки data
        if not os.path.exists(os.path.join("resources", "data")):
            errors.append("Папка 'resources/data' не найдена.")
        else:
            # Проверка папок win и lose
            if not os.path.exists(os.path.join("resources", "data", "win")):
                errors.append("Папка 'resources/data/win' не найдена.")
            if not os.path.exists(os.path.join("resources", "data", "lose")):
                errors.append("Папка 'resources/data/lose' не найдена.")

    # Проверка папки scenarios
    if not os.path.exists("scenarios"):
        errors.append("Папка 'scenarios' не найдена.")

    if errors:
        error_message = "\n".join(errors)
        messagebox.showerror("Ошибка", f"Необходимые файлы или папки не найдены:\n{error_message}")
        app.quit()

# Объявление timer_id как глобальной переменной
timer_id = None

def check_answer(selected_button):
    global current_question_index, score, game_over, timer_id, user_answers

    if game_over:
        return

    if timer_id:
        app.after_cancel(timer_id)  # Остановка таймера при ответе

    correct_answer = questions[current_question_index]["answer"]
    selected_option = selected_button['text'] if selected_button else "Не выбран"

    # Сохраняем информацию о вопросе, выбранном и правильном ответе
    user_answers.append((questions[current_question_index]["question"], selected_option, correct_answer))

    # Отключение кнопок
    for btn in option_buttons:
        btn.config(state=tk.DISABLED)

    # Найти кнопку с правильным ответом
    correct_button = None
    for btn in option_buttons:
        if btn['text'] == correct_answer:
            correct_button = btn
            break

    # Подсветка кнопок в зависимости от правильности ответа
    if selected_button:
        selected_button.config(bg=theme["incorrect_answer_background"])  # Цвет неправильного ответа из темы
    if correct_button:
        correct_button.config(bg=theme["correct_answer_background"])  # Цвет правильного ответа из темы

    if selected_option == correct_answer:
        score += 1
        if encouragement_enabled:
            show_encouragement(True)  # Показать поощрение за правильный ответ
        elif sound_enabled and correct_sound:  # Воспроизводим звук только если поощрение отключено
            try:
                play_sound(correct_sound)
            except Exception as e:
                print(f"Ошибка воспроизведения звука: {e}")
    else:
        if encouragement_enabled:
            show_encouragement(False)  # Показать поощрение за неправильный ответ
        elif sound_enabled and incorrect_sound:  # Воспроизводим звук только если поощрение отключено
            try:
                play_sound(incorrect_sound)
            except Exception as e:
                print(f"Ошибка воспроизведения звука: {e}")
        if game_mode == "Режим выживания":
            game_over = True
            if timer_id:
                app.after_cancel(timer_id)  # Остановить таймер
            app.after(2500, show_results)  # Показать результаты после 2.5 секунд
            return

    # Обновление счёта на экране
    score_label.config(text=f"Счет: {score}")

    # Переход к следующему вопросу или завершение игры
    current_question_index += 1
    if current_question_index < len(questions):
        app.after(2500, show_question)  # Показать следующий вопрос через 2.5 секунд
    else:
        game_over = True
        if timer_id:
            app.after_cancel(timer_id)  # Остановить таймер
        app.after(2500, show_results)  # Показать результаты после 2.5 секунд


def show_question():
    global timer_label, timer_id

    if current_question_index >= len(questions):
        return

    question = questions[current_question_index]
    question_label.config(text=question["question"])

    options = question["options"]
    random.shuffle(options)

    # Очистка старых кнопок перед отображением новых
    for btn in option_buttons:
        btn.grid_forget()
        btn.config(bg=theme["button_background"], state=tk.NORMAL)  # Цвет фона кнопки из темы

    # Размещение кнопок в два столбика
    num_options = len(options)
    for i, option in enumerate(options):
        row = i // 2
        col = i % 2
        option_buttons[i].config(text=option)
        option_buttons[i].grid(row=row + 2, column=col, padx=10, pady=5, sticky="nsew")

    # Если количество кнопок нечетное, последнюю кнопку растянуть на два столбика
    if num_options % 2 != 0:
        option_buttons[num_options - 1].grid(columnspan=2)

    # Сброс и запуск таймера, если игра идет на время
    if game_mode == "На время":
        global time_remaining
        time_remaining = timer_duration  # Установка таймера из настроек
        timer_label.config(text=f"Оставшееся время: {time_remaining // 60} мин. {time_remaining % 60} сек.")
        if timer_id:
            app.after_cancel(timer_id)  # Остановить предыдущий таймер
        timer_id = app.after(1000, countdown, time_remaining)


def countdown(time_left):
    global timer_id

    if time_left > 0:
        if app.winfo_exists():  # Проверка, что окно еще существует
            timer_label.config(text=f"Оставшееся время: {time_left // 60} мин. {time_left % 60} сек.")
            timer_id = app.after(1000, countdown, time_left - 1)
        else:
            # Остановка таймера, если окно закрыто
            pass
    else:
        if app.winfo_exists():  # Проверка, что окно еще существует
            messagebox.showinfo("Время вышло!", "Вы не успели ответить на вопрос.")
            check_answer(None)  # Засчитать ответ как неправильный


def show_results():
    result_window = tk.Toplevel(app)
    result_window.title("Результаты игры")
    result_window.geometry("600x400")
    result_window.configure(bg=theme["background"])

    # Закрытие всей викторины при закрытии окна результатов
    result_window.protocol("WM_DELETE_WINDOW", app.quit)

    style = ttk.Style()  # Создаем объект Style для ttk виджетов
    style.theme_use("clam")  # Используем тему "clam" как основу (можно изменить на другую)
    style.configure("TLabel", background=theme["background"], foreground=theme["foreground"])

    header = ttk.Label(result_window, text="Результаты", font=("Arial", 16, "bold"), style="TLabel")
    header.pack(pady=10)

    # Создаем таблицу с результатами
    result_frame = tk.Frame(result_window, bg=theme["background"])
    result_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    # Создаем заголовки таблицы
    headers = ["Вопрос", "Ваш ответ", "Правильный ответ"]
    for col, header_text in enumerate(headers):
        ttk.Label(result_frame, text=header_text, font=("Arial", 12, "bold"), style="TLabel",
                  borderwidth=1, relief="solid").grid(row=0, column=col, sticky="nsew", padx=5,
                                                      pady=5)  # Используем grid для padx и pady

    # Заполняем таблицу результатами
    for i, (question, user_answer, correct_answer) in enumerate(user_answers):
        ttk.Label(result_frame, text=question, style="TLabel",
                  borderwidth=1, relief="solid").grid(row=i + 1, column=0, sticky="nsew", padx=5,
                                                      pady=5)  # Используем grid для padx и pady
        ttk.Label(result_frame, text=user_answer, style="TLabel",
                  borderwidth=1, relief="solid").grid(row=i + 1, column=1, sticky="nsew", padx=5,
                                                      pady=5)  # Используем grid для padx и pady
        ttk.Label(result_frame, text=correct_answer, style="TLabel",
                  borderwidth=1, relief="solid").grid(row=i + 1, column=2, sticky="nsew", padx=5,
                                                      pady=5)  # Используем grid для padx и pady

    # Настройка растягивания строк и столбцов
    for i in range(len(headers)):
        result_frame.grid_columnconfigure(i, weight=1)
    for i in range(len(user_answers) + 1):
        result_frame.grid_rowconfigure(i, weight=1)

    result_window.mainloop()


# Объявление encouragement_files как глобальной переменной
encouragement_files = {}

def load_encouragement_files():
    """Загружает файлы поощрения из папок win и lose."""
    global encouragement_files  # Используем глобальный словарь

    encouragement_files = {
        "win": [],
        "lose": []
    }

    for folder in ["win", "lose"]:
        folder_path = os.path.join("resources", "data", folder)
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if file.endswith((".mp4", ".gif")):
                    encouragement_files[folder].append(os.path.join(folder_path, file))

    # Вывод списка файлов в терминал для отладки
    print("Файлы поощрения:")
    for folder, files in encouragement_files.items():
        print(f"{folder}: {files}")

    return encouragement_files


def show_encouragement(is_correct):
    global encouragement_files  # Используем глобальный словарь

    # Создаем новое окно поверх основного
    encouragement_window = tk.Toplevel(app)
    encouragement_window.overrideredirect(True)  # Убираем рамку окна
    encouragement_window.attributes('-topmost', True)  # Делаем окно поверх всех остальных

    # Выбираем случайный файл из списка
    if is_correct:
        file_path = random.choice(encouragement_files["win"])
    else:
        file_path = random.choice(encouragement_files["lose"])

    print(f"Выбранный файл поощрения: {file_path}")  # Добавляем вывод

    # Отображаем видео или GIF
    if file_path.endswith('.mp4'):
        # Если это видео, используем cv2 для воспроизведения
        try:
            video = cv2.VideoCapture(file_path)
            fps = video.get(cv2.CAP_PROP_FPS)
            frame_delay = int(1000 / fps)  # Задержка между кадрами в миллисекундах

            # Размер видео (уменьшаем на 50%)
            video_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH) * 0.5)
            video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT) * 0.5)

            # Центрируем видео
            x = (app.winfo_screenwidth() - video_width) // 2
            y = (app.winfo_screenheight() - video_height) // 2

            encouragement_window.geometry(f"{video_width}x{video_height}+{x}+{y}")

            # Создаем холст для отображения видео
            canvas = tk.Canvas(encouragement_window, width=video_width, height=video_height)
            canvas.pack()

            # Функция для обновления кадра видео
            def update_frame():
                ret, frame = video.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Преобразуем BGR в RGB
                    photo = ImageTk.PhotoImage(image=Image.fromarray(frame).resize((video_width, video_height)))
                    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                    canvas.image = photo  # Сохраняем ссылку на изображение
                    app.after(frame_delay, update_frame)
                else:
                    video.release()
                    encouragement_window.destroy()

            # Начинаем воспроизведение
            update_frame()

        except Exception as e:
            print(f"Ошибка воспроизведения видео: {e}")

    elif file_path.endswith('.gif'):
        # Если это GIF, используем PIL для отображения
        try:
            gif = Image.open(file_path)

            # Получаем размеры GIF
            gif_width, gif_height = gif.size

            # Центрируем GIF
            x = (app.winfo_screenwidth() - gif_width) // 2
            y = (app.winfo_screenheight() - gif_height) // 2

            encouragement_window.geometry(f"{gif_width}x{gif_height}+{x}+{y}")

            # Создаем метку для отображения GIF
            label = tk.Label(encouragement_window)
            label.pack()

            # Функция для обновления кадра GIF
            def update_gif_frame(frame_index=0):
                try:
                    gif.seek(frame_index)
                    photo = ImageTk.PhotoImage(gif)
                    label.config(image=photo)
                    label.image = photo  # Сохраняем ссылку на изображение
                    app.after(gif.info['duration'], update_gif_frame, frame_index + 1)
                except EOFError:
                    encouragement_window.destroy()

            # Начинаем воспроизведение
            update_gif_frame()

        except Exception as e:
            print(f"Ошибка отображения GIF: {e}")

    encouragement_window.update()  # Обновляем окно поощрения


settings = json.loads(sys.argv[1])
scenario_file = settings["scenario"]
game_mode = settings["mode"]
sound_enabled = settings["sound_enabled"]
encouragement_enabled = settings["encouragement_enabled"]  # Получаем настройку поощрения
correct_sound = settings["correct_sound"]
incorrect_sound = settings["incorrect_sound"]
timer_duration = settings.get("timer_duration", 60)  # По умолчанию 60 секунд, если не указано
selected_theme_name = settings.get("theme", "dark")  # Получаем имя выбранной темы

themes = load_themes()
theme = themes.get(selected_theme_name, themes["dark"])  # Получаем данные темы, по умолчанию темная

# Проверка файлов перед запуском игры
check_files()

questions = load_scenario(scenario_file)

# Запуск вопросов в случайном порядке
random.shuffle(questions)

current_question_index = 0
score = 0
game_over = False
timer_thread = None
user_answers = []  # Хранение информации о вопросах, ответах и правильных ответах

app = tk.Tk()
app.title("Викторина")

# Установить окно на весь экран
app.attributes("-fullscreen", True)
app.configure(bg=theme["background"])  # Цвет фона из темы

# Использование grid для размещения элементов на экране
main_frame = tk.Frame(app, bg=theme["background"])
main_frame.grid(row=1, column=0, columnspan=3, pady=20, sticky="nsew")

question_label = tk.Label(main_frame, text="", wraplength=800, font=("Arial", 14), fg=theme["foreground"],
                           bg=theme["background"])
question_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="nsew")

option_buttons = []
for i in range(6):
    btn = tk.Button(main_frame, text="", font=("Arial", 12), bg=theme["button_background"], fg=theme["foreground"],
                    activebackground=theme["button_active_background"],
                    command=lambda button=i: check_answer(option_buttons[button]))
    option_buttons.append(btn)

# Счет слева снизу
score_label = tk.Label(app, text=f"Счет: {score}", font=("Arial", 12), fg=theme["foreground"], bg=theme["background"])
score_label.grid(row=3, column=0, padx=20, pady=20, sticky="sw")

# Таймер справа снизу
timer_label = tk.Label(app, text="", font=("Arial", 12), fg=theme["foreground"], bg=theme["background"])
timer_label.grid(row=3, column=2, padx=20, pady=20, sticky="se")

# Загрузка файлов поощрения при запуске
encouragement_files = load_encouragement_files()

# Настройка растягивания строк и столбцов
app.grid_rowconfigure(0, weight=1)
app.grid_rowconfigure(1, weight=10)
app.grid_rowconfigure(2, weight=1)
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=10)
app.grid_columnconfigure(2, weight=1)

# Настройка растягивания строк и столбцов внутри main_frame
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_rowconfigure(2, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

# Обеспечить растяжение кнопок
for row in range(3):
    main_frame.grid_rowconfigure(row + 2, weight=1)  # Растягиваем строки для кнопок
for col in range(2):
    main_frame.grid_columnconfigure(col, weight=1)  # Растягиваем столбцы для кнопок

show_question()
app.mainloop()