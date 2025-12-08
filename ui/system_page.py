from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt

class SystemPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("🖥️ Sistem Ayarları & İletişim")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color:#FFD000;")
        layout.addWidget(title)

        self.btnRestart = QPushButton("SİSTEMİ YENİDEN BAŞLAT")
        self.btnRestart.setStyleSheet("background-color:#FF0000; padding:12px;")
        layout.addWidget(self.btnRestart)

        self.setLayout(layout)
