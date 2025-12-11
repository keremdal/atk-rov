import time
from pymavlink import mavutil

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QStackedWidget, QLabel
)
from PyQt5.QtCore import Qt, QTimer

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

from video.camera_worker import CameraWorker
from input.joystick_worker import JoystickWorker


class MainWindow(QMainWindow):
    def __init__(self, rov):
        super().__init__()

        self.rov = rov
        self.shared_mav = None

        # STATE
        self.armed = False
        self.mav_ok = False
        self.camera_ok = False

        # JOYSTICK
        self.joy_center = None
        self.last_buttons = []
        self.speed = 0.5

        # WINDOW
        self.showFullScreen()
        self.setMinimumSize(1150, 680)
        self.setWindowTitle("ATK ROV STATION")

        # UI LABELS
        self.labelTime = QLabel("--:--:--")
        self.labelPing = QLabel("Ping: -- ms")
        self.labelFPS = QLabel("FPS: --")
        self.labelMav = QLabel("MAVLink: ✖")
        self.labelMode = QLabel("Mod: --")
        self.labelBatt = QLabel("Batarya: --")
        self.labelStatus = QLabel("Durum: Bekleniyor")

        self._build_ui()
        self._build_footer()
        self._start_workers()
        self._start_clock()

    ###########################################################################
    # UI
    ###########################################################################
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)

        # TOP BAR
        top = QHBoxLayout()
        top.addWidget(QLabel("⚡ ATK ROV STATION"))
        top.addStretch()
        top.addWidget(self.labelStatus)
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
            "PID",
            "Motor Test",
            "Log",
            "Sistem",
            "Nesne Algılama"
        ])
        self.menu.setFixedWidth(160)

        self.pages = QStackedWidget()
        self.dashboard = DashboardPage()
        self.cameraPage = CameraPage()
        self.telemetryPage = TelemetryPage()
        self.motorsPage = MotorsPage()
        self.paramsPage = ParamsPage()
        self.pidPage = PIDPage()
        self.motorTestPage = MotorTestPage(self)
        self.logPage = LogPage()
        self.systemPage = SystemPage()
        self.objectPage = ObjectPage()

        for p in [
            self.dashboard, self.cameraPage, self.telemetryPage,
            self.motorsPage, self.paramsPage, self.pidPage,
            self.motorTestPage, self.logPage, self.systemPage, self.objectPage
        ]:
            self.pages.addWidget(p)

        content.addWidget(self.menu)
        content.addWidget(self.pages)
        self.menu.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.menu.setCurrentRow(0)

    ###########################################################################
    # FOOTER
    ###########################################################################
    def _build_footer(self):
        bar = QHBoxLayout()
        for w in [self.labelTime, self.labelPing, self.labelFPS, self.labelMav, self.labelMode, self.labelBatt]:
            bar.addWidget(w)
            bar.addWidget(QLabel("|"))
        bar.addStretch()

        footer = QWidget()
        footer.setLayout(bar)
        footer.setFixedHeight(26)
        self.centralWidget().layout().addWidget(footer)

    ###########################################################################
    # CLOCK
    ###########################################################################
    def _start_clock(self):
        self._update_time()
        timer = QTimer(self)
        timer.timeout.connect(self._update_time)
        timer.start(1000)

    def _update_time(self):
        self.labelTime.setText(time.strftime("%H:%M:%S"))

    ###########################################################################
    # WORKERS
    ###########################################################################
    def _start_workers(self):

        if hasattr(self.rov, "connectionStatus"):
            self.rov.connectionStatus.connect(self._on_mav_status)

        if hasattr(self.rov, "mavReady"):
            self.rov.mavReady.connect(self._on_mav_ready)

        if hasattr(self.rov, "logSignal"):
            self.rov.logSignal.connect(self.logPage.add_log)

        if hasattr(self.rov, "depthSignal"):
            self.rov.depthSignal.connect(self.dashboard.update_depth)

        if hasattr(self.rov, "headingSignal"):
            self.rov.headingSignal.connect(self.dashboard.update_heading)

        if hasattr(self.rov, "batterySignal"):
            self.rov.batterySignal.connect(self.dashboard.update_battery)

        self.rov.start()

        # CAMERA
        self.cam = CameraWorker()
        self.cam.frameSignal.connect(self.dashboard.update_camera_frame)
        self.cam.frameSignal.connect(self.cameraPage.update_camera_frame)
        self.cam.frameSignal.connect(self.objectPage.update_object_frame)
        self.cam.statusSignal.connect(lambda t, ok=True: None)
        self.cam.start()

        # JOYSTICK
        try:
            self.joy = JoystickWorker()
            self.joy.axesSignal.connect(self._on_axes)
            self.joy.buttonsSignal.connect(self._on_buttons)
            self.joy.start()
            print("🎮 Joystick OK")
        except Exception as e:
            print("❌ Joystick ERROR:", e)

    ###########################################################################
    # MAV
    ###########################################################################
    def _on_mav_ready(self, mav):
        self.shared_mav = mav
        self.mav_ok = True
        self.labelMav.setText("MAVLink: ✓")
        self.labelStatus.setText("MAV: Bağlandı")
        print("🔥 MAV READY")

    def _on_mav_status(self, ok):
        self.mav_ok = ok
        self.labelMav.setText("MAVLink: ✓" if ok else "MAVLink: ✖")

    ###########################################################################
    # ARM / DISARM
    ###########################################################################
    def _arm(self):
        if not self.shared_mav:
            print("❌ ARM: MAV yok")
            return

        print("🟢 ARM")
        self.shared_mav.mav.command_long_send(
            self.shared_mav.target_system,
            self.shared_mav.target_component,
            400,
            0,
            1, 0, 0, 0, 0, 0, 0
        )
        self.armed = True

    def _disarm(self):
        if not self.shared_mav:
            print("❌ DISARM: MAV yok")
            return

        print("🔴 DISARM")
        self.shared_mav.mav.command_long_send(
            self.shared_mav.target_system,
            self.shared_mav.target_component,
            400,
            0,
            0, 0, 0, 0, 0, 0, 0
        )
        self.armed = False

    ###########################################################################
    # MODES
    ###########################################################################
    def _set_mode(self, name, mode_id):
        if not self.shared_mav:
            print("❌ MODE: MAV yok")
            return

        print(f"🎛 MODE → {name}")
        self.labelMode.setText(f"Mod: {name}")

        self.shared_mav.mav.command_long_send(
            self.shared_mav.target_system,
            self.shared_mav.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE,
            0,
            1,
            mode_id,
            0, 0, 0, 0, 0
        )

    ###########################################################################
    # JOYSTICK BUTTONS
    ###########################################################################
    def _on_buttons(self, b):
        if not self.last_buttons:
            self.last_buttons = [0] * len(b)

        # ARM
        if b[7] == 1 and self.last_buttons[7] == 0:
            self._arm()

        # DISARM
        if b[6] == 1 and self.last_buttons[6] == 0:
            self._disarm()

        # X → MANUAL
        if b[2] == 1 and self.last_buttons[2] == 0:
            self._set_mode("MANUAL", 0)

        # Y → STABILIZE
        if b[3] == 1 and self.last_buttons[3] == 0:
            self._set_mode("STABILIZE", 19)

        self.last_buttons = b[:]

    ###########################################################################
    # JOYSTICK AXES (MOTOR CONTROL)
    ###########################################################################
    def _on_axes(self, axes):

        # merkez al
        if self.joy_center is None:
            self.joy_center = axes[:]
            print("🎯 Joystick Center:", self.joy_center)
            return

        axes = [(v - c) for v, c in zip(axes, self.joy_center)]
        axes = [0 if abs(v) < 0.06 else v for v in axes]

        # mapping:
        # SAĞ stick → throttle + lateral
        heave = -axes[3] * self.speed
        strafe = axes[2] * self.speed

        # SOL stick → yaw + forward
        yaw = axes[0] * self.speed
        forward = -axes[1] * self.speed

        # ARM yoksa → dur
        if not (self.armed and self.mav_ok):
            return

        # MANUAL modda motor komutu gönderme (çok önemli!)
        if self.labelMode.text() == "Mod: MANUAL":
            return

        # Stabilize mod → motor gönder
        self.rov.move(
            heave * 500,
            strafe * 500,
            forward * 500
        )

        if hasattr(self.rov, "turnDegrees"):
            self.rov.turnDegrees(yaw * 180)

    ###########################################################################
    # CLOSE
    ###########################################################################
    def closeEvent(self, event):
        try: self.rov.stop()
        except: pass
        try: self.cam.stop()
        except: pass
        try: self.joy.stop()
        except: pass
        event.accept()
