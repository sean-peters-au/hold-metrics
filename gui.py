from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QInputDialog, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt

import numpy as np
import matplotlib.pyplot as plt

class LoadCellCanvas(QWidget):
    def __init__(self, num_load_cells, parent=None):
        super().__init__(parent)
        self.load_values = [0] * num_load_cells
        self.num_load_cells = num_load_cells
        self.max_load = 10000
        self.min_load = -10000

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        line_width = 10
        spacing = (width - line_width * self.num_load_cells) / (self.num_load_cells + 1)
        x_start = spacing

        for i in range(self.num_load_cells):
            load_value = self.load_values[i]

            # Normalize load value for colormap
            norm_load = (load_value - self.min_load) / (self.max_load - self.min_load)
            color = self.get_color_from_colormap(norm_load)

            pen = QPen(color, line_width)
            painter.setPen(pen)

            line_length = int((load_value / self.max_load) * height / 2)  # Scale line length
            x_pos = int(x_start + i * (line_width + spacing))
            painter.drawLine(x_pos, int(height / 2), x_pos, int(height / 2 - line_length))

    def update_load(self, index, load_value):
        self.load_values[index] = load_value
        self.update()

    def get_color_from_colormap(self, value):
        cmap = plt.get_cmap('coolwarm')
        rgba = cmap(value)
        return QColor(int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255), int(rgba[3]*255))
    def update_load(self, index, load_value):
        self.load_values[index] = load_value
        self.update()

    def get_color_from_colormap(self, value):
        cmap = plt.get_cmap('coolwarm')
        rgba = cmap(value)
        return QColor(int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255), int(rgba[3]*255))

class LoadCellGUI(QMainWindow):
    def __init__(self, num_load_cells, start_zeroing, start_calibration, start_streaming, stop_streaming):
        super().__init__()
        self.setWindowTitle("Load Cell Readings")

        self.num_load_cells = num_load_cells
        self.labels = []

        for i in range(num_load_cells):
            label = QLabel(f"Load Cell {i}: 0.00", self)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 16px;")
            self.labels.append(label)

        self.canvas = LoadCellCanvas(num_load_cells, self)
        self.canvas.setMinimumSize(200, 400)

        self.zero_button = QPushButton("Zero", self)
        self.zero_button.clicked.connect(start_zeroing)

        self.calibrate_button = QPushButton("Calibrate", self)
        self.calibrate_button.clicked.connect(start_calibration)

        self.stream_button = QPushButton("Start Streaming", self)
        self.stream_button.clicked.connect(start_streaming)

        self.stop_button = QPushButton("Stop Streaming", self)
        self.stop_button.clicked.connect(stop_streaming)

        layout = QVBoxLayout()
        for label in self.labels:
            layout.addWidget(label)
        layout.addWidget(self.canvas)
        layout.addWidget(self.zero_button)
        layout.addWidget(self.calibrate_button)
        layout.addWidget(self.stream_button)
        layout.addWidget(self.stop_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_load(self, index, load_value):
        self.labels[index].setText(f"Load Cell {index}: {load_value:.2f}")
        self.canvas.update_load(index, load_value)

    def prompt_known_mass(self):
        known_mass, ok = QInputDialog.getDouble(self, "Known Mass", "Enter the known mass (in grams):")
        if ok:
            return known_mass
        return None

    def show_message(self, message):
        QMessageBox.information(self, "Information", message)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    gui = LoadCellGUI(2, lambda: print("Zero"), lambda: print("Calibrate"), lambda: print("Start Streaming"), lambda: print("Stop Streaming"))
    gui.show()
    sys.exit(app.exec_())