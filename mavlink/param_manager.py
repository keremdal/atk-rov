from pymavlink import mavutil
from PyQt5.QtCore import QThread, pyqtSignal
import time

class ParamManager(QThread):
    statusSignal = pyqtSignal(str)
    progressSignal = pyqtSignal(int, int)
    listReady = pyqtSignal(list)

    def set_mav(self, mav):
        self.master = mav

    def run(self):
        self.statusSignal.emit("Parametre çekimi başladı...")

        if not hasattr(self, "master") or self.master is None:
            self.statusSignal.emit("❗ MAV hatası — master yok")
            return

        self.master.param_fetch_all()
        time.sleep(1)

        params = {}
        total = 0
        received = 0

        # önce param sayısını öğren
        while True:
            msg = self.master.recv_match(type='PARAM_VALUE', blocking=False)
            if msg:
                total = msg.param_count
                break
            time.sleep(0.1)

        # şimdi parametreleri oku
        while received < total:
            msg = self.master.recv_match(type='PARAM_VALUE', blocking=True, timeout=2)
            
            if not msg:
                continue

            name = msg.param_id
            value = msg.param_value

            params[name] = value
            received += 1

            self.progressSignal.emit(received, total)

        self.statusSignal.emit("🟢 Parametreler alınmıştır!")
        self.listReady.emit(list(params.keys()))
