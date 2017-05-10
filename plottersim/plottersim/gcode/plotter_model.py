class PlotterModel:

    SERVO_PWM_MIDPOINT = 1150

    def __init__(self):
        self.relative = {
            "X": 0.0,
            "Y": 0.0,
            "F": 0.0,
        }

        self.offset = {
            "X": 0.0,
            "Y": 0.0,
        }

        self.is_relative = False
        self.segments = []
        self.servo_pwm = PlotterModel.SERVO_PWM_MIDPOINT
        
    def set_relative(self, is_relative):
        self.is_relative = is_relative
        
    def add_segment(self, segment):
        self.segments.append(segment)
