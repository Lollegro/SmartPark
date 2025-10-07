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
station.connect(ssid,password)

while station.isconnected() == False:
    pass

#definizione topic a cui l'ESP effettua la sottoscrizione
MQTT_TOPIC_VELOCITA_SBARRA = b'IotUnisa/Gruppo02/Velocità_sbarra'
MQTT_TOPIC_SBARRA = b'IotUnisa/Gruppo02/Gestione_sbarra'
MQTT_TOPIC_SOGLIA_DISTANZA = b'IotUnisa/Gruppo02/Imposta_soglia_distanza'
MQTT_TOPIC_SOGLIA_TEMPERATURA = b'IotUnisa/Gruppo02/Imposta_soglia_temperatura'
MQTT_TOPIC_LUNGHEZZA_CODICE = b'IotUnisa/Gruppo02/Settaggio_lunghezza_codice'
MQTT_TOPIC_RESET = b'IotUnisa/Gruppo02/Reset'
MQTT_TOPIC_ALLARME = b'IotUnisa/Gruppo02/Gestione_allarme'
MQTT_TOPIC_INTERVALLO_COUNTER_ENTRATE = b'IotUnisa/Gruppo02/Intervallo_counter_entrate'

#definizione topic su cui l'ESP effettua delle pubblicazioni
MQTT_TOPIC_SEMAFORO = b'IotUnisa/Gruppo02/Semaforo'
MQTT_TOPIC_ERRORE = b'IotUnisa/Gruppo02/Errore'
MQTT_TOPIC_STATO_GARAGE = b'IotUnisa/Gruppo02/Stato_garage'
MQTT_TOPIC_MISURAZIONI = b'IotUnisa/Gruppo02/Misurazioni'
MQTT_TOPIC_CONTEGGIO_ENTRATE = b'IotUnisa/Gruppo02/Monitoraggio_entrate'
MQTT_TOPIC_INIZIALIZZAZIONE = b'IotUnisa/Gruppo02/Inizializzazione'
MQTT_TOPIC_STORICO_EMERGENZE = b'IotUnisa/Gruppo02/Storico_emergenze'
MQTT_TOPIC_RESET_ESP = b'IotUnisa/Gruppo02/Reset_esp'
