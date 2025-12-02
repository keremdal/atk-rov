from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QListWidget, QProgressBar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        self.camStatus = QLabel("🔴 Kamera bağlı değil")
        self.camStatus.setStyleSheet("font-size:15px; font-weight:bold; color:#FF4444;")
        self.camStatus.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.camStatus)

        self.cameraLabel = QLabel("CAMERA")
        self.cameraLabel.setFixedHeight(350)
        self.cameraLabel.setAlignment(Qt.AlignCenter)
        self.cameraLabel.setStyleSheet(
            "background-color:#14171c; border-radius:12px; "
            "border:1px solid #2A3441; font-size:22px; color:#8C99A5;"
        )
        layout.addWidget(self.cameraLabel)

        midLayout = QHBoxLayout()

        cardsLayout = QHBoxLayout()
        self.depthCard, self.depthLabel = self._make_card("Derinlik", "-- m")
        self.headingCard, self.headingLabel = self._make_card("Heading", "--°")
        self.battCard, self.battLabel = self._make_card("Batarya", "-- V")

        cardsLayout.addWidget(self.depthCard)
        cardsLayout.addWidget(self.headingCard)
        cardsLayout.addWidget(self.battCard)

        leftMid = QVBoxLayout()
        leftMid.addLayout(cardsLayout)

        motorsLayout = QGridLayout()
        motorsLayout.setSpacing(6)
        self.motorBars = []
        for i in range(8):
            mName = QLabel(f"M{i+1}")
            bar = QProgressBar()
            bar.setMaximum(100)
            bar.setValue(0)
            bar.setStyleSheet("QProgressBar::chunk{ background-color:#FFD000; }")

            val = QLabel("0%")

            motorsLayout.addWidget(mName, i, 0)
            motorsLayout.addWidget(bar, i, 1)
            motorsLayout.addWidget(val, i, 2)

            self.motorBars.append((bar, val))

        leftMid.addLayout(motorsLayout)
        midLayout.addLayout(leftMid)

        self.logList = QListWidget()
        self.logList.addItem("Log sistemi hazir")
        self.logList.setFixedWidth(350)
        self.logList.setStyleSheet("background-color:#111821; border-radius:10px;")
        midLayout.addWidget(self.logList)

        layout.addLayout(midLayout)
        self.setLayout(layout)


    def _make_card(self, title, value):
        frame = QFrame()
        frame.setStyleSheet(
            "background-color:#111821; border-radius:10px; border:1px solid #2A3441;"
        )
        vlayout = QVBoxLayout()
        t = QLabel(title)
        v = QLabel(value)
        t.setStyleSheet("font-size:14px; color:#9DA6B2;")
        v.setStyleSheet("font-size:28px; font-weight:bold; color:white;")
        vlayout.addWidget(t)
        vlayout.addWidget(v)
        frame.setLayout(vlayout)
        return frame, v

    def update_depth(self, d):
        self.depthLabel.setText(f"{d:.2f} m")

    def update_heading(self, h):
        self.headingLabel.setText(f"{h:.0f}°")

    def update_battery(self, volt, percent):
        self.battLabel.setText(f"{volt:.2f} V / %{percent:.0f}")

    def update_motors(self, motors):
        for i, val in enumerate(motors):
            bar, label = self.motorBars[i]
            bar.setValue(abs(val))
            label.setText(f"{val}%")

    # ============= KAMERA =============
    def update_camera_frame(self, frame):
        """
        frame buraya her zaman QImage olarak gelecek — None gelebilir.
        """
        if frame is None:
            self.camStatus.setText("🔴 Kamera yok")
            self.camStatus.setStyleSheet(
                "font-size:15px; font-weight:bold; color:#FF4444;"
            )
            self.cameraLabel.setText("NO SIGNAL")
            return

        # Frame QImage garantilidir
        if isinstance(frame, QImage):
            self.camStatus.setText("🟢 Kamera aktif")
            self.camStatus.setStyleSheet(
                "font-size:15px; font-weight:bold; color:#00FF66;"
            )

            pix = QPixmap.fromImage(frame)
            self.cameraLabel.setPixmap(pix)
            self.cameraLabel.setScaledContents(True)
        else:
            self.camStatus.setText("⚠️ Kamera format hatası")
            self.camStatus.setStyleSheet(
                "font-size:15px; font-weight:bold; color:#FFBB00;"
            )
            self.cameraLabel.setText("FRAME ERROR")
