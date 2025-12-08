import pygame
from PyQt5.QtCore import QThread, pyqtSignal

class JoystickReader(QThread):
    axisSignal = pyqtSignal(float, float, float, float)   # X, Y, Z, Throttle
    buttonSignal = pyqtSignal(int, bool)

    def __init__(self):
        super().__init__()

        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            print("❌ Joystick yok")
            self.joy = None
        else:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()
            print("🎮 Joystick bağlı:", self.joy.get_name())

        self.running = True

    def run(self):
        while self.running:
            pygame.event.pump()

            if self.joy:
                x = self.joy.get_axis(0)   # sol / sağ
                y = self.joy.get_axis(1)   # ileri / geri
                z = self.joy.get_axis(2)   # yaw
                t = self.joy.get_axis(3)   # throttle

                self.axisSignal.emit(x, y, z, t)

                for b in range(self.joy.get_numbuttons()):
                    pressed = self.joy.get_button(b)
                    if pressed:
                        self.buttonSignal.emit(b, True)

    def stop(self):
        self.running = False
