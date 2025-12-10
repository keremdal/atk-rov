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
from input.joy_center import load_center, save_center


class MainWindow(QMainWindow):
    def __init__(self, rov):
        super().__init__()

        self.rov = rov
        self.shared_mav = None
        self.target_sys = None
        self.target_comp = None
        self.armed = False

        self.joy_center = load_center()
        self.cmd_surge = 0.0
        self.cmd_strafe = 0.0
        self.cmd_throttle = 0.0
        self.cmd_yaw = 0.0
        self.speed_factor = 1.0

        self.last_start_btn = 0
        self.last_back_btn = 0

        self.manual_block_until = 0  # NEW !!!

        self.mav_ok = False
        self.camera_ok = False

        self._build_ui()
        self._build_footer()
        self._start_workers()
        self._start_clock()

        self.showFullScreen()
        self.setWindowTitle("ATK ROV STATION")

        # CONTROL LOOP
        self.ctrl_timer = QTimer(self)
        self.ctrl_timer.timeout.connect(self._send_manual_control)
        self.ctrl_timer.start(50)

        # HEARTBEAT GCS
        self.hb_timer = QTimer(self)
        self.hb_timer.timeout.connect(self._send_gcs_heartbeat)
        self.hb_timer.start(1000)

    # =================== UI ======================
    def _build_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        main = QVBoxLayout(central)

        top = QHBoxLayout()
        title = QLabel("⚡ ATK ROV STATION")
        title.setStyleSheet("font-size:17px; font-weight:bold; color:#FFD000;")
        top.addWidget(title)

        self.labelTop = QLabel("ROV: ✖   MAVLink: Bekleniyor   Kamera: ✖   Speed: x1.0")
        top.addStretch()
        top.addWidget(self.labelTop)
        main.addLayout(top)

        body = QHBoxLayout()
        main.addLayout(body)

        self.menu = QListWidget()
        self.menu.addItems([
            "Gösterge Paneli",
            "Kamera",
            "Telemetri",
            "Motorlar",
            "Parametreler",
            "PID Ayarları",
            "Motor Test",
            "Kayıt / Log",
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
            self.motorTestPage, self.logPage, self.systemPage,
            self.objectPage
        ]:
            self.pages.addWidget(p)

        body.addWidget(self.menu)
        body.addWidget(self.pages)

        self.menu.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.menu.setCurrentRow(0)

    # =================== FOOTER ======================
    def _build_footer(self):
        bar = QHBoxLayout()
        self.labelTime = QLabel("--:--:--")
        self.labelSpeed = QLabel("Speed: x1.0")

        for w in [self.labelTime, self.labelSpeed]:
            w.setStyleSheet("font-size:11px; padding:2px 4px;")

        bar.addWidget(self.labelTime)
        bar.addWidget(QLabel("|"))
        bar.addWidget(self.labelSpeed)
        bar.addStretch()

        footer = QWidget()
        footer.setFixedHeight(24)
        footer.setLayout(bar)
        self.centralWidget().layout().addWidget(footer)

    # =================== CLOCK ======================
    def _start_clock(self):
        t = QTimer(self)
        t.timeout.connect(lambda: self.labelTime.setText(time.strftime("%H:%M:%S")))
        t.start(1000)

    # =================== WORKERS ======================
    def _start_workers(self):
        self.rov.connectionStatus.connect(self._on_mav_status)
        self.rov.mavReady.connect(self._on_mav_ready)
        self.rov.depthSignal.connect(self.dashboard.update_depth)
        self.rov.headingSignal.connect(self.dashboard.update_heading)
        self.rov.batterySignal.connect(self.dashboard.update_battery)
        self.rov.start()

        self.cam_worker = CameraWorker()
        self.cam_worker.frameSignal.connect(self.dashboard.update_camera_frame)
        self.cam_worker.frameSignal.connect(self.cameraPage.update_camera_frame)
        self.cam_worker.frameSignal.connect(self.objectPage.update_object_frame)
        self.cam_worker.statusSignal.connect(self._on_camera_status)
        self.cam_worker.start()
        self.cameraPage.set_cam_worker(self.cam_worker)

        self.joy = JoystickWorker()
        self.joy.axesSignal.connect(self._on_joy_axes)
        self.joy.buttonsSignal.connect(self._on_joy_buttons)
        self.joy.hatSignal.connect(self._on_hat)
        self.joy.start()

    # =================== STATUS ======================
    def _on_mav_status(self, ok: bool):
        self.mav_ok = ok
        self._update_top()

    def _on_camera_status(self, text, ok=True):
        self.camera_ok = ok
        self._update_top()

    def _update_top(self):
        self.labelTop.setText(
            f"RO: {'✓' if self.mav_ok else '✖'}   "
            f"MAVLink: {'✓' if self.mav_ok else '✖'}   "
            f"Kamera: {'✓' if self.camera_ok else '✖'}   "
            f"Speed: x{self.speed_factor:.1f}"
        )

    # =================== MAV READY ======================
    def _on_mav_ready(self, mav):
        print("🔥 SHARED_MAV READY")
        self.shared_mav = mav
        self.target_sys = mav.target_system or 1
        self.target_comp = mav.target_component or 1
        print(f"🎯 USING SYS={self.target_sys} COMP={self.target_comp}")

    # =================== AXES ======================
    def _on_joy_axes(self, axes):
        if len(axes) < 4:
            return

        if self.joy_center is None:
            self.joy_center = [round(a, 3) for a in axes[:4]]
            save_center(self.joy_center)
            print("🎯 Center alındı:", self.joy_center)
            return

        axes = [v - c for v, c in zip(axes[:4], self.joy_center)]

        lx = axes[0]
        ly = axes[1]
        rx = axes[2]
        ry = axes[3]

        self.cmd_surge = 0 if abs(-ly) < 0.12 else -ly
        self.cmd_yaw = 0 if abs(lx) < 0.12 else lx
        self.cmd_strafe = 0 if abs(rx) < 0.12 else rx
        self.cmd_throttle = 0 if abs(-ry) < 0.12 else -ry

    # =================== BUTTONS ======================
    def _on_joy_buttons(self, buttons):
        start = buttons[7] if len(buttons) > 7 else 0
        back = buttons[6] if len(buttons) > 6 else 0

        if start == 1 and self.last_start_btn == 0:
            self._arm()

        if back == 1 and self.last_back_btn == 0:
            self._disarm()

        self.last_start_btn = start
        self.last_back_btn = back

    # =================== D-PAD ======================
    def _on_hat(self, hat):
        x, y = hat
        if y == 1:
            self.speed_factor = min(self.speed_factor + 0.1, 2.0)
        elif y == -1:
            self.speed_factor = max(self.speed_factor - 0.1, 0.2)

        self.labelSpeed.setText(f"Speed: x{self.speed_factor:.1f}")
        self._update_top()

    # =================== ARM / DISARM ======================
    def _arm(self):
        if not self.shared_mav:
            return

        print("🟢 ARM")

        self.shared_mav.mav.command_long_send(
            self.target_sys, self.target_comp,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1, 0, 0, 0, 0, 0, 0
        )

        self.armed = True

        # BLOCK manual control 1 sec (FIX)
        self.manual_block_until = time.time() + 1.0

    def _disarm(self):
        if not self.shared_mav:
            return
        print("🔴 DISARM")

        self.shared_mav.mav.command_long_send(
            self.target_sys, self.target_comp,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            0, 0, 0, 0, 0, 0, 0
        )

        self.armed = False

    # =================== GCS HEARTBEAT ======================
    def _send_gcs_heartbeat(self):
        if not self.shared_mav:
            return

        self.shared_mav.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_GCS,
            mavutil.mavlink.MAV_AUTOPILOT_INVALID,
            0, 0,
            mavutil.mavlink.MAV_STATE_ACTIVE
        )

    # =================== MANUAL CONTROL ======================
    def _send_manual_control(self):
        if not self.shared_mav or not self.target_sys:
            return

        # BLOCK AFTER ARM
        if time.time() < self.manual_block_until:
            # neutral
            self.shared_mav.mav.manual_control_send(
                self.target_sys,
                0, 0, 500, 0,
                0
            )
            return

        if not self.armed:
            self.shared_mav.mav.manual_control_send(
                self.target_sys,
                0, 0, 500, 0,
                0
            )
            return

        sf = self.speed_factor

        surge = max(-1, min(1, self.cmd_surge * sf))
        strafe = max(-1, min(1, self.cmd_strafe * sf))
        yaw = max(-1, min(1, self.cmd_yaw * sf))
        thr = max(-1, min(1, self.cmd_throttle * sf))

        x = int(surge * 1000)
        y = int(strafe * 1000)
        r = int(yaw * 1000)
        z = int((1 - thr) * 500)

        z = max(0, min(z, 1000))

        self.shared_mav.mav.manual_control_send(
            self.target_sys,
            x, y, z, r,
            0
        )

    # =================== CLOSE ======================
    def closeEvent(self, event):
        try:
            self.joy.stop()
        except:
            pass
        try:
            self.cam_worker.stop()
        except:
            pass
        try:
            self.rov.stop()
        except:
            pass
        event.accept()
