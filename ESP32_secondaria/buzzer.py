from machine import Pin,PWM

class Buzzer:
    
    def __init__(self, buzzer_pin):
        self.pwm = PWM(Pin(buzzer_pin, Pin.OUT))
        self.pwm.freq(2000)
        self.pwm.duty(0)
        
    def play(self, duty):
        self.pwm.duty(duty)
