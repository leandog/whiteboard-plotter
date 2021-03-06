import serial
from random import random
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.widget import Widget
from kivy.clock import mainthread, Clock
from pydispatch import dispatcher


PLOTTER_WIDTH=3000
PLOTTER_HEIGHT=1000

class PainterWidget(Widget):

    def __init__(self, **kwargs):
        super(PainterWidget, self).__init__(**kwargs)
        Clock.schedule_once(self._initialize)

    def _initialize(self, *args, **kwargs):
        self._clear_canvas()

    def _clear_canvas(self):
        with self.canvas:
            self.canvas.clear()
            Color(246.0/255.0, 251.0/255.0, 247.0/255.0, 1)
            print_ratio = PLOTTER_WIDTH / PLOTTER_HEIGHT
            screen_ratio = self.width / self.height
            
            fit_width, fit_height = (PLOTTER_WIDTH * self.height / PLOTTER_HEIGHT, self.height) if screen_ratio > print_ratio else (self.width, PLOTTER_HEIGHT * self.width / PLOTTER_WIDTH)
            y = ((self.height/2)-(fit_height / 2))
            Rectangle(pos=(self.x, y), size=(fit_width, fit_height))

    def on_touch_up(self, touch):
        x,y = self._relative_coords((touch.x, touch.y))
        dispatcher.send(signal='MOVE_TO_POINT', sender=self, x=x, y=y)
        dispatcher.send(signal='PEN_LIFT', sender=self)

    def on_touch_down(self, touch):
        color = (random(), random(), random())
        with self.canvas:
            Color(74.0/255.0, 1.0/255.0, 63.0/255.0)
            touch.ud['line'] = Line(points=(touch.x, touch.y))

        x,y = self._relative_coords((touch.x, touch.y))

        dispatcher.send(signal='MOVE_TO_POINT', sender=self, x=x, y=y)
        dispatcher.send(signal='PEN_DROP', sender=self)

    def on_touch_move(self, touch):
        touch.ud['line'].points += [touch.x, touch.y]
        x,y = self._relative_coords((touch.x, touch.y))

        dispatcher.send(signal='MOVE_TO_POINT', sender=self, x=x, y=y)

    def _drawing_bounds(self):
        print_ratio = PLOTTER_WIDTH / PLOTTER_HEIGHT
        screen_ratio = self.width / self.height
        fit_width, fit_height = (PLOTTER_WIDTH * self.height / PLOTTER_HEIGHT, self.height) if screen_ratio > print_ratio else (self.width, PLOTTER_HEIGHT * self.width / PLOTTER_WIDTH)
        y = ((self.height/2)-(fit_height / 2))
        return (self.x,y,fit_width,fit_height)

    def _relative_coords(self, segment): 
        coords = { 'X':0.0, 'Y':0.0 }
        if segment:
            coords = { 'X':segment[0], 'Y':segment[1] }

        (draw_x,draw_y,draw_width,draw_height) = self._drawing_bounds()

        x = coords['X']
        #invert y for kivy coords
        y = PLOTTER_HEIGHT - coords['Y']

        return ((x / draw_width) * PLOTTER_WIDTH, ((y / draw_height) * PLOTTER_HEIGHT)-draw_y)

    def on_size(self, *args, **kwargs):
        self._clear_canvas()
