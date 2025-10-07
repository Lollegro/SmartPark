from machine import Pin
import utime

class StepMotor:
    
    def __init__(self,motor_pin,step_sequence):
        
        self.stepper_pins = [Pin(pin,Pin.OUT) for pin in motor_pin]
        self.step_sequence = step_sequence
        self.step_index = 0
    
    #funzione per il movimento del motore in senso orario
    def raising(self,delay):
        
        direction = -1
        for i in range(512):
            self.step_index = (self.step_index + direction) % len(self.step_sequence)
            for pin_index in range(len(self.stepper_pins)):
                self.stepper_pins[pin_index].value(self.step_sequence[self.step_index][pin_index])
            utime.sleep(delay)
    
    #funzione per il movimento del motore in senso antiorario
    def falling(self,delay):
        
        direction = 1
        for i in range(512):
            self.step_index = (self.step_index + direction) % len(self.step_sequence)
            for pin_index in range(len(self.stepper_pins)):
                self.stepper_pins[pin_index].value(self.step_sequence[self.step_index][pin_index])
            utime.sleep(delay) 
