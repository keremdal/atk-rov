from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSlider
from PyQt5.QtCore import Qt

class PIDPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("⚙️ PID Ayarları")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color:#FFD000;")
        layout.addWidget(title)

        self.info = QLabel("PID ayarlama sistemi henüz aktif değil.")
        self.info.setAlignment(Qt.AlignCenter)
        self.info.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.info)

        self.setLayout(layout)
