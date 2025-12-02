from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QListWidget, QProgressBar

class ParamsPage(QWidget):
    def __init__(self):
        super().__init__()
        
        self.manager = None

        layout = QVBoxLayout()
        
        self.status = QLabel("Parametre durumu: Bekleniyor")
        layout.addWidget(self.status)

        self.btnFetch = QPushButton("PARAMETRELERİ ÇEK")
        layout.addWidget(self.btnFetch)

        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        layout.addWidget(self.progress)

        self.list = QListWidget()
        layout.addWidget(self.list)

        self.setLayout(layout)

    def set_manager(self, m):
        self.manager = m

    def set_status(self, msg):
        self.status.setText(msg)

    def update_progress(self, current, total):
        if total == 0:
            percent = 0
        else:
            percent = int((current / total) * 100)

        self.progress.setValue(percent)
        self.status.setText(f"{current} / {total} alındı (%{percent})")

    def show_param_list(self, params):
        self.list.clear()
        for p in params:
            self.list.addItem(p)
        self.status.setText(f"Toplam {len(params)} parametre alındı ✓")
