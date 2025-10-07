import dht

class SensorDHT:
    
    def __init__(self,dht_pin):
        self.sensor = dht.DHT22(dht_pin)
        
    def read_measure(self):
        self.sensor.measure()
        
    def read_temperature(self):
        return self.sensor.temperature()
    
    def read_humidity(self):
        return self.sensor.humidity()