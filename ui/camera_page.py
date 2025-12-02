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
        self.cameraLabel.setStyleSheet("background-color:#111; color:white; font-size:16px;")
        self.cameraLabel.setFixedHeight(350)
        layout.addWidget(self.cameraLabel)

        self.btnStart = QPushButton("Kamera Başlat")
        self.btnStop = QPushButton("Kamera Durdur")

        # START RECORD ve STOP RECORD BAĞLANTILARI KALDIRILDI !!!
        # self.btnStart.clicked.connect(self.cam_worker.start_record)
        # self.btnStop.clicked.connect(self.cam_worker.stop_record)

        layout.addWidget(self.btnStart)
        layout.addWidget(self.btnStop)

        self.setLayout(layout)

    def set_cam_worker(self, worker):
        self.cam_worker = worker

    def update_frame(self, frame):
        if frame is None:
            return

        h, w, ch = frame.shape
        qimg = QImage(frame.data, w, h, ch * w, QImage.Format_BGR888)
        pix = QPixmap.fromImage(qimg)
        self.cameraLabel.setPixmap(pix)
