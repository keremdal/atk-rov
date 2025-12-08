import pygame
from PyQt5.QtCore import QThread, pyqtSignal

class JoystickWorker(QThread):
    axesSignal = pyqtSignal(list)
    buttonsSignal = pyqtSignal(list)
    statusSignal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        pygame.init()

        try:
            pygame.joystick.init()
            self.js = pygame.joystick.Joystick(0)
            self.js.init()
            self.statusSignal.emit(True)
            print("🎮 Joystick bağlandı:", self.js.get_name())
        except:
            self.js = None
            self.statusSignal.emit(False)
            print("❌ Joystick yok")

        self.running = True

    def run(self):
        while self.running:
            if self.js:
                pygame.event.pump()

                axes = [self.js.get_axis(i) for i in range(self.js.get_numaxes())]
                buttons = [self.js.get_button(i) for i in range(self.js.get_numbuttons())]

                self.axesSignal.emit(axes)
                self.buttonsSignal.emit(buttons)

            self.msleep(20)

    def stop(self):
        self.running = False
