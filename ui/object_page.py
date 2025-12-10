import cv2
import numpy as np
from ultralytics import YOLO

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QMainWindow
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage


class YoloThread(QThread):
    """
    YOLO modeli ayrı thread içinde çalışır -> UI donmaz.
    """
    resultSignal = pyqtSignal(object, object)  # (img, results)

    def __init__(self, model_path="models/best.pt"):
        super().__init__()
        self.model = YOLO(model_path)
        self.last_frame = None
        self.running = True

    def run(self):
        while self.running:
            if self.last_frame is None:
                self.msleep(5)
                continue

            frame = self.last_frame.copy()

            results = self.model(
                frame,
                imgsz=480,
                conf=0.45,
                max_det=10,
                verbose=False
            )

            self.resultSignal.emit(frame, results)
            self.msleep(5)

    def set_frame(self, frame):
        self.last_frame = frame

    def stop(self):
        self.running = False
        self.wait(500)


class ObjectPage(QWidget):
    """
    YOLO Nesne Algılama Sayfası
    """
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("YOLO Nesne Algılama (models/best.pt)")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:20px; font-weight:bold; color:#FFD000;")
        layout.addWidget(title)

        self.cameraLabel = QLabel("Görüntü bekleniyor...")
        self.cameraLabel.setAlignment(Qt.AlignCenter)
        self.cameraLabel.setMinimumHeight(420)
        self.cameraLabel.setStyleSheet(
            "background-color:#000; border:1px solid #333; border-radius:8px;"
        )
        layout.addWidget(self.cameraLabel)

        self.popupBtn = QPushButton("Ayır Pencere Aç")
        self.popupBtn.clicked.connect(self.openPopup)
        layout.addWidget(self.popupBtn)

        self.setLayout(layout)

        self.popupWindow = None
        self.popupLabel = None

        # YOLO thread başlat
        self.yolo_thread = YoloThread("models/best.pt")
        self.yolo_thread.resultSignal.connect(self.updateResult)
        self.yolo_thread.start()

    # Kamera worker burayı çağıracak
    def update_object_frame(self, frame):
        self.yolo_thread.set_frame(frame)

    def updateResult(self, img_bgr, results):
        det = results[0]

        # bounding box çiz
        if det.boxes is not None:
            names = det.names
            for box in det.boxes:
                x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                label = names.get(cls, str(cls))

                cv2.rectangle(img_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    img_bgr,
                    f"{label} {conf:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytesPerLine = ch * w
        qimg = QImage(img_rgb.data, w, h, bytesPerLine, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)

        # Ana sayfa
        self.cameraLabel.setPixmap(pix)

        # Popup varsa
        if self.popupLabel:
            self.popupLabel.setPixmap(pix)

    def openPopup(self):
        if self.popupWindow:
            self.popupWindow.raise_()
            return

        win = QMainWindow()
        win.setWindowTitle("YOLO Pop-up")

        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("background:#000;")
        win.setCentralWidget(label)

        win.resize(960, 540)
        win.show()

        self.popupWindow = win
        self.popupLabel = label

    def shutdown(self):
        try:
            self.yolo_thread.stop()
        except:
            pass

        if self.popupWindow:
            self.popupWindow.close()
