from inputs import get_gamepad, UnpluggedError
from PyQt5.QtCore import QThread, pyqtSignal
import time

class GamepadReader(QThread):
    stickSignal = pyqtSignal(int, int, int, int)
    buttonSignal = pyqtSignal(str)

    def run(self):
        lx = ly = rx = ry = 32767

        while True:
            try:
                events = get_gamepad()
                for event in events:

                    # STICKLER
                    if event.code == "ABS_X":
                        lx = event.state
                    elif event.code == "ABS_Y":
                        ly = event.state
                    elif event.code == "ABS_RX":
                        rx = event.state
                    elif event.code == "ABS_RY":
                        ry = event.state

                    self.stickSignal.emit(lx, ly, rx, ry)

            except UnpluggedError:
                # Joystick yok → UYGULAMA ÇÖKMESİN
                time.sleep(1)
