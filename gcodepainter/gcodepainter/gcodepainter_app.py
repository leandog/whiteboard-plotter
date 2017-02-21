from kivy.app import App

from gcodepainter.screens.painter_screen import PainterScreen
from gcodepainter.services.gcode_sender import GcodeSender


class GcodepainterApp(App):

    def on_start(self):
        self.gcode_sender = GcodeSender()
        self.gcode_sender.start()

    def on_stop(self):
        self.gcode_sender.stop()

