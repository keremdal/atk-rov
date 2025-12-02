from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QFrame
from PyQt5.QtCore import Qt

class TelemetryPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        title = QLabel("📡 Telemetri Detayları")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color:#FFD000;")
        layout.addWidget(title)

        gridFrame = QFrame()
        gridFrame.setStyleSheet("""
            QFrame {
                background-color:#111821;
                border-radius:10px;
                border:1px solid #2A3441;
            }
        """)
        grid = QGridLayout()
        grid.setContentsMargins(15, 15, 15, 15)
        grid.setHorizontalSpacing(25)
        grid.setVerticalSpacing(12)

        # etiketler
        lbl_depth_t = QLabel("Derinlik:")
        lbl_heading_t = QLabel("Heading (Yaw):")
        lbl_batt_t = QLabel("Batarya:")

        self.lbl_depth_v = QLabel("-- m")
        self.lbl_heading_v = QLabel("--°")
        self.lbl_batt_v = QLabel("-- V / %--")

        for l in (lbl_depth_t, lbl_heading_t, lbl_batt_t,
                  self.lbl_depth_v, self.lbl_heading_v, self.lbl_batt_v):
            l.setStyleSheet("font-size: 16px;")

        grid.addWidget(lbl_depth_t,   0, 0, alignment=Qt.AlignLeft)
        grid.addWidget(self.lbl_depth_v, 0, 1, alignment=Qt.AlignLeft)

        grid.addWidget(lbl_heading_t, 1, 0, alignment=Qt.AlignLeft)
        grid.addWidget(self.lbl_heading_v, 1, 1, alignment=Qt.AlignLeft)

        grid.addWidget(lbl_batt_t,    2, 0, alignment=Qt.AlignLeft)
        grid.addWidget(self.lbl_batt_v, 2, 1, alignment=Qt.AlignLeft)

        gridFrame.setLayout(grid)
        layout.addWidget(gridFrame)

        self.setLayout(layout)

    # Dashboard ile aynı sinyalleri kullanacağız:
    def update_depth(self, d: float):
        self.lbl_depth_v.setText(f"{d:.2f} m")

    def update_heading(self, h: float):
        self.lbl_heading_v.setText(f"{h:.0f}°")

    def update_battery(self, volt: float, percent: float):
        self.lbl_batt_v.setText(f"{volt:.2f} V / %{percent:.0f}")
