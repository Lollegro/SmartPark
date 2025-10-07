from machine import Pin
import time

class Keypad:
    
    def __init__(self,rows_pin,cols_pin,keys):
        self.rows = [Pin(pin,Pin.OUT) for pin in rows_pin]
        for i in range(len(self.rows)):
            self.rows[i].on()
        self.cols = [Pin(pin,Pin.IN,Pin.PULL_UP) for pin in cols_pin]
        self.keys = keys
        
    #funzione per lettura input del tastierino
    def read_value(self):
        value = None
        for i,row in enumerate(self.rows):
            row.off()
            for j,col in enumerate(self.cols):
                if not col.value():
                    value = self.keys[i][j]
                    while not col.value():
                        time.sleep_ms(10)
            row.on()
            
        return value
