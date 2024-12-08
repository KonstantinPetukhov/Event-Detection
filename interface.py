import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
import subprocess
import os
from notifypy import Notify
import re  # Импортируем модуль для регулярных выражений

# Создаем основное окно
app = ctk.CTk()
app.title("Приложение")
app.geometry("480x480")
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("dark-blue")  

# Переменная для хранения процесса
process = None

# Функция для открытия диалогового окна выбора папки
def browse_directory():
    folder_selected = filedialog.askdirectory()
    entry1.delete(0, ctk.END)  # Очищаем текущее значение в поле
    entry1.insert(0, folder_selected)  # Вставляем выбранный путь
    check_fields()  # Проверяем поля после выбора папки

# Функция для добавления новых полей ввода
def add_entry():
    global entry_count
    if entry_count < 6:  # Проверяем, не превышает ли количество полей 6
        entry_count += 1
        new_entry = ctk.CTkEntry(frame3, placeholder_text="Введите rtsp-адрес камеры", width=300)
        new_entry.pack(side=ctk.TOP, padx=(0, 110), pady=(0, 10))  # Отступы сверху и снизу
        new_entry.bind("<KeyRelease>", lambda event: check_fields())  # Проверяем поля при вводе

        # Если количество полей равно 6, отключаем кнопку "+"
        if entry_count == 6:
            plus_button.configure(state="disabled")

        # Если кнопка "-" еще не создана, создаем ее
        if entry_count == 1:
            create_remove_button()

        check_fields()  # Проверяем поля после добавления нового

# Функция для создания кнопки "-"
def create_remove_button():
    global remove_button
    remove_button = ctk.CTkButton(frame2, text="-", command=remove_entry, width=50, hover_color="white", fg_color="gray", text_color="black")
    remove_button.place(relx=1.0, x=-20, y=0, anchor='ne')  # Размещаем кнопку в правом верхнем углу фрейма

# Функция для удаления последнего поля ввода
def remove_entry():
    global entry_count
    if entry_count > 0:  # Проверяем, есть ли поля для удаления
        entry_count -= 1
        # Удаляем последнее добавленное поле
        if frame3.winfo_children():
            frame3.winfo_children()[-1].destroy()  # Удаляем последнее поле

        # Если количество полей стало 0, скрываем кнопку "-"
        if entry_count == 0:
            remove_button.place_forget()  # Скрываем кнопку "-"
            plus_button.configure(state="normal")  # Включаем кнопку "+"

        check_fields()  # Проверяем поля после удаления

# Функция для проверки заполненности полей
def check_fields():
    path_file = entry1.get().strip()
    rtsp_address = entry2.get().strip()
    rtsp_list = [entry.get() for entry in frame3.winfo_children()]

    # Проверяем, является ли путь действительным
    if not os.path.isdir(path_file):
        messagebox.showerror("Ошибка", "Введенный путь не является действительным. Пожалуйста, выберите другой путь.")
        run_button.configure(state="disabled")  # Блокируем кнопку "Запустить"
        return

    # Проверяем, заполнены ли все необходимые поля
    if path_file and rtsp_address and all(rtsp.strip() for rtsp in rtsp_list):
        run_button.configure(state="normal")  # Разблокируем кнопку "Запустить"
    else:
        run_button.configure(state="disabled")  # Блокируем кнопку "Запустить"

# Функция для проверки формата RTSP-адреса
def is_valid_rtsp(rtsp):
    rtsp_pattern = re.compile(r'^rtsp://.+')  # Простой пат терн для проверки RTSP-адреса
    return bool(rtsp_pattern.match(rtsp))

# Функция для сохранения данных в JSON файл
def save_to_json():
    global process
    path_file = entry1.get()  # Получаем путь из entry1
    rtsp_address = entry2.get()
    rtsp_list = [entry.get() for entry in frame3.winfo_children()]

    # Проверяем действительность RTSP-адресов
    if not is_valid_rtsp(rtsp_address):
        messagebox.showerror("Ошибка", "Второй RTSP-адрес недействителен. Пожалуйста, введите корректный адрес.")
        return

    for rtsp in rtsp_list:
        if not is_valid_rtsp(rtsp):
            messagebox.showerror("Ошибка", "Один или несколько дополнительных RTSP-адресов недействительны. Пожалуйста, введите корректные адреса.")
            return

    notification = Notify()
    notification.title = "Запуск приложения"
    notification.message = "Приложение было запущано"
    notification.send()
    data = {
        "Path_file": path_file,
        "RTSP_Adres": rtsp_address,
    }

    # Добавляем rtsp адреса из дополнительных полей
    for i, rtsp in enumerate(rtsp_list):
        data[f"RTSP_ Adres_{i+2}"] = rtsp

    # Сохраняем данные в JSON файл в текущей директории
    json_file_path = os.path.join(os.getcwd(), 'data.json')
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    # Запускаем процесс
    process = subprocess.Popen(["python", "detection.py"])
    stop_button.configure(state="normal")  # Разблокируем кнопку "Стоп"

# Функция для завершения процесса
def stop_process():
    global process
    if process:
        # Завершаем процесс
        process.terminate()
        process = None
        stop_button.configure(state="disabled")  # Блокируем кнопку "Стоп"

frame = ctk.CTkFrame(app, fg_color="transparent")
frame.pack(pady=(20, 10))
frame2 = ctk.CTkFrame(app, fg_color="transparent")
frame2.pack(pady=(20, 10), fill="x")
frame3 = ctk.CTkFrame(app, fg_color="transparent")  # Новый фрейм для дополнительных полей
frame3.pack(pady=(10, 10))

# Создаем первое поле ввода
entry1 = ctk.CTkEntry(frame, placeholder_text="Введите путь сохранения", width=300)
entry1.pack(side=ctk.LEFT, pady=(20, 10))  # Размещаем поле ввода слева
entry1.bind("<KeyRelease>", lambda event: check_fields())  # Проверяем поля при вводе

# Создаем кнопку "Обзор"
browse_button = ctk.CTkButton(frame, text="Обзор", command=browse_directory, width=100, hover_color="white", fg_color="gray", text_color="black")
browse_button.pack(side=ctk.LEFT, padx=(10, 0), pady=(10, 0))  # Размещаем кнопку справа от поля ввода

# Создаем второе поле ввода
entry2 = ctk.CTkEntry(frame2, placeholder_text="Введите rtsp-адрес камеры", width=300)
entry2.pack(side=ctk.LEFT, padx=(35, 0))  # Отступы сверху и снизу
entry2.bind("<KeyRelease>", lambda event: check_fields())  # Проверяем поля при вводе

# Инициализируем счетчик полей
entry_count = 0

# Создаем кнопку "+"
plus_button = ctk.CTkButton(frame2, text="+", command=add_entry, width=50, hover_color="white", fg_color="gray", text_color="black")
plus_button.pack(side=ctk.RIGHT, padx=(0, 85), pady=(0, 0))  # Размещаем кнопку справа от второго поля ввода

# Создаем кнопку "Стоп" и фиксируем её на месте
stop_button = ctk.CTkButton(app, text="Стоп", command=stop_process, width=100, hover_color="white", fg_color="red", text_color="black", state="disabled")
stop_button.pack(side=ctk.BOTTOM, pady=(0, 0), padx=(0, 0))  # Размещаем кнопку "Стоп" под кнопкой "Запустить"

# Создаем кнопку "Запустить" и фиксируем её на месте
run_button = ctk.CTkButton(app, text="Запустить", command=save_to_json, width=100, hover_color="white", fg_color="green", text_color="black", state="disabled")
run_button.pack(side=ctk.BOTTOM, pady=(20, 10))  # Размещаем кнопку внизу по центру

app.resizable(False, False)  # Запускаем основной цикл приложения
app.mainloop() 