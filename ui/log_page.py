# ui/log_page.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from PyQt5.QtCore import Qt

class LogPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setStyleSheet("""
            background-color:#0A0D12;
            color:#EAEAEA;
            font-size:13px;
        """)

        layout.addWidget(self.text)

        clear_btn = QPushButton("Temizle")
        clear_btn.clicked.connect(self.clear)
        layout.addWidget(clear_btn)

    def add_log(self, msg: str):
        self.text.append(msg)

    def clear(self):
        self.text.clear()
