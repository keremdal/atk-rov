import cv2
import numpy as np

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QMainWindow, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage


class ObjectPage(QWidget):
    """
    Nesne algılama sayfası:
      - Kameradan gelen frame burada işleniyor.
      - Basit şekil tabanlı "CUBE" (kare/dikdörtgen) algılama yapıyor.
      - Aynı görüntüyü ayrı bir pencerede de gösterebiliyor.
    """
    def __init__(self):
        super().__init__()

        self.childWindow = None  # Ayrı pencere referansı

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # ÜST BİLGİ METNİ
        self.info = QLabel("NESNE ALGILAMA - CUBE (kare/dikdörtgen) tespiti")
        self.info.setAlignment(Qt.AlignCenter)
        self.info.setStyleSheet("font-size:18px; color:#00D0FF; font-weight:bold;")
        main_layout.addWidget(self.info)

        # ORTA KISIM
        center_layout = QHBoxLayout()
        main_layout.addLayout(center_layout)

        # KAMERA LABEL
        self.cameraLabel = QLabel("KAMERA GÖRÜNTÜSÜ")
        self.cameraLabel.setAlignment(Qt.AlignCenter)
        self.cameraLabel.setMinimumHeight(420)
        self.cameraLabel.setStyleSheet(
            "background-color:#111827; "
            "border-radius:12px; "
            "border:1px solid #374151; "
            "color:#9CA3AF; "
            "font-size:16px;"
        )
        center_layout.addWidget(self.cameraLabel)

        # SAĞDA BUTONLAR
        side_layout = QVBoxLayout()
        side_layout.setSpacing(10)

        self.btnOpen = QPushButton("AYRI PENCEREDE AÇ")
        self.btnOpen.setStyleSheet("""
            QPushButton {
                background-color:#00D0FF;
                color:#000;
                font-size:15px;
                border-radius:8px;
                padding:8px 12px;
            }
            QPushButton:hover {
                background-color:#38E0FF;
            }
        """)
        self.btnOpen.clicked.connect(self.open_window)
        side_layout.addWidget(self.btnOpen)

        side_layout.addStretch()
        center_layout.addLayout(side_layout)

        self.setLayout(main_layout)

    # ================== AYRI PENCERE ==================
    def open_window(self):
        """
        Aynı QLabel'i yeni bir QMainWindow içine koyup 2. ekran gibi gösterir.
        """
        win = QMainWindow()
        win.setWindowTitle("ATK ROV - Nesne Algılama")
        win.setCentralWidget(self.cameraLabel)
        win.resize(1280, 720)
        win.show()
        self.childWindow = win

    # ================== FRAME ALMA + İŞLEME ==================
    def update_object_frame(self, frame):
        """
        MainWindow'dan CameraWorker.frameSignal ile gelen frame'leri işler.
        Küp/kare/dikdörtgen algılama yapar, bounding box ve 'CUBE' etiketi çizer.
        """
        # Kamera yoksa siyah ekran üret
        if frame is None:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

        img = frame.copy()

        # --- Sualtı için kontrast iyileştirme (opsiyonel ama faydalı) ---
        try:
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            lim = cv2.merge((cl, a, b))
            img = cv2.cvtColor(lim, cv2.COLOR_LAB2BGR)
        except Exception as e:
            # Bir hata olursa orijinal img ile devam et
            pass

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 1)
        edges = cv2.Canny(blur, 50, 150)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        h_img, w_img = img.shape[:2]
        frame_center_x = w_img // 2

        cube_center_x = None

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 2000:
                continue  # çok küçük gürültüleri at

            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

            # 4 köşeli ise kare/dikdörtgen ~ "küp yüzü" kabul edelim
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)

                # çok ince şeyleri at (ör: tel, kenar)
                if w < 30 or h < 30:
                    continue

                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 3)
                cv2.putText(
                    img,
                    "CUBE",
                    (x, max(0, y - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                cube_center_x = x + w // 2

        # (İleride buradan hareket komutu türetebilirsin)
        # Örneğin:
        # if cube_center_x is not None:
        #     if cube_center_x < frame_center_x - 50:
        #         print("Küp solda → sola dön")
        #     elif cube_center_x > frame_center_x + 50:
        #         print("Küp sağda → sağa dön")
        #     else:
        #         print("Küp ortada → ileri git")

        # --- PyQt'de göster ---
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytesPerLine = ch * w

        qimg = QImage(img_rgb.data, w, h, bytesPerLine, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)

        self.cameraLabel.setPixmap(pix)
