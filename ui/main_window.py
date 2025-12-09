import os
import json
import time

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QStackedWidget, QLabel
)
from PyQt5.QtCore import QTimer, Qt

from ui.dashboard_page import DashboardPage
from ui.camera_page import CameraPage
from ui.telemetry_page import TelemetryPage
from ui.motors_page import MotorsPage
from ui.params_page import ParamsPage
from ui.pid_page import PIDPage
from ui.motor_test_page import MotorTestPage
from ui.log_page import LogPage
from ui.system_page import SystemPage
from ui.object_page import ObjectPage   # 🔹 YENİ: Nesne Algılama sayfası

from mavlink.mavlink_reader import MavlinkReader
from mavlink.param_manager import ParamManager
from video.camera_worker import CameraWorker
from input.joystick_worker import JoystickWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.showFullScreen()
        self.setMinimumSize(1100, 650)

        self.setWindowTitle("ATK ROV STATION")
        self.setStyleSheet("background-color:#05070B; color:#EAEAEA; font-family:'Segoe UI';")

        self.shared_mav = None
        self.param_manager = None
        self.armed = False

        self.joy_center = None  # AUTO CALIBRATION
        self.throttle = 0.0

        # Durum flagleri
        self.mav_ok = False
        self.camera_ok = False

        self.labelTime = QLabel("--:--:--")
        self.labelPing = QLabel("Ping: -- ms")
        self.labelFPS = QLabel("FPS: --")
        self.labelMav = QLabel("MAVLink: ✖")
        self.labelMode = QLabel("Mod: --")
        self.labelBatt = QLabel("Batarya: -- V %--")
        self.labelTopStatus = QLabel("ROV: ✖   MAVLink: Bekleniyor   Kamera: ✖   Uyarılar: 0")

        self.param_cache_path = os.path.join("cache", "params.json")

        self._build_ui()
        self._build_footer()
        self._start_workers()
        self._start_clock()

    # ===================== KEYS =====================
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.showNormal()
        if event.key() == Qt.Key_F11:
            self.showFullScreen()
        if event.key() == Qt.Key_R:
            self.joy_center = None
            print("🔄 Joystick kalibrasyon reset — tekrar ortada bekle!")

    # ===================== UI =====================
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout()
        central.setLayout(main)

        top = QHBoxLayout()
        title = QLabel("⚡ ATK   ROV STATION")
        title.setStyleSheet("font-size:16px; font-weight:bold; color:#FFD000;")
        top.addWidget(title)
        top.addStretch()
        self.labelTopStatus.setStyleSheet("font-size:11px; color:#E5E7EB;")
        top.addWidget(self.labelTopStatus)
        main.addLayout(top)

        content = QHBoxLayout()
        main.addLayout(content)

        self.menu = QListWidget()
        self.menu.addItems([
            "Gösterge Paneli",
            "Kamera",
            "Telemetri",
            "Motorlar",
            "Parametreler",
            "PID Ayarlari",
            "Motor Test",
            "Kayit / Log",
            "Sistem",
            "Nesne Algılama"      # 🔹 YENİ MENU ITEM
        ])
        self.menu.setFixedWidth(150)

        self.pages = QStackedWidget()

        self.dashboard = DashboardPage()
        self.cameraPage = CameraPage()
        self.telemetryPage = TelemetryPage()
        self.motorsPage = MotorsPage()
        self.paramsPage = ParamsPage()
        self.pidPage = PIDPage()
        self.motorTestPage = MotorTestPage()
        self.logPage = LogPage()
        self.systemPage = SystemPage()
        self.objectPage = ObjectPage()   # 🔹 YENİ SAYFA

        for p in [
            self.dashboard, self.cameraPage, self.telemetryPage, self.motorsPage,
            self.paramsPage, self.pidPage, self.motorTestPage, self.logPage,
            self.systemPage, self.objectPage
        ]:
            self.pages.addWidget(p)

        content.addWidget(self.menu)
        content.addWidget(self.pages)

        self.menu.setCurrentRow(0)
        self.menu.currentRowChanged.connect(self.pages_setIndex)

    # ===================== PAGE SWITCH =====================
    def pages_setIndex(self, index):
        self.pages.setCurrentIndex(index)

    # ===================== FOOTER =====================
    def _build_footer(self):
        bar = QHBoxLayout()

        def style(lbl):
            lbl.setStyleSheet("font-size:11px; padding:2px 5px;")

        for lbl in [
            self.labelTime, self.labelPing, self.labelFPS,
            self.labelMav, self.labelMode, self.labelBatt
        ]:
            style(lbl)

        bar.addWidget(self.labelTime)
        bar.addWidget(QLabel("|"))
        bar.addWidget(self.labelPing)
        bar.addWidget(QLabel("|"))
        bar.addWidget(self.labelFPS)
        bar.addWidget(QLabel("|"))
        bar.addWidget(self.labelMav)
        bar.addWidget(QLabel("|"))
        bar.addWidget(self.labelMode)
        bar.addWidget(QLabel("|"))
        bar.addWidget(self.labelBatt)
        bar.addStretch()

        container = QWidget()
        container.setFixedHeight(24)
        container.setLayout(bar)
        self.centralWidget().layout().addWidget(container)

    # ===================== CLOCK =====================
    def _start_clock(self):
        self._update_time()
        t = QTimer(self)
        t.timeout.connect(self._update_time)
        t.start(1000)

    def _update_time(self):
        self.labelTime.setText(time.strftime("%H:%M:%S"))

    # ===================== START WORKERS =====================
    def _start_workers(self):

        # MAVLINK
        self.mav_worker = MavlinkReader()
        self.mav_worker.connectionStatus.connect(self._on_mavlink_status)
        self.mav_worker.mavReady.connect(self._on_mav_ready)
        self.mav_worker.depthSignal.connect(self.dashboard.update_depth)
        self.mav_worker.headingSignal.connect(self.dashboard.update_heading)
        self.mav_worker.batterySignal.connect(self.dashboard.update_battery)
        self.mav_worker.motorSignal.connect(self.dashboard.update_motors)
        self.mav_worker.start()

        # CAMERA
        self.cam_worker = CameraWorker()
        self.cam_worker.frameSignal.connect(self.dashboard.update_camera_frame)
        self.cam_worker.frameSignal.connect(self.cameraPage.update_camera_frame)
        self.cam_worker.frameSignal.connect(self.objectPage.update_object_frame)  # 🔹 Nesne algılama sayfasına da frame gönder
        self.cam_worker.statusSignal.connect(self._on_camera_status)
        self.cam_worker.start()
        self.cameraPage.set_cam_worker(self.cam_worker)

        # JOYSTICK
        try:
            self.joy = JoystickWorker()
            self.joy.axesSignal.connect(self._on_joy_axes)
            self.joy.buttonsSignal.connect(self._on_joy_buttons)
            self.joy.start()
        except Exception as e:
            print("❌ Joystick başlatılamadı:", e)

        # PARAM CACHE
        if os.path.exists(self.param_cache_path):
            try:
                with open(self.param_cache_path, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                self.paramsPage.show_param_list(cached)
            except:
                pass

    # ===================== STATUS =====================
    def _on_mavlink_status(self, ok: bool):
        self.mav_ok = ok
        self.labelMav.setText("MAVLink: ✓" if ok else "MAVLink: ✖")
        self._update_top_status()

    def _on_mav_ready(self, mav):
        self.shared_mav = mav

    def _on_camera_status(self, text: str, ok: bool = True):
        """
        CameraWorker.statusSignal(text, ok) çağrıldığında gelir.
        Burada sadece kamera durumunu flag'e alıp üst barı güncelliyoruz.
        """
        self.camera_ok = ok
        self._update_top_status()

    def _update_top_status(self):
        rov_txt = "Bağlı" if self.mav_ok else "✖"
        cam_txt = "✓" if self.camera_ok else "✖"

        self.labelTopStatus.setText(
            f"ROV: {rov_txt}   "
            f"{self.labelMav.text()}   "
            f"Kamera: {cam_txt}   "
            f"Uyarılar: 0"
        )

    # ===================== JOYSTICK CALLBACKS =====================
    def _on_joy_axes(self, axes: list):

        # AUTO CALIBRATE ONCE
        if self.joy_center is None and axes:
            self.joy_center = axes[:]
            print("🎯 Joystick merkez kaydedildi:", self.joy_center)

        if self.joy_center is None:
            return

        # APPLY CENTER OFFSET
        axes = [v - c for v, c in zip(axes, self.joy_center)]

        self.throttle = axes[1] if len(axes) > 1 else 0.0
        self._send_motor_outputs(axes)

    def _on_joy_buttons(self, buttons: list):

        # START → ARM
        if len(buttons) > 7 and buttons[7] == 1 and not self.armed:
            self._arm()

        # BACK → DISARM
        if len(buttons) > 6 and buttons[6] == 1 and self.armed:
            if abs(self.throttle) < 0.1:
                self._disarm()
            else:
                print("⚠️ DISARM iptal: throttle yüksek!")

    # ===================== ARM / DISARM =====================
    def _arm(self):
        if not self.shared_mav:
            return
        print("🟢 ARM")
        self.shared_mav.mav.command_long_send(
            self.shared_mav.target_system,
            self.shared_mav.target_component,
            400, 0,
            1, 0, 0, 0, 0, 0, 0
        )
        self.armed = True

    def _disarm(self):
        if not self.shared_mav:
            return
        print("🔴 DISARM")
        self.shared_mav.mav.command_long_send(
            self.shared_mav.target_system,
            self.shared_mav.target_component,
            400, 0,
            0, 0, 0, 0, 0, 0, 0
        )
        self.armed = False

    # ===================== MOTOR MIXING =====================
    def _send_motor_outputs(self, axes):

        if not self.shared_mav:
            return

        # DEADZONE
        def dz(v):
            return 0 if abs(v) < 0.20 else v

        # Aks uzunluk kontrolü
        ax = axes + [0] * (4 - len(axes))  # eksikse 0 ile doldur

        forward = dz(-ax[1])   # İLERİ - GERİ
        strafe  = dz(ax[0])    # SAĞ - SOL (YANA KAYMA)
        updown  = dz(-ax[3])   # YUKARI - AŞAĞI
        yaw     = dz(ax[2])    # SAĞA YAW / SOLA YAW

        pwm = [1500] * 8

        if self.armed:

            # NEUTRAL
            if forward == 0 and strafe == 0 and updown == 0 and yaw == 0:
                pwm = [1500] * 8

            else:
                # FORWARD / BACK
                for i in [4, 5, 6, 7]:
                    pwm[i] += int(forward * 400)

                # STRAFE LEFT/RIGHT
                pwm[4] += int(strafe * 400)   # right
                pwm[6] -= int(strafe * 400)   # left

                # YAW LEFT/RIGHT
                pwm[4] += int(yaw * 400)
                pwm[6] += int(yaw * 400)

                # UP / DOWN
                pwm[2] = int(1500 + updown * 400)
                pwm[3] = int(1500 + updown * 400)

                # LIMIT VALUES
                for i in range(8):
                    pwm[i] = max(1100, min(1900, pwm[i]))

        try:
            self.shared_mav.mav.rc_channels_override_send(
                self.shared_mav.target_system,
                self.shared_mav.target_component,
                pwm[0], pwm[1], pwm[2], pwm[3],
                pwm[4], pwm[5], pwm[6], pwm[7]
            )
        except Exception as e:
            print("RC OVERRIDE ERROR:", e)

    # ===================== CLOSE =====================
    def closeEvent(self, event):
        try:
            self.mav_worker.quit()
            self.mav_worker.wait(500)
        except:
            pass

        try:
            self.cam_worker.stop()
            self.cam_worker.quit()
            self.cam_worker.wait(500)
        except:
            pass

        event.accept()
