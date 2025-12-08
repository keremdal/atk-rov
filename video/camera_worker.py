import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal


class CameraWorker(QThread):
    frameSignal = pyqtSignal(np.ndarray)
    statusSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        Gst.init(None)

        # ==============================
        # LOW LATENCY BLUEOS PIPELINE
        # ==============================
        pipeline_str = (
            "udpsrc port=5600 caps=application/x-rtp,encoding-name=H264,payload=96 ! "
            "rtph264depay ! avdec_h264 ! videoconvert ! "
            "video/x-raw,format=RGB ! appsink name=sink emit-signals=True sync=false max-buffers=1 drop=true"
        )

        self.pipeline = Gst.parse_launch(pipeline_str)
        self.appsink = self.pipeline.get_by_name("sink")

        self.appsink.connect("new-sample", self.on_new_sample)

        self.loop = GLib.MainLoop()
        self.running = True

    # ============================================================
    def run(self):
        try:
            self.pipeline.set_state(Gst.State.PLAYING)
            self.statusSignal.emit("✓ Kamera başladı")
            self.loop.run()
        except Exception as e:
            self.statusSignal.emit(f"❌ Kamera Hatası: {e}")

    # ============================================================
    def stop(self):
        self.running = False
        try:
            self.pipeline.set_state(Gst.State.NULL)
        except:
            pass
        try:
            self.loop.quit()
        except:
            pass

    # ============================================================
    def on_new_sample(self, sink):
        sample = sink.emit("pull-sample")
        if sample is None:
            return Gst.FlowReturn.OK

        buf = sample.get_buffer()
        caps = sample.get_caps()
        structure = caps.get_structure(0)

        width = structure.get_value("width")
        height = structure.get_value("height")

        ok, mapinfo = buf.map(Gst.MapFlags.READ)
        if not ok:
            return Gst.FlowReturn.OK

        data = mapinfo.data

        arr = np.frombuffer(data, np.uint8)

        # =====================================
        # FORMAT TESPİT
        # =====================================

        expected_rgb = width * height * 3

        if arr.size == expected_rgb:
            # RGB
            frame = arr.reshape((height, width, 3))
        else:
            # YUYV fallback
            try:
                yuyv = arr.reshape((height, width, 2))
                frame = cv2.cvtColor(yuyv, cv2.COLOR_YUV2RGB_YUYV)
            except Exception as e:
                print("⚠️ Bilinmeyen format, atlanıyor:", arr.size)
                buf.unmap(mapinfo)
                return Gst.FlowReturn.OK

        buf.unmap(mapinfo)

        # =====================================
        # FRAME EMIT
        # =====================================
        try:
            self.frameSignal.emit(frame)
        except:
            pass

        return Gst.FlowReturn.OK
