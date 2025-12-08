import pygame
import time
from PyQt5.QtCore import QThread, pyqtSignal


class JoystickWorker(QThread):
    joystickStatus = pyqtSignal(str, bool)
    axesChanged = pyqtSignal(list)
    buttonsChanged = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.joy = None
        self.running = True

    def run(self):

        pygame.init()
        pygame.joystick.init()

        time.sleep(1)

        count = pygame.joystick.get_count()
        if count == 0:
            self.joystickStatus.emit("Joystick bulunamadı", False)
            return

        try:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()
            self.joystickStatus.emit(f"Bağlandı: {self.joy.get_name()}", True)
        except Exception as e:
            self.joystickStatus.emit(f"Joystick açılamadı: {e}", False)
            return

        # okuma döngüsü
        while self.running:
            pygame.event.pump()

            try:
                axes = [self.joy.get_axis(i) for i in range(self.joy.get_numaxes())]
                buttons = [self.joy.get_button(i) for i in range(self.joy.get_numbuttons())]

                self.axesChanged.emit(axes)
                self.buttonsChanged.emit(buttons)

            except Exception as e:
                self.joystickStatus.emit(f"HATA: {e}", False)
                break

            time.sleep(0.02)

    def stop(self):
        self.running = False
        pygame.quit()
