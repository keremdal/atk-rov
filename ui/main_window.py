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
from ui.object_page import ObjectPage

from mavlink.mavlink_reader import MavlinkReader
from mavlink.param_manager import ParamManager
from video.camera_worker import CameraWorker
from input.joystick_worker import JoystickWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # FULLSCREEN
        self.showFullScreen()
        self.setMinimumSize(1100, 650)
        self.setWindowTitle("ATK ROV STATION")

        self.setStyleSheet("background-color:#05070B; color:#EAEAEA; font-family:'Segoe UI';")

        self.shared_mav = None
        self.param_manager = None

        # TOP LABELS
        self.labelTime = QLabel("--:--:--")
        self.labelPing = QLabel("Ping: -- ms")
        self.labelFPS = QLabel("FPS: --")
        self.labelMav = QLabel("MAVLink: ✖")
        self.labelMode = QLabel("Mod: --")
        self.labelBatt = QLabel("Batarya: -- V %--")
        self.labelTopStatus = QLabel("ROV: ✖   MAVLink: Bekleniyor   Kamera: ?   Uyarılar: 0")

        self.param_cache_path = os.path.join("cache", "params.json")

        self._build_ui()
        self._build_footer()
        self._start_workers()
        self._start_clock()

    # FULLSCREEN KEY
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.showNormal()
        if event.key() == Qt.Key_F11:
            self.showFullScreen()

    # UI BUILD
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout()
        central.setLayout(main)

        # TOP BAR
        top = QHBoxLayout()
        title = QLabel("⚡ ATK ROV STATION")
        title.setStyleSheet("font-size:16px; font-weight:bold; color:#FFD000;")
        top.addWidget(title)
        top.addStretch()

        self.labelTopStatus.setStyleSheet("font-size:11px; color:#E5E7EB;")
        top.addWidget(self.labelTopStatus)
        main.addLayout(top)

        # MIDDLE
        content = QHBoxLayout()
        main.addLayout(content)

        # MENU
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
            "Görüntü İşleme"  # <-- NEW
        ])
        self.menu.setFixedWidth(150)
        self.menu.currentRowChanged.connect(self.pages_setIndex)

        # PAGES
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
        self.objectPage = ObjectPage()

        for p in [
            self.dashboard, self.cameraPage, self.telemetryPage,
            self.motorsPage, self.paramsPage, self.pidPage,
            self.motorTestPage, self.logPage, self.systemPage,
            self.objectPage
        ]:
            self.pages.addWidget(p)

        content.addWidget(self.menu)
        content.addWidget(self.pages)
        self.menu.setCurrentRow(0)

    # FOOTER
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

    # CLOCK
    def _start_clock(self):
        self._update_time()
        t = QTimer(self)
        t.timeout.connect(self._update_time)
        t.start(1000)

    def _update_time(self):
        self.labelTime.setText(time.strftime("%H:%M:%S"))

    # PAGE SWITCH
    def pages_setIndex(self, index):
        self.pages.setCurrentIndex(index)

    # WORKERS
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
        self.cam_worker.frameSignal.connect(self.objectPage.update_object_frame)
        self.cam_worker.statusSignal.connect(self._on_camera_status)
        self.cam_worker.start()

        # JOYSTICK
        try:
            self.joy = JoystickWorker()
            self.joy.statusSignal.connect(self._on_joy_status)
            self.joy.axesSignal.connect(self._on_joy_axes)
            self.joy.buttonsSignal.connect(self._on_joy_buttons)
            self.joy.start()
        except Exception as e:
            print("❌ Joystick başlatılamadı:", e)

    # STATUS UPDATE
    def _on_mavlink_status(self, ok: bool):
        self.labelMav.setText("MAVLink: ✓" if ok else "MAVLink: ✖")
        self._update_top_status()

    def _on_mav_ready(self, mav):
        self.shared_mav = mav

    def _on_camera_status(self, text: str, ok: bool = True):
        self._update_top_status()

    def _on_joy_status(self, ok: bool):
        pass

    def _on_joy_axes(self, axes):
        pass

    def _on_joy_buttons(self, buttons):
        pass

    def _update_top_status(self):
        cam = "✓"
        self.labelTopStatus.setText(
            f"ROV: {'Bağlı' if '✓' in self.labelMav.text() else '✖'}   "
            f"{self.labelMav.text()}   Kamera: {cam}   Uyarılar: 0"
        )

    # CLOSE
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
