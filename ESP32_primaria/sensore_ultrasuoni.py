from machine import Pin
import machine, time

class HCSR04:
    
    def __init__(self, trigger_pin, echo_pin):
        
        self.trigger = Pin(trigger_pin, mode=Pin.OUT)
        self.trigger.value(0)
        self.echo = Pin(echo_pin, mode=Pin.IN)

    def distance_cm(self):
        
        self.trigger.value(0) 
        time.sleep_us(2)
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)
        
        #Metodo per misurare la durata dell'impulso in microsecondi
        pulse_duration = machine.time_pulse_us(self.echo, 1)
        
        #Calcolo della distanza in centimetri utilizzando la velocità del suono (343 m/s)
        distanza = (pulse_duration * 0.0343)/2
        
        return distanza

