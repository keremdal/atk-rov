import sys
from PyQt5.QtWidgets import QApplication

from mavlink.mavlink_reader import MavlinkReader
from ui.main_window import MainWindow

if __name__ == "__main__":

    app = QApplication(sys.argv)

    # MAVLINK THREAD OLUŞTUR
    rov = MavlinkReader()

    # WINDOW’A VER
    win = MainWindow(rov)
    win.show()

    sys.exit(app.exec_())
