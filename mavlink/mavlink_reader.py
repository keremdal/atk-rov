from pymavlink import mavutil
from PyQt5.QtCore import QThread, pyqtSignal

class MavlinkReader(QThread):
    depthSignal = pyqtSignal(float)
    headingSignal = pyqtSignal(float)
    batterySignal = pyqtSignal(float, float)
    motorSignal = pyqtSignal(list)
    connectionStatus = pyqtSignal(bool)
    mavReady = pyqtSignal(object)

    def run(self):
        print("MAVLINK: AUTO SCAN başlıyor...")

        # Olası bağlantılar:
        connections = [
            'udp:192.168.2.2:14550',
            'udp:0.0.0.0:14550',
            'udp:0.0.0.0:14552',
            'udp:192.168.2.2:14552',
            'udp:192.168.2.2:14000',
            'udp:192.168.2.2:14660',
        ]

        self.master = None

        # sırayla dene
        for c in connections:
            try:
                print(f"Deniyorum → {c}")
                m = mavutil.mavlink_connection(c, autoreconnect=True, timeout=3)
                
                msg = m.recv_match(type="HEARTBEAT", blocking=True, timeout=2)
                if msg:
                    print(f"✔ MAVLINK BAĞLANDI → {c}")
                    self.master = m
                    self.connectionStatus.emit(True)
                    self.mavReady.emit(self.master)
                    break
            except:
                pass

        if self.master is None:
            print("❗ MAVLINK BAĞLANAMADI ❗")
            self.connectionStatus.emit(False)
            return
