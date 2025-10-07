from machine import Pin

class Led:
    
    def __init__(self,led_pin):
        self.led = Pin(led_pin, Pin.OUT)
        
    def turn_on(self):
        self.led.on()
        
    def turn_off(self):
        self.led.off()