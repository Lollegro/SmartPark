from machine import Pin,I2C
import ssd1306, framebuf

class Oled:
    
    def __init__(self,oled_width,oled_height,scl_pin,sda_pin):
        self.width = oled_width
        self.height = oled_height
        self.i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.oled = ssd1306.SSD1306_I2C(oled_width, oled_height, self.i2c)
        
    def fill(self):
        self.oled.fill(0)
    
    def print_text(self,text,x,y):
        self.oled.text(text,x,y)
        self.oled.show()
 