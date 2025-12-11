from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from mavlink.mavlink_reader import MavlinkReader

import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # MAVLINK
    rov = MavlinkReader()

    # UI
    win = MainWindow(rov)
    win.show()

    # MAVLINK START
    rov.start()

    sys.exit(app.exec_())
