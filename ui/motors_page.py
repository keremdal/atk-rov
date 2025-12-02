from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout
from PyQt5.QtCore import Qt

class MotorsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(20)

        title = QLabel("🔧 Motor Durumları")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFD000;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(10)
        self.motorLabels = []

        for i in range(8):
            lbl1 = QLabel(f"M{i+1}")
            lbl1.setStyleSheet("font-size: 17px;")

            lbl2 = QLabel("0%")
            lbl2.setStyleSheet("font-size: 17px; color:#FFD000;")

            self.motorLabels.append(lbl2)

            grid.addWidget(lbl1, i, 0)
            grid.addWidget(lbl2, i, 1)

        layout.addLayout(grid)
        self.setLayout(layout)

    def update_motors(self, motors):
        for i, val in enumerate(motors):
            self.motorLabels[i].setText(f"{val}%")
