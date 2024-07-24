import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, QLineEdit, QSizePolicy
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont, QFontMetrics, QImage, QPainterPath
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QRect
from pymavlink import mavutil
from math import cos, sin, pi
import cv2
import numpy as np
import requests
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class BatteryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.battery_level = 0
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 120, 40)
        self.setWindowTitle('Battery Status')
        self.setStyleSheet('background-color: lightgrey;')
        self.setFixedSize(120, 40)
        self.show()

    def update_battery_level(self, level):
        self.battery_level = level
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawBattery(painter)

    def drawBattery(self, painter):
        rect = self.rect()
        painter.setBrush(Qt.NoBrush)

        battery_width = 100
        battery_height = 40

        center_x = rect.width() // 2
        center_y = rect.height() // 2

        battery_x = center_x - battery_width // 2
        battery_y = center_y - battery_height // 2

        pen = QPen(Qt.green, 3)
        painter.setPen(pen)
        painter.drawRect(battery_x, battery_y, battery_width, battery_height)

        level = self.battery_level
        if level == 0:
            return

        if level >= 75:
            color = QColor(0, 100, 0)
            segments = 4
        elif level >= 50:
            color = QColor(100, 238, 100)
            segments = 3
        elif level >= 25:
            color = QColor(255, 165, 0)
            segments = 2
        else:
            color = QColor(255, 0, 0)
            segments = 1

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color, Qt.SolidPattern))

        segment_width = (battery_width // 4) - 8
        segment_height = battery_height - 10
        segment_spacing = (battery_width - (segment_width * 4)) // 5

        for i in range(segments):
            segment_x = battery_x + segment_spacing + i * (segment_width + segment_spacing)
            segment_y = battery_y + 5
            painter.drawRect(segment_x, segment_y, segment_width, segment_height)

        painter.setPen(QPen(Qt.black))
        painter.setFont(QFont("Armstrong", 12))
        text_x = battery_x + 10
        text_y = battery_y + 25
        painter.drawText(text_x, text_y, f"% {self.battery_level}")


class VerticalSpeedGaugeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.value = 0
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 720, 400, 400)
        self.setWindowTitle('Vertical Speed')
        self.show()

    def update_value(self, value):
        self.value = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawBackground(painter)
        self.drawGauge(painter)
        self.drawText(painter)

    def drawBackground(self, painter):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 7, 14, 255)))
        painter.drawRect(self.rect())

    def drawGauge(self, painter):
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = 100
        radius2 = 110
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor(127, 127, 127, 255), 2)
        painter.setPen(pen)
        painter.drawArc(center_x - radius, center_y - radius, 2 * radius, 2 * radius, -90 * 16, 240 * 16)

        if self.value >= 0:
            pen_up = QPen(QColor(25, 25, 255), 8)
            painter.setPen(pen_up)
            angle_start = 0
            angle_span = int(self.value * 3)
        else:
            pen_down = QPen(QColor(255, 165, 0), 8)
            painter.setPen(pen_down)
            angle_start = 0
            angle_span = int(self.value * 3)

        painter.drawArc(center_x - radius2, center_y - radius2, 2 * radius2, 2 * radius2, angle_start * 16, angle_span * 16)

        painter.setPen(QPen(Qt.gray, 2))
        font = QFont("Armstrong", 8)
        painter.setFont(font)
        for i in range(-30, 31, 2):
            angle = 0 + i * 3
            if i % 15 == 0:
                x1 = int(center_x + (radius - 20) * cos(angle * pi / 180))
                y1 = int(center_y - (radius - 20) * sin(angle * pi / 180))
                x2 = int(center_x + (radius - 5) * cos(angle * pi / 180))
                y2 = int(center_y - (radius - 5) * sin(angle * pi / 180))
                text_x = int(center_x + (radius - 35) * cos(angle * pi / 180))
                text_y = int(center_y - (radius - 35) * sin(angle * pi / 180))
                painter.drawText(text_x - 10, text_y + 5, f"{i}")
            else:
                x1 = int(center_x + (radius - 10) * cos(angle * pi / 180))
                y1 = int(center_y - (radius - 10) * sin(angle * pi / 180))
                x2 = int(center_x + (radius - 5) * cos(angle * pi / 180))
                y2 = int(center_y - (radius - 5) * sin(angle * pi / 180))
            painter.drawLine(x1, y1, x2, y2)

        font = QFont("Armstrong", 5)
        painter.setFont(font)
        painter.setPen(QPen(Qt.gray))
        painter.drawText(center_x + 55, center_y - 40, "UP")
        painter.drawText(center_x + 40, center_y + 45, "DOWN")

    def drawText(self, painter):
        center_x = self.width() // 2
        center_y = self.height() // 2

        painter.setPen(QPen(QColor(240, 240, 240, 255)))
        font = QFont("Armstrong", 8)
        painter.setFont(font)
        painter.drawText(center_x - 100, center_y - 10, "VERTICAL SPEED")

        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(center_x - 25, center_y + 10, "m/s")

        font.setPointSize(65)
        painter.setFont(font)
        value_str = str(int(abs(self.value)))
        fm = QFontMetrics(font)
        text_width = fm.width(value_str)
        painter.drawText(center_x - text_width - 30, center_y + 100, value_str)

        rect_x = center_x - 85
        rect_y = center_y + 0
        rect_width = 50
        rect_height = 10

        if self.value < 0:
            painter.setBrush(QBrush(QColor(255, 165, 0)))
        else:
            painter.setBrush(QBrush(QColor(40, 40, 40, 255)))

        painter.drawRect(rect_x, rect_y, rect_width, rect_height)


class AirSpeedGaugeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.value = 0
        self.initUI()

    def initUI(self):
        self.setGeometry(440, 720, 400, 400)
        self.setWindowTitle('Air Speed')
        self.show()

    def update_value(self, value):
        self.value = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawBackground(painter)
        self.drawGauge(painter)
        self.drawText(painter)

    def drawBackground(self, painter):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 7, 14, 255)))
        painter.drawRect(self.rect())

    def drawGauge(self, painter):
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = 100
        radius2 = 110
        painter.setRenderHint(QPainter.Antialiasing)

        angle_start = 270
        angle_span = self.value * 6

        # Draw the arc for the gauge
        pen = QPen(QColor(127, 127, 127, 255), 2)
        painter.setPen(pen)
        painter.drawArc(center_x - radius, center_y - radius, 2 * radius, 2 * radius, 30 * 16, 240 * 16)

        # Calculate the color based on the value
        red = min(255, int(255 * (self.value / 40.0)))
        green = max(0, 165 - int(165 * (self.value / 40.0)))
        pen61 = QPen(QColor(red, green, 0), 8)

        painter.setPen(pen61)

        painter.drawArc(center_x - radius2, center_y - radius2, 2 * radius2, 2 * radius2, int(angle_start * 16), int(angle_span * -16))

        # Draw the ticks and labels inside the arc
        painter.setPen(QPen(Qt.gray, 2))
        font = QFont("Armstrong", 8)
        painter.setFont(font)
        for i in range(-0, 41, 1):
            angle = - 90 - i * 6
            if i % 10 == 0:
                x1 = int(center_x + (radius - 20) * cos(angle * pi / 180))
                y1 = int(center_y - (radius - 20) * sin(angle * pi / 180))
                x2 = int(center_x + (radius - 5) * cos(angle * pi / 180))
                y2 = int(center_y - (radius - 5) * sin(angle * pi / 180))
                text_x = int(center_x + (radius - 35) * cos(angle * pi / 180))
                text_y = int(center_y - (radius - 35) * sin(angle * pi / 180))
                painter.drawText(text_x - 10, text_y + 5, f"{i}")
            else:
                x1 = int(center_x + (radius - 10) * cos(angle * pi / 180))
                y1 = int(center_y - (radius - 10) * sin(angle * pi / 180))
                x2 = int(center_x + (radius - 5) * cos(angle * pi / 180))
                y2 = int(center_y - (radius - 5) * sin(angle * pi / 180))
            painter.drawLine(x1, y1, x2, y2)

    def drawText(self, painter):
        center_x = self.width() // 2
        center_y = self.height() // 2

        painter.setPen(QPen(QColor(240, 240, 240, 255)))
        font = QFont("Armstrong", 8)
        painter.setFont(font)
        painter.drawText(center_x - 37, center_y - 10, "AIR SPEED")

        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(center_x - 36 , center_y + 10, "m/s")

        font.setPointSize(65)
        painter.setFont(font)
        value_str = str(int(abs(self.value)))
        fm = QFontMetrics(font)
        text_width = fm.width(value_str)
        painter.drawText(center_x + 20, center_y + 90, str(value_str))


class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.y_value = 0
        self.x_value = 0
        self.initUI()

    def initUI(self):
        self.setGeometry(440, 720, 440, 320)
        self.setWindowTitle('Gyro Indicator')
        self.show()

    def update_graph(self, y, x):
        self.y_value = y
        self.x_value = -x
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.rect(), QColor(0, 7, 14, 255))

        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2

        painter.translate(center_x, center_y)
        painter.rotate(self.x_value)
        painter.translate(-center_x, -center_y)

        path = QPainterPath()
        path.addEllipse(center_x - 100, center_y - 100, 200, 200)
        painter.setClipPath(path)

        self.draw_graph(painter)

    def draw_graph(self, painter):
        width = self.width()
        height = self.height()

        center_x = width // 2
        center_y = height // 2

        painter.setPen(QPen(QColor(127, 127, 127, 255), 4))
        painter.setBrush(QBrush(Qt.black))
        painter.drawEllipse(center_x - 100, center_y - 100, 200, 200)

        painter.setBrush(QBrush(QColor(0, 0, 255)))
        painter.drawRect(center_x - 100, center_y - 100, 200, int(100 + self.y_value * 3.33))

        painter.setPen(QPen(QColor(255, 255, 255, 255), 10))
        painter.drawPoint(center_x, center_y)

        for i, value in enumerate(range(-30, 31, 10)):
            y_position = center_y - int((value - self.y_value) * 3.5)

            if i % 2 == 0:
                line_length = 60
                font_size = 6
            else:
                line_length = 20
                font_size = 8

            painter.setPen(QPen(QColor(255, 255, 255), 3))
            painter.drawLine(center_x - line_length // 2, y_position, center_x + line_length // 2, y_position)

            painter.setFont(QFont("Armstrong", font_size))
            painter.drawText(center_x + 40, y_position + 5, str(value))


class VideoStreamWorker(QThread):
    frame_received = pyqtSignal(np.ndarray)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self._run_flag = True

    def run(self):
        while self._run_flag:
            try:
                response = requests.get(self.url, stream=True)
                response.raise_for_status()
                bytes_data = b''
                for chunk in response.iter_content(chunk_size=1024):
                    bytes_data += chunk
                    a = bytes_data.find(b'\xff\xd8')
                    b = bytes_data.find(b'\xff\xd9')
                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]
                        img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        if img is not None:
                            self.frame_received.emit(img)
                        else:
                            print("Görüntü çözme hatası")
            except requests.exceptions.RequestException as e:
                print(f"Bağlantı hatası: {e}")
                break

    def stop(self):
        self._run_flag = False
        self.wait()

class VideoStreamWidget(QWidget):
    def __init__(self, url):
        super().__init__()
        self.image = QImage()
        self.url = url
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Video Stream')
        self.start_video_stream(self.url)

    def start_video_stream(self, url):
        self.video_thread = VideoStreamWorker(url)
        self.video_thread.frame_received.connect(self.update_image)
        self.video_thread.start()

    def update_image(self, frame):
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        self.image = q_img
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.image.isNull():
            painter.drawImage(self.rect(), self.image)

class LidarDataWorker(QThread):
    lidar_data_received = pyqtSignal(list)

    def __init__(self, ip):
        super().__init__()
        self.ip = ip
        self._run_flag = True

    def run(self):
        while self._run_flag:
            try:
                response = requests.get(f'http://{self.ip}/lidar', timeout=5)  # Zaman aşımı 5 saniye olarak ayarlanmış
                if response.status_code == 200:
                    data = response.json()
                    print(f"Lidar Data: {data}")  # Debug print
                    self.lidar_data_received.emit(data)
                else:
                    print(f"Failed to get Lidar data: {response.status_code}")
            except requests.exceptions.Timeout:
                print(f"Connection to {self.ip} timed out.")
            except Exception as e:
                print(f'Error fetching Lidar data: {e}')
            self.msleep(500)

    def stop(self):
        self._run_flag = False
        self.wait()


class LidarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111, polar=True)
        self.ax.set_ylim(0, 10)
        self.ax.set_xlim(-np.pi, np.pi)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_lidar_data(self, data):
        angles = np.linspace(-np.pi, np.pi, len(data))
        self.ax.clear()
        self.ax.plot(angles, data, 'b.')
        self.ax.set_ylim(0, 10)
        self.ax.set_xlim(-np.pi, np.pi)
        self.canvas.draw()            

class PixhawkInterface(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.connection = None

    def initUI(self):
        self.setWindowTitle('Pixhawk Arayüzü')
        self.setGeometry(0, 0, 1920, 1080)

        # Ana widget ve layout'un arka planını siyah yapma
        self.setStyleSheet("background-color: #000714;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Video Stream
        self.video_widget = VideoStreamWidget(url="http://192.168.85.114:5000/video_feed")
        self.video_widget.setFixedSize(1320, 640)

        # Video widget'ı içeren layout'u oluştur
        video_layout = QVBoxLayout()
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_layout.setSpacing(0)
        video_layout.addWidget(self.video_widget)

        main_layout.addLayout(video_layout)

                # Gauges ve Lidar widget'ını içeren layout'u oluştur
        gauges_and_lidar_layout = QHBoxLayout()
        gauges_and_lidar_layout.setContentsMargins(0, 0, 0, 0)
        gauges_and_lidar_layout.setSpacing(0)

        # Gauges
        gauges_container_layout = QHBoxLayout()  # Dikey değil yatay layout kullanıyoruz
        gauges_container_layout.setContentsMargins(0, 0, 0, 0)
        gauges_container_layout.setSpacing(0)

        self.vertical_speed_gauge = VerticalSpeedGaugeWidget()
        self.vertical_speed_gauge.setFixedSize(440, 320)
        self.vertical_speed_gauge.setContentsMargins(0, 0, 0, 0)

        self.graph_widget = GraphWidget()
        self.graph_widget.setFixedSize(440, 320)
        self.graph_widget.setContentsMargins(0, 0, 0, 0)

        self.air_speed_gauge = AirSpeedGaugeWidget()
        self.air_speed_gauge.setFixedSize(440, 320)
        self.air_speed_gauge.setContentsMargins(0, 0, 0, 0)

        gauges_container_layout.addWidget(self.vertical_speed_gauge)  # İlk olarak vertical_speed_gauge
        gauges_container_layout.addWidget(self.graph_widget)
        gauges_container_layout.addWidget(self.air_speed_gauge)  # Son olarak air_speed_gauge

        gauges_container = QWidget()
        gauges_container.setLayout(gauges_container_layout)

        gauges_and_lidar_layout.addWidget(gauges_container, alignment=Qt.AlignLeft)



        # Lidar Widget ekle
        self.lidar_widget = LidarWidget()
        self.lidar_widget.setFixedSize(440, 320)  # Boyutu uygun şekilde ayarlayın
        gauges_and_lidar_layout.addWidget(self.lidar_widget, alignment=Qt.AlignRight)

        main_layout.addLayout(gauges_and_lidar_layout)

        # Alt merkez (COM ve baud seçimi, bağlan düğmesi ve durum etiketi)
        connection_layout = QHBoxLayout()
        connection_layout.setContentsMargins(10, 10, 10, 10)
        connection_layout.setSpacing(10)

        self.port_label = QLabel('PORT')
        self.port_label.setFont(QFont("Armstrong", 10))
        self.port_label.setStyleSheet('color: #bbc5c9 ; background-color : #011c38 ; padding:5px;')
        connection_layout.addWidget(self.port_label)

        self.port_combo = QComboBox()
        self.port_combo.addItems(['COM5', 'COM6', 'COM7', 'COM8', 'COM9'])
        self.port_combo.setFont(QFont("Armstrong", 10))
        self.port_combo.setStyleSheet('background-color : #002142 ; color : #bbc5c9 ; padding:5px;')
        self.port_combo.setFixedWidth(100)
        connection_layout.addWidget(self.port_combo)

        self.baud_label = QLabel('BAUD RATE')
        self.baud_label.setFont(QFont("Armstrong", 10))
        self.baud_label.setStyleSheet('color : #bbc5c9 ; background-color: #011c38 ; padding:5px;')
        connection_layout.addWidget(self.baud_label)

        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.baud_combo.setFont(QFont("Armstrong", 10))
        self.baud_combo.setStyleSheet('background-color: #002142 ; color: #bbc5c9 ; padding:5px;')
        self.baud_combo.setFixedWidth(100)
        connection_layout.addWidget(self.baud_combo)

        self.connect_button = QPushButton('CONNECT')
        self.connect_button.setFont(QFont("Armstrong", 10))
        self.connect_button.setStyleSheet('background-color: #3CB371; color: white; padding:5px;')
        self.connect_button.setFixedSize(120, 30)
        self.connect_button.clicked.connect(self.connect_pixhawk)
        connection_layout.addWidget(self.connect_button)

        self.status_label = QLabel('NO CONNECTION')
        self.status_label.setFont(QFont("Armstrong", 10))
        self.status_label.setStyleSheet('color: white; background-color: #798499; padding:5px;')
        self.status_label.setFixedSize(170, 30)
        connection_layout.addWidget(self.status_label)

        self.camera_ip_label = QLabel('IP adresi:')
        self.camera_ip_label.setFont(QFont("Armstrong", 10))
        self.camera_ip_label.setStyleSheet('color: #ffffff; padding:5px;')
        connection_layout.addWidget(self.camera_ip_label)

        self.camera_ip_combo = QComboBox()
        self.camera_ip_combo.setFont(QFont("Armstrong", 10))
        self.camera_ip_combo.setStyleSheet('background-color: #ffffff; color: #000000; padding:5px;')
        self.camera_ip_combo.setEditable(True)
        self.camera_ip_combo.addItems([
            "192.168.85.114:5000",
            "192.168.85.115:5000",
            "192.168.85.116:5000"
        ])
        self.camera_ip_combo.setFixedWidth(300)
        self.camera_ip_combo.currentTextChanged.connect(self.update_camera_ip)
        connection_layout.addWidget(self.camera_ip_combo)

        self.altitude_label = QLabel('Altitude: ')
        self.altitude_label.setFont(QFont("Armstrong", 10))
        self.altitude_label.setStyleSheet('color: #ffffff; padding:5px;')
        connection_layout.addWidget(self.altitude_label)

        self.altitude_value_label = QLabel('--- m')
        self.altitude_value_label.setFont(QFont("Armstrong", 10))
        self.altitude_value_label.setStyleSheet('color: #ffffff; padding:5px;')
        connection_layout.addWidget(self.altitude_value_label)

        self.flight_time_label = QLabel('Flight Time: ')
        self.flight_time_label.setFont(QFont("Armstrong", 10))
        self.flight_time_label.setStyleSheet('color: #ffffff; padding:5px;')
        connection_layout.addWidget(self.flight_time_label)

        self.flight_time_value_label = QLabel('--- h')
        self.flight_time_value_label.setFont(QFont("Armstrong", 10))
        self.flight_time_value_label.setStyleSheet('color: #ffffff; padding:5px;')
        connection_layout.addWidget(self.flight_time_value_label)

        self.battery_label = QLabel('Battery')
        self.battery_label.setFont(QFont("Armstrong", 10))
        self.battery_label.setStyleSheet('color: #ffffff; padding:5px;')
        self.battery_label.setFixedSize(90, 30)
        connection_layout.addWidget(self.battery_label)

        self.battery_widget = BatteryWidget()
        self.battery_widget.setFixedSize(120, 40)
        connection_layout.addWidget(self.battery_widget, alignment=Qt.AlignVCenter)

        connection_widget = QWidget()
        connection_widget.setLayout(connection_layout)
        connection_widget.setFixedSize(1920, 60)
        connection_widget.setStyleSheet('background-color: #001020;')

        main_layout.addWidget(connection_widget)

        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)

        self.lidar_worker = LidarDataWorker(ip="192.168.85.114:5001")
        self.lidar_worker.lidar_data_received.connect(self.lidar_widget.update_lidar_data)
        self.lidar_worker.start()

    def update_altitude(self, altitude):
        self.altitude_value_label.setText(f'{altitude} m')

    def update_flight_time(self, flight_time):
        self.flight_time_value_label.setText(f'{flight_time} h')

    def update_camera_ip(self):
        ip = self.camera_ip_combo.currentText()
        if ip:
            url = f"http://{ip}/video_feed"
            self.video_widget.video_thread.stop()
            self.video_widget.start_video_stream(url)

    def connect_pixhawk(self):
        port = self.port_combo.currentText()
        baud = int(self.baud_combo.currentText())
        try:
            self.connection = mavutil.mavlink_connection(port, baud=baud)
            self.status_label.setText(f'CONNECTED ({port} @ {baud})')
            self.status_label.setStyleSheet('color: white; background-color: #228B22; padding:5px;')

            self.connection.mav.request_data_stream_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL,
                10,
                1
            )

            self.timer.start(200)
        except Exception as e:
            self.status_label.setText(f'Hata: {str(e)}')
            self.status_label.setStyleSheet('color: white; background-color: #B22222; padding:5px;')

    def update_data(self):
        if self.connection:
            try:
                msg = self.connection.recv_match(type='VFR_HUD', blocking=True, timeout=0.5)
                if msg:
                    airspeed = msg.airspeed
                    altitude = msg.alt
                    vertical_speed = msg.climb
                    self.air_speed_gauge.update_value(airspeed)
                    self.vertical_speed_gauge.update_value(vertical_speed)
                    self.update_altitude(altitude)
                    flight_time = self.connection.time_since(self.connection.last_heartbeat()) / 3600
                    self.update_flight_time(round(flight_time, 2))
                else:
                    self.air_speed_gauge.update_value(0)
                    self.vertical_speed_gauge.update_value(0)

                msg_attitude = self.connection.recv_match(type='ATTITUDE', blocking=True, timeout=0.5)
                if msg_attitude:
                    roll = msg_attitude.roll * (180 / pi)
                    pitch = msg_attitude.pitch * (180 / pi)
                    self.graph_widget.update_graph(pitch, roll)
                else:
                    self.graph_widget.update_graph(0, 0)

                msg_sys_status = self.connection.recv_match(type='SYS_STATUS', blocking=True, timeout=0.5)
                if msg_sys_status:
                    battery_remaining = msg_sys_status.battery_remaining
                    if battery_remaining < 0:
                        battery_remaining = 0
                    self.battery_widget.update_battery_level(battery_remaining)
                else:
                    pass

            except Exception as e:
                self.status_label.setText(f'Veri Hatasi: {str(e)}')
                self.status_label.setStyleSheet('color: white; background-color: #B22222; padding:5px;')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PixhawkInterface()
    ex.show()
    sys.exit(app.exec_())
