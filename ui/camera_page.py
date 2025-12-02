from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import numpy as np

class CameraPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cam_worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        self.camStatus = QLabel("🔴 Kamera yok")
        self.camStatus.setAlignment(Qt.AlignCenter)
        self.camStatus.setStyleSheet("color:#FF5555; font-size:14px; font-weight:bold;")
        layout.addWidget(self.camStatus)

        self.cameraLabel = QLabel("KAMERA")
        self.cameraLabel.setAlignment(Qt.AlignCenter)
        self.cameraLabel.setStyleSheet(
            "background-color:#111821; border-radius:12px; border:1px solid #2A3441; font-size:24px;")
        layout.addWidget(self.cameraLabel)

        btnLayout = QHBoxLayout()

        self.btnStart = QPushButton("🔴 Kaydı Başlat")
        self.btnStop = QPushButton("🟡 Kaydı Durdur")

        btnLayout.addWidget(self.btnStart)
        btnLayout.addWidget(self.btnStop)
        layout.addLayout(btnLayout)

        self.setLayout(layout)

    # Kamera thread’i bağlama
    def set_cam_worker(self, worker):
        self.cam_worker = worker
        self.cam_worker.frameSignal.connect(self.update_camera_frame)

        self.btnStart.clicked.connect(self.cam_worker.start_record)
        self.btnStop.clicked.connect(self.cam_worker.stop_record)

    def update_camera_frame(self, frame):
        if frame is None:
            self.camStatus.setText("🔴 Kamera yok")
            self.cameraLabel.setText("NO SIGNAL")
            return

        self.camStatus.setText("🟢 Kamera aktif")

        h, w, ch = frame.shape
        bytesPerLine = w * ch
        qimg = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
        pix = qimg.scaled(1200, 400, Qt.KeepAspectRatio)

        self.cameraLabel.setPixmap(QPixmap.fromImage(pix))
