import time
import pygame

from PyQt5.QtCore import QThread, pyqtSignal


class JoystickWorker(QThread):
    # MainWindow buraya bağlanıyor:
    # self.joy.axesSignal.connect(self._on_joy_axes)
    # self.joy.buttonsSignal.connect(self._on_joy_buttons)
    axesSignal = pyqtSignal(list)
    buttonsSignal = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.joy = None

    def run(self):
        # Pygame başlat
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            print("❌ Joystick bulunamadı")
            return

        self.joy = pygame.joystick.Joystick(0)
        self.joy.init()
        print(f"🎮 Joystick aktif: {self.joy.get_name()}")

        # Sürekli okuma döngüsü
        while self.running:
            # event pump zorunlu
            pygame.event.pump()

            # axis değerleri
            axes = [round(self.joy.get_axis(i), 3) for i in range(self.joy.get_numaxes())]
            # butonlar
            buttons = [self.joy.get_button(i) for i in range(self.joy.get_numbuttons())]

            # PyQt sinyalleri
            self.axesSignal.emit(axes)
            self.buttonsSignal.emit(buttons)

            time.sleep(0.01)  # 100 Hz civarı

        # thread kapanırken
        pygame.quit()

    def stop(self):
        # dışarıdan çağırılacak
        self.running = False
        # thread’in düzgün bitmesini bekle
        self.wait(2000)
