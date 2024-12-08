import cv2
import os
import asyncio
import time
import json
from concurrent.futures import ThreadPoolExecutor
from ultralytics import YOLO
from datetime import datetime
import subprocess

# Загрузка модели
model = YOLO("last.pt")  # Изменено на last.pt

# Загрузка данных из data.json
with open('data.json', 'r') as f:
    data = json.load(f)

# Извлечение путей сохранения файлов и RTSP адресов
base_path = data.get("Path_file", "видео")  # Путь для сохранения видео
archive_dir = os.path.join(base_path, "Видеоархив")  # Папка "Видеоархив"
os.makedirs(archive_dir, exist_ok=True)

# Извлечение RTSP адресов
rtsp_streams = [value for key, value in data.items() if key.startswith("RTSP_Adres")]

# Функция для получения текущей даты 
def get_current_date_folder():
    return datetime.now().strftime("%Y-%m-%d")

# Функция для обработки видеопотока
def process_stream(rtsp_url, stream_number):
    record_counter = 1  # Счетчик видео
    recording = False  # Флаг записи

    # Получение текущей даты для создания папки
    current_date_folder = get_current_date_folder()
    date_folder_path = os.path.join(archive_dir, current_date_folder)
    os.makedirs(date_folder_path, exist_ok=True)

    while True:
        cap = cv2.VideoCapture(rtsp_url)  # Открытие RTSP потока
        if not cap.isOpened():
            print(f"Не удалось открыть поток {stream_number}. Повторная попытка через 1 секунду.")
            time.sleep(1)  # Задержка перед повторной попыткой
            continue

        # Определяем параметры кодирования видео
        video_filename = os.path.join(date_folder_path, f"Камера{stream_number:02d}_{record_counter:02d}.avi")
        
        # Запуск FFmpeg для записи видео
        ffmpeg_command = [
            'ffmpeg',
            '-y',  # Перезаписывать выходной файл
            '-f', 'rawvideo',
            '-pixel_format', 'bgr24',
            '-video_size', f"{int(cap.get(3))}x{int(cap.get(4))}",
            '-framerate', '15',
            '-i', '-',  # Входные данные будут переданы через stdin
            '-c:v', 'mpeg4',
            '-an',
            video_filename
        ]
        #запуск ffmpeg
        process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

        while True:
            ret, frame = cap.read()  # Чтение кадра из потока
            if not ret: #Если не получилось получить кадр
                print(f"Не удалось получить кадр из потока {stream_number}. Начинаем новую запись.")
                if recording:
                    process.stdin.close()  # Закрываем stdin для FFmpeg
                    process.wait()  # Ждем завершения процесса
                    recording = False  # Сбрасываем флаг записи
                cap.release()  # Освобождение захвата видео
                break  # Выход из внутреннего цикла для повторного подключения к потоку

            # Выполнение предсказания на текущем кадре
            results = model(frame, stream=True, conf=0.5)
            # Определение цветов для классов
            colors = {
                "Mycop": (255, 0, 0),  # Синий
                "Chelovek": (255, 192, 203),  # Розовый
                "Chelovek c Mycopom": (173, 216, 230),  # Голубой
                "Mycop na zemlyu": (0, 0, 255),  # Красный
                "chelovek": (255, 228, 196),  # Бежевый
                "Mycop v mycopky": (0, 255, 0)  # Зеленый
            }

            # Внутри цикла обработки обнаруженных объектов
            detected_classes = set()  # Множество для хранения обнаруженных классов
            for result in results:
                if result.boxes:
                    for detection in result.boxes.data:  # Проходим по всем обнаруженным объектам
                        class_id = int(detection[5])  # Индекс класса
                        class_name = model.names[class_id]  # Получаем имя класса по его ID
                        detected_classes.add(class_name)  # Добавляем класс в множество

                        # Определяем цвет для текущего класса
                        color = colors.get(class_name, (255, 255, 255))

                        # Рисуем прямоугольник и метку на кадре
                        x1, y1, x2, y2 = map(int, detection[:4])  # Координаты бокса
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(frame, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Проверяем, обнаружены ли нужные классы
            if any(cls in detected_classes for cls in ["Chelovek", "Chelovek c Mycopom", "Mycop v mycopky", "Mycop na zemlyu", "Mycop"]):
                if not recording:  # Если запись еще не начата
                    recording = True  # Устанавливаем флаг записи
                    print(f"Начинаем запись на потоке {stream_number}.")
                    record_counter += 1 
                process.stdin.write(frame.tobytes())
                  # Увеличиваем счетчик записи
            else:
                if recording:
                    
                    for i in range(50):
                        ret, frame = cap.read()
                        if not ret:
                            break
                        detected_classes = set()  # Сбрасываем множество для нового кадра
                        # Здесь должен быть код для получения результатов обнаружения для текущего кадра
                        results = model(frame)  # Предполагается, что у вас есть модель для обработки кадра
                        if results:
                            for result in results:
                                if result.boxes:
                                    for detection in result.boxes.data:  # Проходим по всем обнаруженным объектам
                                        class_id = int(detection[5])  # Индекс класса
                                        class_name = model.names[class_id]  # Получаем имя класса по его ID
                                        detected_classes.add(class_name)  # Добавляем класс в множество
                                        # Определяем цвет для текущего класса
                                        color = colors.get(class_name, (255, 255, 255))
                                        # Рисуем прямоугольник и метку на кадре
                                        x1, y1, x2, y2 = map(int, detection[:4])  # Координаты бокса
                                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                                        cv2.putText(frame, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


                        # Отправка кадра в FFmpeg

                        process.stdin.write(frame.tobytes())
                    process.stdin.close()  # Закрываем stdin для FFmpeg
                    process.wait()  # Ждем завершения процесса
                    recording = False  # Сбрасываем флаг записи
                    print(f"Запись остановлена на потоке {stream_number}.")

        # Освобождение ресурсов и подготовка к новой записи
        print(f"Поток {stream_number} закрыт. Попытка переподключения...")
        

async def main():
    # Создание пула потоков
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, process_stream, rtsp_url, i)
            for i, rtsp_url in enumerate(rtsp_streams, start=1)
        ]
        await asyncio.gather(*tasks)

# Запуск асинхронной функции main
if __name__ == "__main__":
    asyncio.run(main())