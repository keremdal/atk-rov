from pymavlink import mavutil
from PyQt5.QtCore import QThread, pyqtSignal
import time
import os


class MavlinkReader(QThread):
    depthSignal = pyqtSignal(float)
    headingSignal = pyqtSignal(float)
    batterySignal = pyqtSignal(float, float)
    motorSignal = pyqtSignal(list)
    connectionStatus = pyqtSignal(bool)
    mavReady = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.master = None
        self.running = True

        # === LOG FILE ===
        os.makedirs("logs", exist_ok=True)
        logname = time.strftime("logs/pixhawk_%Y-%m-%d.txt")
        self.logfile = open(logname, "a")

    # =====================================================
    # LOG FUNCTION
    # =====================================================
    def log(self, txt):
        t = time.strftime("%H:%M:%S")
        line = f"[{t}] {txt}"
        print(line)

        try:
            self.logfile.write(line + "\n")
            self.logfile.flush()
        except:
            pass

    # =====================================================
    # THREAD MAIN
    # =====================================================
    def run(self):
        self.log("MAVLINK AUTO SCAN starting...\n")

        connections = [
            'udp:0.0.0.0:14550',
            'udp:0.0.0.0:14552'
        ]

        # =================================================
        # CONNECTION SCAN
        # =================================================
        for c in connections:
            try:
                self.log(f"Trying → {c}")
                m = mavutil.mavlink_connection(c, autoreconnect=True, timeout=2)

                msg = m.recv_match(type='HEARTBEAT', blocking=True, timeout=2)
                if msg:
                    self.master = m
                    self.log(f"✔ MAVLINK CONNECTED → {c}")
                    break

            except:
                continue

        if not self.master:
            self.log("❌ MAVLINK FAILED")
            self.connectionStatus.emit(False)
            return

        # =================================================
        # HEARTBEAT WAIT
        # =================================================
        self.log("Waiting HEARTBEAT...")
        hb = self.master.recv_match(type='HEARTBEAT', blocking=True, timeout=3)

        if not hb:
            self.log("❌ NO HEARTBEAT")
            self.connectionStatus.emit(False)
            return

        self.log("💓 HEARTBEAT OK")

        # TARGET INFO
        self.master.target_system = 1
        self.master.target_component = hb.autopilot

        self.log(f"🎯 Updated Target System: {self.master.target_system}")
        self.log(f"🎯 Updated Target Component: {self.master.target_component}")

        self.mavReady.emit(self.master)
        self.connectionStatus.emit(True)

        # =================================================
        # MAIN MAV LOOP
        # =================================================
        while self.running:
            try:
                msg = self.master.recv_match(blocking=False)

                if not msg:
                    continue

                t = msg.get_type()

                # === LOG EVENTS ===
                if t == "HEARTBEAT":
                    mode = msg.custom_mode
                    armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
                    self.log(f"HEARTBEAT → MODE={mode} ARMED={armed}")

                if t == "STATUSTEXT":
                    self.log(f"STATUSTEXT: {msg.severity} → {msg.text}")

                if t == "SYS_STATUS":
                    v = msg.voltage_battery / 1000
                    c = msg.current_battery / 100
                    self.batterySignal.emit(v, c)

                    if msg.errors_count1 or msg.errors_count2 or msg.errors_count3 or msg.errors_count4:
                        self.log(f"ERRORS: {msg.errors_count1} {msg.errors_count2} {msg.errors_count3} {msg.errors_count4}")

                if t == "COMMAND_ACK":
                    self.log(f"CMD_ACK: {msg.command} → {msg.result}")

                if t == "RC_CHANNELS":
                    ch5 = msg.chan5_raw
                    ch7 = msg.chan7_raw
                    self.log(f"RC: CH5={ch5} CH7={ch7}")

                if t == "GLOBAL_POSITION_INT":
                    alt = msg.relative_alt / 1000
                    hdg = msg.hdg / 100
                    self.depthSignal.emit(alt)
                    self.headingSignal.emit(hdg)
                    self.log(f"POS: ALT={alt:.2f} HDG={hdg:.1f}")

            except Exception as e:
                self.log(f"EXCEPTION: {e}")

    # =====================================================
    # STOP
    # =====================================================
    def stop(self):
        self.running = False
        try:
            self.logfile.close()
        except:
            pass
