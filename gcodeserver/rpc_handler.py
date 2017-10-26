from pydispatch import dispatcher


class RpcHandler(object):

    def __init__(self):
        self.lift = True

    def on_connect(self, data):
        self.home()

    def on_disconnect(self, data):
        self.home()

    def home(self):
        self.pen_lift()
        dispatcher.send(signal='HOME', sender=self)

    def pen_drop(self):
        self.lift = 0
        dispatcher.send(signal='PEN_DROP', sender=self)

    def pen_lift(self):
        self.lift = 1
        dispatcher.send(signal='PEN_LIFT', sender=self)

    def up(self):
        dispatcher.send(signal='MOVE_RELATIVE', sender=self, x=0, y=-10, speed=18000.0)

    def down(self):
        dispatcher.send(signal='MOVE_RELATIVE', sender=self, x=0, y=10, speed=18000.0)

    def left(self):
        dispatcher.send(signal='MOVE_RELATIVE', sender=self, x=-10, y=0, speed=18000.0)

    def right(self):
        dispatcher.send(signal='MOVE_RELATIVE', sender=self, x=10, y=0, speed=18000.0)

    def gcode(self, gcode):
        dispatcher.send(signal='GCODE', sender=self, gcode=gcode)

    def center(self):
        dispatcher.send(signal='MOVE_TO_POINT', sender=self, x=2770/2, y=875/2, speed=18000.0)

    def draw(self, draw_data):
        x = (draw_data['x'] * 1166) + 802#2770
        y = draw_data['y'] * 875
        #dispatcher.send(signal='MOVE_TO_POINT', sender=self, x=x, y=y, speed=9600.0)
        dispatcher.send(signal='MOVE_TO_POINT', sender=self, x=x, y=y, speed=18000.0)

        new_lift = draw_data['lift'] == 1
        if new_lift != self.lift:
            self.lift = new_lift
            if self.lift:
                dispatcher.send(signal='PEN_LIFT', sender=self)
            else:
                dispatcher.send(signal='PEN_DROP', sender=self)
