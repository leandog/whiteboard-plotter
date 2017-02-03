from kivy.uix.screenmanager import Screen
from kivy.clock import Clock


class PlotterScreen(Screen):

    def __init__(self, **kwargs):
        super(PlotterScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._initialize)

    def _initialize(self, dt):
        self.ids.plotter_canvas.draw_gcode('/Users/garyjohnson/Desktop/test.gcode')


