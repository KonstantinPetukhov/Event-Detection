import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout, QFileDialog
from PyQt6 import QtCore
from PyQt6.QtCore import Qt

class SimpleApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Простой интерфейс")
        self.setFixedSize(500, 400)
        self.layout = QVBoxLayout()

        # Список для хранения полей ввода
        self.input_fields = []

        # Создаем фиксированный layout для первых двух полей ввода
        fixed_layout = QVBoxLayout()

        # Создаем горизонтальный layout для первого поля ввода и кнопки "Обзор"
        h_layout1 = QHBoxLayout()
        self.input1 = QLineEdit(self)
        self.input1.setPlaceholderText("Введите первое значение")
        h_layout1.addWidget(self.input1)

        # Кнопка "Обзор"
        self.browse_button = QPushButton("Обзор", self)
        self.browse_button.clicked.connect(self.browse_directory)
        h_layout1.addWidget(self.browse_button)

        # Добавляем горизонтальный layout в фиксированный layout
        fixed_layout.addLayout(h_layout1)

        # Создаем горизонтальный layout для второго поля ввода и кнопок "+" и "-"
        h_layout2 = QHBoxLayout()
        self.input2 = QLineEdit(self)
        self.input2.setPlaceholderText("Введите второе значение")
        h_layout2.addWidget(self.input2)

        # Кнопка "+"
        self.add_button = QPushButton("+", self)
        self.add_button.clicked.connect(self.add_input_field)
        h_layout2.addWidget(self.add_button)

        # Кнопка "-" (изначально скрыта)
        self.minus_button = QPushButton("-", self)
        self.minus_button.clicked.connect(self.remove_last_input_field)
        self.minus_button.setVisible(False)
        h_layout2.addWidget(self.minus_button)

        # Добавляем второй горизонтальный layout в фиксированный layout
        fixed_layout.addLayout(h_layout2)

        # Добавляем фиксированный layout в основной layout
        self.layout.addLayout(fixed_layout)

        # Создаем отдельный вертикальный layout для новых полей
        self.new_fields_layout = QVBoxLayout()
        self.layout.addLayout(self.new_fields_layout)

        # Устанавливаем layout в окно
        self.setLayout(self.layout)

        # Кнопка "Запустить"
        self.run_button = QPushButton("Запустить", self)
        self.layout.addWidget(self.run_button)

    def browse_directory(self):
        """Открывает диалог выбора папки и записывает выбранный путь в первое поле ввода."""
        folder_path = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if folder_path:
            self.input1.setText(folder_path)

    def add_input_field(self):
        """Добавляет новое поле ввода в отдельный layout."""
        if len(self.input_fields) < 6:
            new_input = QLineEdit(self)
            new_input.setPlaceholderText("Введите значение")
            self.new_fields_layout.addWidget(new_input)
            self.input_fields.append(new_input)

            # Показываем кнопку "-" если это первое добавление
            if len(self.input_fields) == 1:
                self.minus_button.setVisible(True)

            # Если достигли лимита, отключаем кнопку "+"
            if len(self.input_fields) == 6:
                self.add_button.setEnabled(False)

    def remove_last_input_field(self):
        """Удаляет последнее добавленное поле ввода."""
        if self.input_fields:
            last_input = self.input_fields.pop()
            last_input.deleteLater()

            # Скрываем кнопку "-" если больше нет полей
            if not self.input_fields:
                self.minus_button.setVisible(False)

            # Включаем кнопку "+" если количество полей меньше 6
            if len(self.input_fields) < 6:
                self.add_button.setEnabled(True)

    def changeWindow(self, event):
        # Игнорируем событие закрытия окна
        if event.type() == QtCore.QEvent.WindowStateChange or self.windowState() & Qt.WindowState.WindowMaximized:
            self.setWindowState(Qt.WindowState.WindowNoState)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleApp()
    window.show()
    sys.exit(app.exec())