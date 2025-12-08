from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QSlider
from PyQt5.QtCore import Qt

class MotorTestPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(20)

        title = QLabel("🧪 Motor Test Sistemi")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color:#FFD000;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(12)

        self.sliders = []

        for i in range(8):
            lbl = QLabel(f"M{i+1}")
            lbl.setStyleSheet("font-size: 17px;")
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(-100)
            slider.setMaximum(100)
            slider.setValue(0)
            slider.setEnabled(False)

            grid.addWidget(lbl, i, 0)
            grid.addWidget(slider, i, 1)

            self.sliders.append(slider)

        layout.addLayout(grid)

        warn = QLabel("⚠️ Gerçek motora komut gönderme henüz aktif değil.")
        warn.setAlignment(Qt.AlignCenter)
        warn.setStyleSheet("font-size: 14px; color: #FFA000;")
        layout.addWidget(warn)

        self.setLayout(layout)
