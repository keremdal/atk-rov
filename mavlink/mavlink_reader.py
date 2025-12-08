from pymavlink import mavutil
from PyQt5.QtCore import QThread, pyqtSignal

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

    def run(self):
        print("MAVLINK: AUTO SCAN başlıyor...")

        # Deneceğimiz bağlantılar
        connections = [
    'udp:0.0.0.0:14550',
    'udp:0.0.0.0:14552',
    'udp:0.0.0.0:14000',
]


        # Sırayla dene
        for c in connections:
            try:
                print(f"Deniyorum → {c}")
                m = mavutil.mavlink_connection(c, autoreconnect=True, timeout=3)

                # ANY MESSAGE (Heartbeat değil, herhangi bir mesaj)
                msg = m.recv_match(blocking=True, timeout=2)

                if msg:
                    print(f"✔ MAVLINK BAĞLANDI → {c}")
                    self.master = m
                    self.connectionStatus.emit(True)
                    self.mavReady.emit(self.master)
                    break

            except Exception as e:
                print("Hata:", e)
                continue

        if self.master is None:
            print("❗ MAVLINK BAĞLANAMADI ❗")
            self.connectionStatus.emit(False)
            return

        # Sürekli veri dinleme
        while self.running:
            try:
                msg = self.master.recv_match(blocking=True, timeout=1)
                if not msg:
                    continue

                msg_type = msg.get_type()

                # Depth
                if msg_type == "GLOBAL_POSITION_INT":
                    depth = msg.relative_alt / 1000.0
                    self.depthSignal.emit(depth)

                # Heading
                if msg_type == "VFR_HUD":
                    heading = msg.heading
                    self.headingSignal.emit(heading)

                # Battery
                if msg_type == "SYS_STATUS":
                    voltage = msg.voltage_battery / 1000.0
                    current = msg.current_battery / 100.0
                    self.batterySignal.emit(voltage, current)

            except:
                pass

    def stop(self):
        self.running = False
