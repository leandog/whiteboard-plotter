from pydispatch import dispatcher

from kivy.uix.widget import Widget
from kivy.graphics.vertex_instructions import Line,Rectangle
from kivy.graphics import Color
from kivy.clock import mainthread

from plottersim.gcode.plotter_model import PlotterModel
from plottersim.gcode.gcode_parser import GcodeParser


class PlotterCanvas(Widget):

    def __init__(self, *args, **kwargs):
        super(PlotterCanvas, self).__init__(*args, **kwargs)
        self.plotter_model = PlotterModel()
        self.gcode_parser = GcodeParser(self.plotter_model)

        dispatcher.connect(self.on_segment_added, signal='SEGMENT_ADDED', sender=dispatcher.Any)

        self._clear_canvas()
    
    @mainthread
    def on_segment_added(self, *args, **kwargs):
        previous_segment = kwargs['previous_segment']
        current_segment = kwargs['current_segment']
        with self.canvas:
            Color(74.0/255.0, 1.0/255.0, 63.0/255.0)
            coords = map(lambda x: self._relative_coords(x), [previous_segment, current_segment])
            flat_points = [item for sublist in coords for item in sublist]
            Line(points=flat_points, width=0.5)

    def draw_gcode(self, file_path):
        #self.gcode_parser.parse_file_async(file_path)
        self.gcode_parser.start_reading_serial()
        #self._redraw_model()

    def _clear_canvas(self):
        with self.canvas:
            self.canvas.clear()
            Color(246.0/255.0, 251.0/255.0, 247.0/255.0, 1)
            Rectangle(pos=(self.x,self.y), size=(self.width, self.height))


    def _redraw_model(self):
        self._clear_canvas()

        if not self.plotter_model:
            return

        with self.canvas:
            Color(74.0/255.0, 1.0/255.0, 63.0/255.0)
            layers = self.plotter_model.layers if self.plotter_model.layers else []
            for layer in layers:
                coords = map(lambda x: self._relative_coords(x), layer.segments)
                flat_points = [item for sublist in coords for item in sublist]
                Line(points=flat_points, width=1.0)

    def _relative_coords(self, segment): 
        coords = { 'X':0.0, 'Y':0.0 }
        if segment:
            coords = segment.coords

        print_width = 200.0 #self.plotter_model.bbox.xmax
        print_height = 200.0 #self.plotter_model.bbox.ymax
        print_ratio = print_width / print_height
        screen_ratio = self.width / self.height
        
        fit_width, fit_height = (print_width * self.height / print_height, self.height) if screen_ratio > print_ratio else (self.width, print_height * self.width / print_width)

        x = coords['X']
        y = coords['Y']
        return ((x / print_width) * fit_width, (y / print_height) * fit_height)

    def on_size(self, *args, **kwargs):
        self._redraw_model()
