import cv2
import asyncio
import json
import time
import os
from datetime import datetime
from ultralytics import YOLO
from concurrent.futures import ThreadPoolExecutor

# Загрузка модели
model = YOLO('last.pt')

# Функция для загрузки данных из JSON файла
def load_rtsp_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

# Загрузка RTSP адресов и пути для сохранения видео
data = load_rtsp_data('data.json')
rtsp_urls = [value for key, value in data.items() if key.startswith('RTSP_Adres')]
base_output_path = data['Path_file']

# Функция для получения пути к папке с текущей датой
def get_output_path():
    current_date = datetime.now().strftime("%Y-%m-%d")
    output_path = os.path.join(base_output_path, "Видеоархив", current_date)
    os.makedirs(output_path, exist_ok=True)  # Создаёт папку, если она не существует
    return output_path

class_names = {
    0: "Mycop",
    1: "Chelovek",
    2: "Chelovek c Mycopom",
    3: "Mycop v mycopky",
    4: "chelovek",
    5: "Mycop na zemlyu"
}

def process_stream(rtsp_url, camera_number):
    # Получаем путь для сохранения видео
    output_path = get_output_path()

    # Открытие потока
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print(f"Ошибка: Не удалось открыть поток RTSP {rtsp_url}.")
        return

    # Формирование уникального имени файла
    video_number = 1               
    output_file = os.path.join(output_path, f'Камера{camera_number:02d}_{video_number:02d}.avi')
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

    recording = False
    record_start_time = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Ошибка: Не удалось получить кадр из {rtsp_url}.")
            break

        # Обработка кадра с помощью модели YOLO
        results = model.predict(source=frame)
        event_detected = 0
        # Отображение результатов
        for result in results:
            boxes = result.boxes  # Получаем рамки
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]  # Координаты рамки
                conf = box.conf[0]  # Уверенность
                cls = int(box.cls[0])  # Класс
                class_name = class_names.get(cls, "Unknown")

                # Рисуем рамку на кадре
                label = f'{class_name}, Conf: {conf:.2f}'
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                # Проверка на обнаружение "Chelovek"
                if class_name.lower() == "chelovek":
                    event_detected = 1
                    if not recording:
                        recording = True
                        record_start_time = time.time()

        # Если запись активна, проверяем время
        if recording:
            out.write(frame)  # Запись кадра в файл
            if time.time() - record_start_time > 5 and event_detected == 0:
                recording = False  # Останавливаем запись
                event_detected = 0
                out.release()
                video_number+=1
                output_file = os.path.join(output_path, f'Камера{camera_number:02d}_{video_number:02d}.avi')
                out = cv2.VideoWriter(output_file, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))  
            else:  # Если событие обнаружено
                    record_start_time = time.time()

    # Освобождение ресурсов
    cap.release()
    out.release()
    cv2.destroyAllWindows()

async def main():
    # Создаем пул потоков
    with ThreadPoolExecutor() as executor:
        # # Запускаем обработку потоков асинхронно
        await asyncio.gather(*(loop.run_in_executor(executor, process_stream, url, i + 1) for i, url in enumerate(rtsp_urls)))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())