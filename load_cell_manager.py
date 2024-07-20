import serial
import time
import threading
import queue

class LoadCellManager:
    def __init__(self, port, baud_rate):
        self.ser = serial.Serial(port, baud_rate, timeout=0)  # Set timeout to non-blocking
        time.sleep(1)  # Shorten sleep time
        self.data_queues = []
        self.stop_event = threading.Event()
        self.stream_thread = None

    def send_command(self, command):
        self.ser.write(command.encode())
        time.sleep(0.05)  # Shorten sleep time to reduce latency

    def read_response(self):
        while self.ser.in_waiting > 0:
            response = self.ser.readline().decode().strip()
            print(response)

    def configure_load_cell(self, dout_pin, sck_pin):
        self.send_command('n')
        time.sleep(1)
        self.send_command(f'{dout_pin}')
        time.sleep(1)
        self.send_command(f'{sck_pin}')
        time.sleep(1)
        self.listen_responses()
        self.data_queues.append(queue.Queue())

    def listen_responses(self, duration=5):
        print(f'Listening for {duration} seconds')
        start_time = time.time()
        while time.time() - start_time < duration:
            if self.ser.in_waiting > 0:
                response = self.ser.readline().decode().strip()
                print(response)
            time.sleep(0.5)
        print('Listening complete')

    def zero(self):
        self.send_command('z')
        self.listen_responses()

    def calibrate(self, gui):
        for i in range(len(self.data_queues)):
            self.send_command('c')
            time.sleep(0.5)  # Shorten sleep time
            self.read_response()
            gui.show_message(f"Load Cell {i}: Place a known mass on the load cell.")
            known_mass = gui.prompt_known_mass()
            if known_mass is not None:
                self.ser.write((str(known_mass) + '\n').encode())
                self.listen_responses()
            else:
                gui.show_message(f"Load Cell {i}: Calibration canceled.")

    def stream_readings(self):
        self.send_command('s')
        while not self.stop_event.is_set():
            if self.ser.in_waiting > 0:
                response = self.ser.readline().decode().strip()
                print(f"Load values: {response}")
                try:
                    load_values = [float(val) for val in response.split(',')]
                    for i in range(len(load_values)):
                        self.data_queues[i].put(load_values[i])
                except ValueError:
                    pass
            time.sleep(0.025)  # Slight sleep to allow other threads to run, can be adjusted or removed
        self.send_command('q')
        self.read_response()

    def start_streaming(self):
        if self.stream_thread and self.stream_thread.is_alive():
            print("Already streaming. Stop current stream first.")
        else:
            self.stop_event.clear()
            self.stream_thread = threading.Thread(target=self.stream_readings)
            self.stream_thread.start()

    def stop_streaming(self):
        for queue in self.data_queues:
            queue.queue.clear()
        if self.stream_thread and self.stream_thread.is_alive():
            self.stop_event.set()
            self.stream_thread.join()

    def close(self):
        self.ser.close()