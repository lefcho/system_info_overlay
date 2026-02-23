import sys
import psutil
import ctypes
import socket
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont

class Overlay(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.label = QLabel(self)
        self.label.setFont(QFont("Consolas", 12))
        self.label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 160);
            padding: 12px;
            border-radius: 12px;
        """)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_info)
        self.timer.start(1000)

        self.net_old = psutil.net_io_counters()
        self.resize(260, 160)
        self.move_to_top_right()
        self.make_click_through()

    def move_to_top_right(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 200, 20)

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    
    def make_click_through(self):
        hwnd = int(self.winId())

        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x80000
        WS_EX_TRANSPARENT = 0x20

        user32 = ctypes.windll.user32
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE,
                            style | WS_EX_LAYERED | WS_EX_TRANSPARENT)

    def update_info(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent

        if cpu < 50:
            cpu_color = "#A2F53C"
        elif cpu < 80:
            cpu_color = "#FFA600A4"
        else:
            cpu_color = "#EF2B2B"

        if ram < 70:
            ram_color = "#FFFFFF"
        else:
            ram_color = "#E22222"

        net_new = psutil.net_io_counters()
        net_speed = (net_new.bytes_recv - self.net_old.bytes_recv) / 1024 / 1024
        self.net_old = net_new

        ip = self.get_ip()
        time_now = datetime.now().strftime("%H:%M:%S")

        text = f"""
            <span style="color:{cpu_color};">CPU: {cpu}%</span><br>
            <span style="color:{ram_color};">RAM: {ram}%</span><br>
            <span style="color:#9E18E1;">NET: {net_speed:.2f} MB/s</span><br>
            <span style="color:#605D84;">IP: {ip}</span><br>
            <span style="color:#AAAAAA;">{time_now}</span>
        """
        self.label.setText(text)
        self.label.setTextFormat(Qt.TextFormat.RichText)
        self.label.adjustSize()
        self.adjustSize()

app = QApplication(sys.argv)
overlay = Overlay()
overlay.show()
sys.exit(app.exec())