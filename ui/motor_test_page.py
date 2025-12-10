from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel
from PyQt5.QtCore import QTimer


class MotorTestPage(QWidget):
    def __init__(self, main):
        super().__init__()

        self.main = main  # erişim için
        self.mav = None
        self.current_timer = None

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("8 Motor Test Paneli")
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(title)

        grid = QGridLayout()
        layout.addLayout(grid)

        # 8 motor için buton oluştur
        for i in range(1, 9):
            btn_fwd = QPushButton(f"Motor {i} İLERİ")
            btn_rev = QPushButton(f"Motor {i} GERİ")
            btn_stop = QPushButton(f"Motor {i} DUR")

            btn_fwd.clicked.connect(lambda _, m=i: self.test_motor(m, 1700))
            btn_rev.clicked.connect(lambda _, m=i: self.test_motor(m, 1300))
            btn_stop.clicked.connect(lambda _, m=i: self.test_motor(m, 1500))

            grid.addWidget(btn_fwd, i - 1, 0)
            grid.addWidget(btn_rev, i - 1, 1)
            grid.addWidget(btn_stop, i - 1, 2)

        # Stop All
        stop_all = QPushButton("⛔ TÜM MOTORLARI DURDUR")
        stop_all.setStyleSheet("background-color:#b30000; color:white;")
        stop_all.clicked.connect(self.stop_all)
        layout.addWidget(stop_all)

    # ================= MOTOR KONTROL ======================

    def test_motor(self, motor_id, value):
        print(f"[MOTOR TEST] Motor {motor_id} → PWM {value}")

        self._send_pwm_single(motor_id, value)

        # 2 saniye sonra durdur
        if self.current_timer:
            self.current_timer.stop()

        self.current_timer = QTimer()
        self.current_timer.timeout.connect(self.stop_all)
        self.current_timer.start(2000)

    def stop_all(self):
        print("⛔ STOP ALL")

        self._send_pwm_all(1500)

        if self.current_timer:
            self.current_timer.stop()
            self.current_timer = None

    # ===== MAVLINK PWM GÖNDERME =====

    def _send_pwm_single(self, motor_id, value):
        mav = self.main.shared_mav  # Doğru MAV nesnesi

        if not mav:
            print("❌ MAV YOK, gönderemedim.")
            return

        pwm = [1500] * 8
        pwm[motor_id - 1] = value  # motor 1 index 0

        mav.mav.rc_channels_override_send(
            mav.target_system,
            mav.target_component,
            pwm[0], pwm[1], pwm[2], pwm[3],
            pwm[4], pwm[5], pwm[6], pwm[7]
        )

    def _send_pwm_all(self, value):
        mav = self.main.shared_mav
        if not mav:
            return

        pwm = [value] * 8

        mav.mav.rc_channels_override_send(
            mav.target_system,
            mav.target_component,
            pwm[0], pwm[1], pwm[2], pwm[3],
            pwm[4], pwm[5], pwm[6], pwm[7]
        )
