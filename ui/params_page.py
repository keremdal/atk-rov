import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class ParamsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.manager = None
        self.params = {}

        self._build_ui()


    # ---------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        self.setLayout(layout)

        title = QLabel("⚙️ PARAMETRELER")
        title.setStyleSheet("font-size:18px; font-weight:bold; color:#FFD000;")
        layout.addWidget(title)

        # 🔍 ARAMA KUTUSU
        self.searchBox = QLineEdit()
        self.searchBox.setPlaceholderText("Ara: SYS_, PID_, RC_, …")
        self.searchBox.textChanged.connect(self.filter_params)
        layout.addWidget(self.searchBox)

        # 📌 KATEGORİ BUTONLARI
        catBar = QHBoxLayout()
        for cat in ["PID", "SYS", "RC", "EKF", "NAV", "ALL"]:
            btn = QPushButton(cat)
            btn.setStyleSheet("padding:4px; font-size:12px;")
            btn.clicked.connect(lambda _, c=cat: self.filter_category(c))
            catBar.addWidget(btn)

        layout.addLayout(catBar)

        # 📄 PARAMS LIST
        self.listWidget = QListWidget()
        self.listWidget.itemChanged.connect(self._on_param_changed)
        layout.addWidget(self.listWidget, 1)

        # STATUS
        self.statusLabel = QLabel("")
        self.statusLabel.setStyleSheet("font-size:12px; color:#AAAAAA;")
        layout.addWidget(self.statusLabel)


    # ---------------------------------------------------------
    def set_manager(self, m):
        self.manager = m


    # ---------------------------------------------------------
    def set_status(self, txt):
        self.statusLabel.setText(txt)


    # ---------------------------------------------------------
    def show_param_list(self, params: dict):
        """ Parametreleri listeye yükle """

        self.params = params
        self.listWidget.clear()

        for name, value in params.items():
            item = QListWidgetItem(f"{name} = {value}")
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.listWidget.addItem(item)

        self.set_status(f"🟢 {len(params)} parametre yüklendi.")


    # ---------------------------------------------------------
    def filter_params(self, text: str):
        """ Arama kutusuna göre filtre """

        text = text.lower()

        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            if text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)


    # ---------------------------------------------------------
    def filter_category(self, cat):
        """ Kategori butonlarına göre filtre """

        if cat == "ALL":
            for i in range(self.listWidget.count()):
                self.listWidget.item(i).setHidden(False)
            return

        cat = cat.lower()

        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            if item.text().lower().startswith(cat):
                item.setHidden(False)
            else:
                item.setHidden(True)


    # ---------------------------------------------------------
    def update_progress(self, p):
        self.set_status(f"🔄 Yükleniyor… {p}%")


    # ---------------------------------------------------------
    def _on_param_changed(self, item):
        """ Liste üzerinde değer değiştiğinde """

        txt = item.text()

        try:
            name, val = txt.split("=")
            name = name.strip()
            val = float(val.strip())
        except:
            item.setBackground(QColor(80, 0, 0))
            self.set_status("❗ Format yanlış")
            return

        # MAV’e yaz
        try:
            if self.manager:
                self.manager.set_param(name, val)

            # başarı → sarı renklendirme
            item.setBackground(QColor(60, 60, 20))
            item.setForeground(QColor("#FFD000"))

            self.set_status(f"📡 Gönderildi: {name} = {val}")

        except Exception as e:
            item.setBackground(QColor(80, 0, 0))
            item.setForeground(QColor("#FF0000"))
            self.set_status(f"❌ Yazma hatası: {name}")


