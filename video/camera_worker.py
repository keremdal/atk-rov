# camera_worker.py

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')

from gi.repository import Gst, GstApp, GLib
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtGui import QImage
import numpy as np


class CameraWorker(QThread):
    frameSignal = pyqtSignal(QImage)
    statusSignal = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()

        self.pipeline_str = (
            "rtspsrc location=rtsp://192.168.2.2:8554/video_stream__dev_video0 latency=0 protocols=udp ! "
            "rtpjitterbuffer latency=0 drop-on-latency=true ! "
            "rtph264depay ! "
            "h264parse ! "
            "avdec_h264 ! videoconvert ! "
            "video/x-raw,format=RGB ! "
            "appsink name=appsink emit-signals=true drop=true max-buffers=1"
        )

        Gst.init(None)
        self.running = True

    def run(self):
        try:
            self.pipeline = Gst.parse_launch(self.pipeline_str)
            self.appsink = self.pipeline.get_by_name("appsink")
            self.appsink.connect("new-sample", self.on_new_sample)

            self.pipeline.set_state(Gst.State.PLAYING)
            self.statusSignal.emit("Kamera AKTİF", True)

            self.loop = GLib.MainLoop()
            self.loop.run()

        except Exception as e:
            self.statusSignal.emit(f"Kamera HATASI: {e}", False)
            print("Camera error:", e)

    def stop(self):
        self.running = False
        if hasattr(self, "pipeline"):
            self.pipeline.set_state(Gst.State.NULL)
        if hasattr(self, "loop"):
            self.loop.quit()
        self.statusSignal.emit("Kamera DURDU", False)

    def on_new_sample(self, sink, data):
        if not self.running:
            return Gst.FlowReturn.OK

        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()

        arr = np.ndarray(
            (caps.get_structure(0).get_value("height"),
             caps.get_structure(0).get_value("width"), 3),
            buffer=buf.extract_dup(0, buf.get_size()),
            dtype=np.uint8
        )

        h, w, ch = arr.shape
        image = QImage(arr.data, w, h, w * ch, QImage.Format_RGB888)
        self.frameSignal.emit(image)

        return Gst.FlowReturn.OK
