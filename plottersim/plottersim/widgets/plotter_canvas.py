from kivy.uix.widget import Widget
from kivy.graphics.vertex_instructions import Line
from kivy.graphics import Color

from plottersim.gcode.gcode_parser import GcodeParser


class PlotterCanvas(Widget):

    def __init__(self, *args, **kwargs):
        super(PlotterCanvas, self).__init__(*args, **kwargs)
        self.gcode_parser = GcodeParser()
        self.gcode_model = None

    def draw_gcode(self, file_path):
        self.gcode_model = self.gcode_parser.parse_file(file_path)
        self._redraw_model()

    def _redraw_model(self):
        if not self.gcode_model:
            return

        with self.canvas:
            self.canvas.clear()
            Color(1, 1, 1)
            for layer in self.gcode_model.layers:
                coords = map(lambda x: self._relative_coords(x.coords), layer.segments)
                flat_points = [item for sublist in coords for item in sublist]
                Line(points=flat_points, width=0.5)

    def _relative_coords(self, coords): 
        print_width = self.gcode_model.bbox.xmax
        print_height = self.gcode_model.bbox.ymax
        print_ratio = print_width / print_height
        screen_ratio = self.width / self.height
        
        fit_width, fit_height = (print_width * self.height / print_height, self.height) if screen_ratio > print_ratio else (self.width, print_height * self.width / print_width)

        x = coords['X']
        y = coords['Y']
        return ((x / print_width) * fit_width, (y / print_height) * fit_height)

    def on_size(self, *args, **kwargs):
        #super(PlotterCanvas, self).on_size(*args, **kwargs)
        self._redraw_model()
