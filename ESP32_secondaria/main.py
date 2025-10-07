from machine import Pin
from display_oled import Oled
from stoplight import Stoplight
from stoplight_status import StoplightStatus
from led import Led
from buzzer import Buzzer

#funzione callback per la gestione dei messaggi ricevuti dal broker
def sub_func(topic, message):
    
    global stato_semaforo
    global emergenza
    
    if topic == TOPIC_SEMAFORO:
        
        if message == StoplightStatus.VERDE:
            stato_semaforo = "Verde"
            emergenza = False
        elif message == StoplightStatus.GIALLO:
            stato_semaforo = "Giallo"
            emergenza = False
        elif message == StoplightStatus.ROSSO:
            stato_semaforo = "Rosso"
            emergenza = False
        elif message == StoplightStatus.EMERGENZA:
            emergenza =True
            stato_semaforo = "Emergenza"
            
    elif topic == TOPIC_RESET:
        reconnect()
    
#funzione utilizzata per istanziare il client, effettuare la connessione e la sottoscrizione ai due topic
def connect_and_subscribe():
    
    global client_id,mqtt_server,TOPIC_SEMAFORO
    
    client=MQTTClient(client_id,mqtt_server)
    client.set_callback(sub_func)
    client.connect()
    client.subscribe(TOPIC_SEMAFORO)
    client.subscribe(TOPIC_RESET)
    
    return client

#funzione per effettuare il reset dell'ESP, utilizzata nei blocchi try-except
def reconnect():
    
    display_esterno.print_text("Reset del sistema!",0,20)
    time.sleep(3)
    machine.reset()

#tentativo di connessione client,in caso di fallimento si effettua il reset con conseguente tentativo di riconessione
try:
    client=connect_and_subscribe()
except OSError as e:
    reconnect()
    
#istanziamento componenti del sistema
buzzer = Buzzer(18)
display_esterno = Oled(128,64,22,21) 
led_verde = Led(27)
led_giallo = Led(26)
led_rosso = Led(25)
semaforo = Stoplight(led_rosso,led_giallo,led_verde)

#inizializzazione variabili
stato_semaforo = ""
emergenza = False
showLogo = True
last=0
semaforo.turn_off()
duty=1000


#funzione per mostare sul display in maniera alternata il logo e lo stato del garage 
def switch_text():
    
    global last
    global showLogo
    
    #timer di 2 secondi per gestire l'alternanza logo-stato
    if (time.time()-last)> 2:
        showLogo= not showLogo
        last=time.time()

while True:
    
    try:
        client.check_msg()
        #gestione stato 'Garage libero'
        if stato_semaforo == "Verde":
            switch_text()
            if showLogo:         #gestione display
                display_esterno.show_logo()
            else:
                display_esterno.print_text(StoplightStatus.VERDE,3,10)
            semaforo.green_on()
        #gestione stato 'Sbarra in movimento'
        elif stato_semaforo == "Giallo":
            showLogo = False #durante il movimento della sbarra il logo non viene mostrato
            display_esterno.print_text("Sbarra in",5,10)
            display_esterno.print_text("movimento",7,10)
            semaforo.yellow_on()
        #gestione stato 'Sbarra in movimento'
        elif stato_semaforo == "Rosso":
            switch_text()
            if showLogo:         #gestione display
                display_esterno.show_logo()
            else:
                display_esterno.print_text(StoplightStatus.ROSSO,3,10)
            semaforo.red_on()
        #gestione stato 'Emergenza'
        elif stato_semaforo == "Emergenza":
            emergenza = True
            while emergenza:
                #controllo notifica fine emergenza
                client.check_msg()
                #gestione attivazione buzzer
                buzzer.play(duty)        
                duty = (duty+350)%1000
                #gestione blinking semaforo
                semaforo.turn_on()
                time.sleep(0.5)
                semaforo.turn_off()
                time.sleep(0.5)
                #gestione display
                display_esterno.print_emergency()
            buzzer.play(0)
    except OSError as e:
        reconnect()