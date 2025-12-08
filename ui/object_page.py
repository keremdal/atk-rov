from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import numpy as np
import cv2

class ObjectPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # HEADER
        self.info = QLabel("🧠 YOLO NESNE TANIMA - HAZIRLANIYOR")
        self.info.setAlignment(Qt.AlignCenter)
        self.info.setStyleSheet("font-size:20px; color:#FFD000; font-weight:bold;")
        layout.addWidget(self.info)

        # CAMERA AREA
        self.cameraLabel = QLabel("GÖRÜNTÜ AKIŞI")
        self.cameraLabel.setAlignment(Qt.AlignCenter)
        self.cameraLabel.setStyleSheet(
            "background-color:#15191F; border:1px solid #344052; border-radius:12px;"
        )
        self.cameraLabel.setMinimumHeight(500)
        layout.addWidget(self.cameraLabel)

        # BUTTON
        self.btnOpen = QPushButton("AYRI PENCEREDE AÇ")
        self.btnOpen.setStyleSheet("""
            QPushButton {
                background-color:#FFD000;
                color:#000;
                font-size:16px;
                border-radius:8px;
                padding:8px;
            }
            QPushButton:hover {
                background-color:#FFEA55;
            }
        """)
        self.btnOpen.clicked.connect(self.open_window)
        layout.addWidget(self.btnOpen)

        self.setLayout(layout)

        # Yeni pencere referansı
        self.childWindow = None

    def open_window(self):
        win = QMainWindow()
        win.setWindowTitle("YOLO Object Detection")
        win.setCentralWidget(self.cameraLabel)
        win.resize(1280, 720)
        win.show()
        self.childWindow = win

    def update_object_frame(self, frame):
        # YOLO daha sonra burada çalışacak
        # şimdilik sadece gösteriyoruz
        if frame is None:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytesPerLine = ch * w

        qimg = QImage(rgb.data, w, h, bytesPerLine, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        self.cameraLabel.setPixmap(pix)
