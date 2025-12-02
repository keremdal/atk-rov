import cv2
from PyQt5.QtCore import QThread, pyqtSignal

class CameraWorker(QThread):
    frameSignal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        print("KAMERA: RTSP hızlı mod ile başlatılıyor...")

        pipeline = (
            "rtspsrc location=rtsp://192.168.2.2:8554/video_stream__dev_video0 latency=0 ! "
            "decodebin ! videoconvert ! appsink"
        )

        cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

        if not cap.isOpened():
            print("❗ RTSP AÇILMADI — şimdilik bekleme modunda...")
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue
            self.frameSignal.emit(frame)

        cap.release()

    def stop(self):
        self.running = False

    # GUI bozulmasın diye boş fonksiyonlar
    def start_record(self):
        pass

    def stop_record(self):
        pass
