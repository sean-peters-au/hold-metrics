from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from gui import LoadCellGUI
import time
import queue
from load_cell_manager import LoadCellManager

def update_gui(gui, load_cell_manager):
    for i in range(len(load_cell_manager.data_queues)):
        latest_value = None
        while True:
            try:
                latest_value = load_cell_manager.data_queues[i].get_nowait()
            except queue.Empty:
                break
        if latest_value is not None:
            gui.update_load(i, latest_value)
    QTimer.singleShot(5, lambda: update_gui(gui, load_cell_manager))

def main():
    app = QApplication([])

    load_cell_manager = LoadCellManager('/dev/cu.usbmodem101', 115200)
    time.sleep(1)

    # Hardcoded configuration for new load cells
    load_cell_manager.configure_load_cell(4, 5)
    load_cell_manager.configure_load_cell(2, 3)

    def start_zeroing():
        load_cell_manager.stop_streaming()
        load_cell_manager.zero()

    def start_calibration():
        load_cell_manager.stop_streaming()
        load_cell_manager.calibrate(gui)

    def start_streaming():
        load_cell_manager.start_streaming()

    def stop_streaming():
        load_cell_manager.stop_streaming()

    gui = LoadCellGUI(len(load_cell_manager.data_queues), start_zeroing, start_calibration, start_streaming, stop_streaming)
    gui.show()

    QTimer.singleShot(5, lambda: update_gui(gui, load_cell_manager))
    app.exec_()
    load_cell_manager.close()

if __name__ == "__main__":
    main()