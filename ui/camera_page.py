from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QImage, QPixmap

class CameraPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cam_worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        self.cameraLabel = QLabel("KAMERA BEKLENİYOR...")
        self.cameraLabel.setStyleSheet("background-color:#111; color:white; font-size:14px;")
        self.cameraLabel.setFixedHeight(300)  # LAPTOP UYUMLU YÜKSEKLİK
        layout.addWidget(self.cameraLabel)

        self.btnStart = QPushButton("Kamera Başlat")
        self.btnStop = QPushButton("Kamera Durdur")

        layout.addWidget(self.btnStart)
        layout.addWidget(self.btnStop)

        self.setLayout(layout)

    def set_cam_worker(self, worker):
        self.cam_worker = worker

        # Eğer kayıt fonksiyonları varsa bağla
        if hasattr(worker, "start_record"):
            self.btnStart.clicked.connect(worker.start_record)
        if hasattr(worker, "stop_record"):
            self.btnStop.clicked.connect(worker.stop_record)

    # 🔥 MAINWINDOW ile uyumlu FONKSİYON
    def update_camera_frame(self, frame):
        if frame is None:
            return

        h, w, ch = frame.shape
        qimg = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)

        # Fit to label
        pix = pix.scaled(
            self.cameraLabel.width(),
            self.cameraLabel.height(),
            aspectRatioMode=1
        )

        self.cameraLabel.setPixmap(pix)

    # Eski fonksiyonun da çalışması için:
    def update_frame(self, frame):
        self.update_camera_frame(frame)
