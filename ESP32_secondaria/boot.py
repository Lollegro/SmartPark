from umqtt.simple import MQTTClient
import network, time, esp, gc, ubinascii, machine, micropython

#impostazione debug a None e attivazione gargabe collector
esp.osdebug(None) 
gc.collect()

#variabili credenziali connessione
ssid = 'Angelo Infante'
password = 'cwwh3158'
mqtt_server = 'test.mosquitto.org'
mqtt_user = ''
mqtt_pass = ''

#recupero id dell'ESP per creazione cliente MQTT
client_id = ubinascii.hexlify(machine.unique_id())

#procedure per la connessione
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

#definizione topic a cui l'ESP effettua la sottoscrizione
TOPIC_SEMAFORO = b'IotUnisa/Gruppo02/Semaforo'
TOPIC_RESET = b'IotUnisa/Gruppo02/Reset_esp'


