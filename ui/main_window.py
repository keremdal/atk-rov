# ui/main_window.py

import time
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QStackedWidget, QLabel
)
from PyQt5.QtCore import QTimer

from ui.dashboard_page import DashboardPage
from ui.camera_page import CameraPage
        # Telemetri, motor, parametre, pid, log, sistem
from ui.telemetry_page import TelemetryPage
from ui.motors_page import MotorsPage
from ui.params_page import ParamsPage
from ui.pid_page import PIDPage
from ui.motor_test_page import MotorTestPage
from ui.log_page import LogPage
from ui.system_page import SystemPage

from mavlink.mavlink_reader import MavlinkReader
from mavlink.param_manager import ParamManager
from video.camera_worker import CameraWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Pencere
        self.setWindowTitle("ATK ROV STATION")
        self.setGeometry(100, 50, 1680, 920)
        self.setStyleSheet("background-color:#05070B; color:#EAEAEA; font-family:'Segoe UI';")

        # MAV & Param
        self.shared_mav = None
        self.param_manager = None

        # Alt bar label’ları
        self.labelTime = QLabel("--:--:--")
        self.labelPing = QLabel("Ping: -- ms")
        self.labelFPS = QLabel("FPS: --")
        self.labelMav = QLabel("MAVLink: ✖")
        self.labelMode = QLabel("Mod: --")
        self.labelBatt = QLabel("Batarya: -- V %--")

        # Üst durum
        self.labelTopStatus = QLabel("ROV: ✖   MAVLink: Bekleniyor   Kamera: ?   Uyarılar: 0")

        # UI
        self._build_ui()
        self._build_footer()
        self._start_workers()
        self._start_clock()

    # ============================================================
    # UI
    # ============================================================
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        mainLayout = QVBoxLayout()
        central.setLayout(mainLayout)

        # ---------- ÜST BAR ----------
        topBar = QHBoxLayout()
        titleLabel = QLabel("⚡  ATK   ATK ROV STATION")
        titleLabel.setStyleSheet("font-size:22px; font-weight:bold; color:#FFD000;")
        topBar.addWidget(titleLabel)
        topBar.addStretch()

        self.labelTopStatus.setStyleSheet("font-size:13px; color:#E5E7EB;")
        topBar.addWidget(self.labelTopStatus)
        mainLayout.addLayout(topBar)

        # ---------- ORTA KISIM ----------
        contentLayout = QHBoxLayout()
        mainLayout.addLayout(contentLayout)

        # Sol menü
        self.menu = QListWidget()
        self.menu.addItems([
            "Gösterge Paneli",
            "Kamera",
            "Telemetri",
            "Motorlar",
            "Parametreler",
            "PID Ayarlari",
            "Motor Test",
            "Kayit / Log",
            "Sistem"
        ])
        self.menu.setFixedWidth(210)
        self.menu.setStyleSheet("""
            QListWidget {
                background-color:#060910;
                border:1px solid #141A22;
                font-size:14px;
                color:#CBD2E1;
            }
            QListWidget::item {
                padding:8px 10px;
            }
            QListWidget::item:selected {
                background-color:#FFD000;
                color:#000000;
                border-left:3px solid #FFFFFF;
                margin-left:-3px;
            }
            QListWidget::item:hover {
                background-color:#141B29;
            }
        """)
        self.menu.currentRowChanged.connect(self.pages_setIndex)

        # Sayfalar
        self.pages = QStackedWidget()

        self.dashboard = DashboardPage()
        self.cameraPage = CameraPage()
        self.telemetryPage = TelemetryPage()
        self.motorsPage = MotorsPage()
        self.paramsPage = ParamsPage()
        self.pidPage = PIDPage()
        self.motorTestPage = MotorTestPage()
        self.logPage = LogPage()
        self.systemPage = SystemPage()

        self.pages.addWidget(self.dashboard)      # 0
        self.pages.addWidget(self.cameraPage)     # 1
        self.pages.addWidget(self.telemetryPage)  # 2
        self.pages.addWidget(self.motorsPage)     # 3
        self.pages.addWidget(self.paramsPage)     # 4
        self.pages.addWidget(self.pidPage)        # 5
        self.pages.addWidget(self.motorTestPage)  # 6
        self.pages.addWidget(self.logPage)        # 7
        self.pages.addWidget(self.systemPage)     # 8

        contentLayout.addWidget(self.menu)
        contentLayout.addWidget(self.pages)

        # Default sayfa
        self.menu.setCurrentRow(0)

    # ============================================================
    # ALT BAR
    # ============================================================
    def _build_footer(self):
        footerLayout = QHBoxLayout()

        def style_lbl(lbl):
            lbl.setStyleSheet(
                "background-color:#0D131A; padding:4px 10px;"
                "border-top:1px solid #202632; font-size:12px;"
            )

        # label’ları stillendir
        for lbl in [self.labelTime, self.labelPing, self.labelFPS,
                    self.labelMav, self.labelMode, self.labelBatt]:
            style_lbl(lbl)

        def make_sep():
            s = QLabel("|")
            s.setStyleSheet(
                "background-color:#0D131A; padding:4px 4px;"
                "border-top:1px solid #202632; color:#4B5563;"
            )
            return s

        footerLayout.addWidget(self.labelTime)
        footerLayout.addWidget(make_sep())
        footerLayout.addWidget(self.labelPing)
        footerLayout.addWidget(make_sep())
        footerLayout.addWidget(self.labelFPS)
        footerLayout.addWidget(make_sep())
        footerLayout.addWidget(self.labelMav)
        footerLayout.addWidget(make_sep())
        footerLayout.addWidget(self.labelMode)
        footerLayout.addWidget(make_sep())
        footerLayout.addWidget(self.labelBatt)
        footerLayout.addStretch()

        footerWidget = QWidget()
        footerWidget.setLayout(footerLayout)
        footerWidget.setFixedHeight(30)
        self.centralWidget().layout().addWidget(footerWidget)

    # ============================================================
    # SAAT
    # ============================================================
    def _start_clock(self):
        self._update_time()
        t = QTimer(self)
        t.timeout.connect(self._update_time)
        t.start(1000)
        self.clock = t

    def _update_time(self):
        self.labelTime.setText(time.strftime("%H:%M:%S"))

    # ============================================================
    # SAYFA DEĞİŞİMİ
    # ============================================================
    def pages_setIndex(self, index):
        self.pages.setCurrentIndex(index)

    # ============================================================
    # WORKER BAŞLATMA
    # ============================================================
    def _start_workers(self):
        # -------- MAVLINK (UDP AUTO-SCAN) --------
        self.mav_worker = MavlinkReader()

        # Bağlantı durumu + MAV nesnesi
        if hasattr(self.mav_worker, "connectionStatus"):
            self.mav_worker.connectionStatus.connect(self._on_mavlink_status)
        if hasattr(self.mav_worker, "mavReady"):
            self.mav_worker.mavReady.connect(self._on_mav_ready)

        # Telemetri sinyalleri
        self.mav_worker.depthSignal.connect(self.dashboard.update_depth)
        self.mav_worker.headingSignal.connect(self.dashboard.update_heading)
        self.mav_worker.batterySignal.connect(self.dashboard.update_battery)
        self.mav_worker.motorSignal.connect(self.dashboard.update_motors)

        # Alt bar için opsiyonel sinyaller (varsa bağla, yoksa hata verme)
        if hasattr(self.mav_worker, "pingSignal"):
            self.mav_worker.pingSignal.connect(
                lambda p: self.labelPing.setText(f"Ping: {p:.0f} ms")
            )
        if hasattr(self.mav_worker, "fpsSignal"):
            self.mav_worker.fpsSignal.connect(
                lambda f: self.labelFPS.setText(f"FPS: {f}")
            )
        if hasattr(self.mav_worker, "modeSignal"):
            self.mav_worker.modeSignal.connect(
                lambda m: self.labelMode.setText(f"Mod: {m}")
            )
        if hasattr(self.mav_worker, "batteryStatusSignal"):
            self.mav_worker.batteryStatusSignal.connect(
                lambda v, pr: self.labelBatt.setText(f"Batarya: {v:.2f} V %{pr}")
            )

        self.mav_worker.start()

        # -------- KAMERA --------
        self.cam_worker = CameraWorker()
        self.cam_worker.frameSignal.connect(self.dashboard.update_camera_frame)
        self.cam_worker.frameSignal.connect(self.cameraPage.update_camera_frame)
        if hasattr(self.cam_worker, "statusSignal"):
            self.cam_worker.statusSignal.connect(self._on_camera_status)
        self.cam_worker.start()

        if hasattr(self.cameraPage, "set_cam_worker"):
            self.cameraPage.set_cam_worker(self.cam_worker)

        # -------- PARAM --------
        if hasattr(self.paramsPage, "btnFetch"):
            self.paramsPage.btnFetch.clicked.connect(self.start_param_download)

    # ============================================================
    # MAVLINK CALLBACK'LERİ
    # ============================================================
    def _on_mavlink_status(self, ok: bool):
        if ok:
            self.labelMav.setText("MAVLink: ✓ UDP OK")
            # Kamera durumunu koruyarak yazalım
            self._update_top_status(mav_text="MAVLink: UDP OK")
        else:
            self.labelMav.setText("MAVLink: ✖ UDP YOK")
            self._update_top_status(mav_text="MAVLink: UDP YOK")

    def _on_mav_ready(self, mav):
        print("✓ MAV Nesnesi geldi (UDP) ✓")
        self.shared_mav = mav

    # ============================================================
    # KAMERA CALLBACK
    # ============================================================
    def _on_camera_status(self, text: str, ok: bool):
        # CameraPage içinde bir set_status varsa onu da kullan
        if hasattr(self.cameraPage, "set_status"):
            self.cameraPage.set_status(text, ok)

        cam_txt = "Kamera: ✓" if ok else "Kamera: ✖"
        self._update_top_status(cam_text=cam_txt)

    def _update_top_status(self, mav_text=None, cam_text=None):
        """
        Üst bar string’ini tek noktadan güncelleyelim.
        ROV statusünü şimdilik MAVLink’e göre basit tutuyoruz.
        """
        mav_part = mav_text or ("MAVLink: UDP OK" if "✓" in self.labelMav.text() else "MAVLink: UDP YOK")
        cam_part = cam_text or ("Kamera: ✓" if "✓" in getattr(self, "labelTopStatus").text() else "Kamera: ?")

        # ROV bağlı mı? basitçe MAVLink OK ise bağlı kabul edelim
        if "UDP OK" in mav_part:
            rov_part = "ROV: Bağlı"
        else:
            rov_part = "ROV: ✖"

        self.labelTopStatus.setText(f"{rov_part}   {mav_part}   {cam_part}   Uyarılar: 0")

    # ============================================================
    # PARAMETRE ÇEKME
    # ============================================================
    def start_param_download(self):
        if not self.shared_mav:
            self.paramsPage.set_status("❗ MAVLink UDP bağlı değil!")
            return

        # Aynı anda iki thread açma
        if self.param_manager is not None and self.param_manager.isRunning():
            self.paramsPage.set_status("Parametreler zaten çekiliyor…")
            return

        self.param_manager = ParamManager()
        self.param_manager.set_mav(self.shared_mav)
        self.paramsPage.set_manager(self.param_manager)

        self.param_manager.statusSignal.connect(self.paramsPage.set_status)
        self.param_manager.progressSignal.connect(self.paramsPage.update_progress)
        self.param_manager.listReady.connect(self.paramsPage.show_param_list)

        self.param_manager.start()
