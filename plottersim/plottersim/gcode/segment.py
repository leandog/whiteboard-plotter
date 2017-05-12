class Segment:

    def __init__(self, type, coords, lineNb, line, servo_pwm):
        self.type = type
        self.coords = coords
        self.lineNb = lineNb
        self.line = line
        self.servo_pwm = servo_pwm

    def __str__(self):
        return "<Segment: type=%s, lineNb=%d, style=%s, layerIdx=%d, servo_pwm=%d>"%(self.type, self.lineNb, self.style, self.layerIdx, self.servo_pwm)
