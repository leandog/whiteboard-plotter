from pydispatch import dispatcher

from kivy.uix.widget import Widget
from kivy.graphics.vertex_instructions import Line,Rectangle
from kivy.graphics import Color
from kivy.clock import mainthread, Clock

from plottersim.gcode.plotter_model import PlotterModel
from plottersim.gcode.gcode_parser import GcodeParser

PLOTTER_WIDTH = 3000.0
PLOTTER_HEIGHT = 1000.0
PEN_DIAMETER = 2.0
SERVO_PWM_MIDPOINT = 1150

class PlotterCanvas(Widget):

    def __init__(self, *args, **kwargs):
        super(PlotterCanvas, self).__init__(*args, **kwargs)
        self.plotter_model = PlotterModel()
        self.gcode_parser = GcodeParser(self.plotter_model)

        dispatcher.connect(self.on_segment_added, signal='SEGMENT_ADDED', sender=dispatcher.Any)

        self._clear_canvas()
        Clock.schedule_once(self._initialize)
    
    @mainthread
    def on_segment_added(self, *args, **kwargs):
        previous_segment = kwargs['previous_segment']
        current_segment = kwargs['current_segment']
        if current_segment.servo_pwm > SERVO_PWM_MIDPOINT:
            return

        with self.canvas:
            coords = map(lambda x: self._relative_coords(x), [previous_segment, current_segment])
            flat_points = [item for sublist in coords for item in sublist]
            pen_width = PEN_DIAMETER * self._drawing_scale()
            Color(74.0/255.0, 1.0/255.0, 63.0/255.0)
            Line(points=flat_points, width=pen_width)

    def _initialize(self, *args, **kwargs):
        self.gcode_parser.start_reading_serial()

    def on_size(self, *args, **kwargs):
        self._redraw_model()

    def _clear_canvas(self):
        with self.canvas:
            self.canvas.clear()
            Color(246.0/255.0, 251.0/255.0, 247.0/255.0, 1)
            print_width = 3000.0
            print_height = 1000.0
            print_ratio = print_width / print_height
            screen_ratio = self.width / self.height
            
            fit_width, fit_height = (print_width * self.height / print_height, self.height) if screen_ratio > print_ratio else (self.width, print_height * self.width / print_width)
            y = ((self.height/2)-(fit_height / 2))
            Rectangle(pos=(self.x, y), size=(fit_width, fit_height))

    def _redraw_model(self):
        self._clear_canvas()

        if not self.plotter_model:
            return

        with self.canvas:
            Color(74.0/255.0, 1.0/255.0, 63.0/255.0)
            coords = map(lambda x: self._relative_coords(x), self.plotter_model.segments)
            flat_points = [item for sublist in coords for item in sublist]
            pen_width = PEN_DIAMETER * self._drawing_scale()
            Line(points=flat_points, width=pen_width)

    def _relative_coords(self, segment): 
        coords = { 'X':0.0, 'Y':0.0 }
        if segment:
            coords = segment.coords

        (draw_x,draw_y,draw_width,draw_height) = self._drawing_bounds()

        x = coords['X']
        #invert y for kivy coords
        y = PLOTTER_HEIGHT - coords['Y']

        return ((x / PLOTTER_WIDTH) * draw_width, draw_y + ((y / PLOTTER_HEIGHT) * draw_height))

    def _drawing_bounds(self):
        print_ratio = PLOTTER_WIDTH / PLOTTER_HEIGHT
        screen_ratio = self.width / self.height
        fit_width, fit_height = (PLOTTER_WIDTH * self.height / PLOTTER_HEIGHT, self.height) if screen_ratio > print_ratio else (self.width, PLOTTER_HEIGHT * self.width / PLOTTER_WIDTH)
        y = ((self.height/2)-(fit_height / 2))
        return (self.x,y,fit_width,fit_height)

    def _drawing_scale(self):
        (x,y,width,height) = self._drawing_bounds()
        return width / PLOTTER_WIDTH
