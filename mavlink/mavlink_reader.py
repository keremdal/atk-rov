import time
from threading import Thread
from pymavlink import mavutil
from PyQt5.QtCore import QObject, pyqtSignal

class MavlinkReader(QObject):
    connectionStatus = pyqtSignal(bool)
    mavReady = pyqtSignal(object)

    depthSignal = pyqtSignal(float)
    headingSignal = pyqtSignal(float)
    batterySignal = pyqtSignal(float, float)

    logSignal = pyqtSignal(str)  # <-- EKLENDİ

    def __init__(self):
        super().__init__()
        self.master = None
        self.running = False

    # ----------------------------------------------------------------------
    def start(self):
        self.running = True
        Thread(target=self._connect, daemon=True).start()

    def stop(self):
        self.running = False

    # ----------------------------------------------------------------------
    def _connect(self):
        self.log("AUTO SCAN starting...")

        for port in ["udp:0.0.0.0:14550", "udp:0.0.0.0:14552"]:
            try:
                self.log(f"Trying → {port}")
                self.master = mavutil.mavlink_connection(port, autoreconnect=True)
                self.master.wait_heartbeat(timeout=5)
                self.log("✔ MAVLINK CONNECTED")
                self.connectionStatus.emit(True)
                self.mavReady.emit(self.master)
                self._loop()
                return
            except:
                self.log("❌ FAILED")

        self.connectionStatus.emit(False)
        self.log("❌ No connection")

    # ----------------------------------------------------------------------
    def _loop(self):
        while self.running:
            msg = self.master.recv_match(blocking=True, timeout=1)
            if not msg:
                continue

            mtype = msg.get_type()

            if mtype == "VFR_HUD":
                self.headingSignal.emit(msg.heading)

            elif mtype == "GLOBAL_POSITION_INT":
                depth = msg.relative_alt / 1000.0
                self.depthSignal.emit(depth)

            elif mtype == "SYS_STATUS":
                volt = msg.voltage_battery / 1000.0
                batt = msg.battery_remaining
                self.batterySignal.emit(volt, batt)

            elif mtype == "STATUSTEXT":
                self.log(f"[PX4] {msg.text}")  # <--- PIXHAWK LOG

    # ----------------------------------------------------------------------
    # SAFE NEUTRAL - NO BEEP
    # ----------------------------------------------------------------------
    def safe_neutral(self):
        try:
            self.master.mav.manual_control_send(
                self.master.target_system,
                0, 0, 1500, 0, 0
            )
        except:
            pass

    # ----------------------------------------------------------------------
    # MOVE
    # ----------------------------------------------------------------------
    def move(self, heave, strafe, surge):
        try:
            self.master.mav.manual_control_send(
                self.master.target_system,
                surge, strafe, 1500 + heave, 0, 0
            )
        except:
            pass

    # ----------------------------------------------------------------------
    def turn(self, yaw):
        try:
            self.master.mav.manual_control_send(
                self.master.target_system,
                0, 0, 1500, yaw, 0
            )
        except:
            pass

    # ----------------------------------------------------------------------
    def log(self, text):
        print(text)
        self.logSignal.emit(text)
