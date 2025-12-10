import threading
import time
import pygame

from PyQt5.QtCore import QObject, pyqtSignal


class JoystickWorker(QObject, threading.Thread):
    axesSignal = pyqtSignal(list)
    buttonsSignal = pyqtSignal(list)
    hatSignal = pyqtSignal(tuple)  # D-PAD

    def __init__(self):
        QObject.__init__(self)
        threading.Thread.__init__(self)
        self.running = True

    def run(self):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            print("❌ Joystick bulunamadı")
            return

        joy = pygame.joystick.Joystick(0)
        joy.init()
        print(f"🎮 Joystick aktif: {joy.get_name()}")

        while self.running:
            pygame.event.pump()

            axes = [joy.get_axis(i) for i in range(joy.get_numaxes())]
            buttons = [joy.get_button(i) for i in range(joy.get_numbuttons())]

            self.axesSignal.emit(axes)
            self.buttonsSignal.emit(buttons)

            if joy.get_numhats() > 0:
                hat = joy.get_hat(0)
                self.hatSignal.emit(hat)

            time.sleep(0.01)

        pygame.quit()

    def stop(self):
        self.running = False
