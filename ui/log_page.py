from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QListWidget
from PyQt5.QtCore import Qt

class LogPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("📜 Log & Kayıt Sistemi")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color:#FFD000;")
        layout.addWidget(title)

        self.logBox = QListWidget()
        self.logBox.setStyleSheet("background-color:#111821; border-radius:10px; font-size:15px;")
        self.logBox.addItem("Log sistemi başlatıldı ✔")
        layout.addWidget(self.logBox)

        self.setLayout(layout)

    def add_log(self, txt):
        self.logBox.addItem(txt)
