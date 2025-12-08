from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()

        # Telemetri değerleri
        self._depth = None
        self._heading = None
        self._voltage = None
        self._batt_pct = None

        self._build_ui()
        self._setup_overlay()
        self._setup_timer()

    # ------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # İstersen üstte küçük bir status text de bırakabiliriz
        self.camStatus = QLabel("KAMERA")
        self.camStatus.setAlignment(Qt.AlignCenter)
        self.camStatus.setStyleSheet(
            "font-size:14px; font-weight:bold; color:#E5E7EB;"
        )
        layout.addWidget(self.camStatus)

        # BÜYÜK KAMERA ALANI
        self.cameraLabel = QLabel("CAMERA")
        self.cameraLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cameraLabel.setMinimumHeight(600)
        self.cameraLabel.setAlignment(Qt.AlignCenter)
        self.cameraLabel.setStyleSheet(
            "background-color:#14171c; "
            "border:1px solid #2A3441; "
            "border-radius:12px; "
            "font-size:24px; "
            "color:#FFFFFF;"
        )
        layout.addWidget(self.cameraLabel)

        self.setLayout(layout)

    # ------------------------------------------------------
    def _setup_overlay(self):
        # Sağ alt köşede küçük beyaz yazı
        self.overlay = QLabel(self.cameraLabel)
        self.overlay.setStyleSheet(
            "color: white; font-size: 14px; "
            "background-color: rgba(0,0,0,140); "
            "padding:3px 6px; border-radius:6px;"
        )
        self.overlay.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.overlay.resize(230, 28)
        self.overlay.move(
            self.cameraLabel.width() - self.overlay.width() - 10,
            self.cameraLabel.height() - self.overlay.height() - 10
        )
        self._refresh_overlay()

    def _setup_timer(self):
        # Pencere yeniden boyutlandıkça overlay pozisyonunu düzelt
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._fix_overlay_position)
        self._timer.start(400)

    def _fix_overlay_position(self):
        self.overlay.move(
            self.cameraLabel.width() - self.overlay.width() - 10,
            self.cameraLabel.height() - self.overlay.height() - 10
        )

    # ------------------------------------------------------
    # KAMERA FRAME GÜNCELLEME
    def update_camera_frame(self, frame):
        if frame is None:
            return

        # frame: BGR -> RGB
        try:
            h, w, ch = frame.shape
        except Exception:
            return

        bytes_per_line = ch * w
        img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)

        self.cameraLabel.setPixmap(
            pix.scaled(
                self.cameraLabel.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    # ------------------------------------------------------
    # MAVLINK SİNYALLERİ İÇİN FONKSİYONLAR
    # Bunları MainWindow kullanıyor.

    def update_depth(self, depth: float):
        self._depth = depth
        self._refresh_overlay()

    def update_heading(self, heading: float):
        self._heading = heading
        self._refresh_overlay()

    def update_battery(self, voltage: float, percent: float = None):
        self._voltage = voltage
        self._batt_pct = percent
        self._refresh_overlay()

    def update_motors(self, *args, **kwargs):
        # Motor barlarını ekranda göstermiyoruz ama
        # sinyali boşa atmak için fonksiyon var.
        pass

    # ------------------------------------------------------
    def _refresh_overlay(self):
        # None olanları "--" göster
        d = f"{self._depth:.1f}m" if self._depth is not None else "--m"
        h = f"{self._heading:.0f}°" if self._heading is not None else "--°"
        if self._voltage is not None:
            if self._batt_pct is not None:
                b = f"{self._voltage:.1f}V %{int(self._batt_pct)}"
            else:
                b = f"{self._voltage:.1f}V"
        else:
            b = "--V"

        self.overlay.setText(f"D: {d}   HDG: {h}   BAT: {b}")
