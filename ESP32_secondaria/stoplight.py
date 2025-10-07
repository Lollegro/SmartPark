from led import Led

#classe contenente metodi per la gestione dei led che compongono il semaforo
class Stoplight:
    
    def __init__(self,red_led,yellow_led,green_led):
        self.stoplight = [red_led,yellow_led,green_led]
        
    def red_on(self):
        self.stoplight[1].turn_off()
        self.stoplight[2].turn_off()
        self.stoplight[0].turn_on()
        
    def yellow_on(self):
        self.stoplight[0].turn_off()
        self.stoplight[2].turn_off()
        self.stoplight[1].turn_on()
        
    def green_on(self):
        self.stoplight[0].turn_off()
        self.stoplight[1].turn_off()
        self.stoplight[2].turn_on()
        
    def turn_off(self):
        self.stoplight[0].turn_off()
        self.stoplight[1].turn_off()
        self.stoplight[2].turn_off()
        
    def turn_on(self):
        self.stoplight[0].turn_on()
        self.stoplight[1].turn_on()
        self.stoplight[2].turn_on()