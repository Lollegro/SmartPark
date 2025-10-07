from sensore_ultrasuoni import HCSR04
from step_motor import StepMotor
from keypad import Keypad
from display_oled import Oled
from sensore_dht22 import SensorDHT
from enumerazione_stati import Stato
from stati_semaforo import StatoSemaforo
import random, ujson

#funzione callback per la gestione dei messaggi ricevuti dal broker
def sub_func(topic,message):
    
    global velocita_sbarra, sogliaDistanza, sogliaTemperatura, l_codice, intervalloCounter, stato_di_allarme, stato, codice, allarme_manuale, temp, sbarra_alzata, distanza1, distanza2, controllo_codice, key, stato_semaforo, tempoAllarme    
    
    if topic == MQTT_TOPIC_VELOCITA_SBARRA: 
        velocita_sbarra = float(message)
        
    elif topic == MQTT_TOPIC_SBARRA:
        
        #gestione movimento sbarra (apertura garage)
        #nel caso la sbarra sia già alzata il comando viene ignorato
        #se non si è in uno stato di allarme viene comunicato all'ESP secondaria il nuovo stato del sistema
        if int(message) and not sbarra_alzata:
            if not stato_di_allarme:
                stato_semaforo = StatoSemaforo.GIALLO
                send_message_semaforo(stato_semaforo)
            motore.raising(velocita_sbarra)
            sbarra_alzata = True
            if stato == Stato.OCCUPATO:
                controllo_codice = True
                
        #nel caso in cui si voglia abbassare la sbarra mentre è in transito una vettura, il comando non
        #viene eseguito e si mostra un notifica sulla dashboard tramite pubblicazione
        elif not int(message) and (distanza1 <= sogliaDistanza or distanza2 <= sogliaDistanza):
            message = "Auto in transito, impossibile abbassare la sbarra"
            client.publish(MQTT_TOPIC_ERRORE, message)
        
        #gestione movimento sbarra (chiusura garage)
        elif not int(message) and sbarra_alzata:
            if not stato_di_allarme:
                stato_semaforo = StatoSemaforo.GIALLO
                send_message_semaforo(stato_semaforo)
            motore.falling(velocita_sbarra)
            
            #gestione variabile per comunicazione stato corrente all'ESP secondaria
            if stato == Stato.OCCUPATO:
                stato_semaforo = StatoSemaforo.ROSSO
            else:
                stato_semaforo = StatoSemaforo.VERDE
                
            send_message_semaforo(stato_semaforo)
            sbarra_alzata = False
            controllo_codice = False
            
    elif topic == MQTT_TOPIC_SOGLIA_DISTANZA:
        sogliaDistanza = float(message)
        
    elif topic == MQTT_TOPIC_SOGLIA_TEMPERATURA:
        sogliaTemperatura = int(message)
        
    elif topic == MQTT_TOPIC_LUNGHEZZA_CODICE:
        
        #nel caso in cui sia presente un codice valido, si impedisce la modifica della lunghezza del codice
        #comunicandolo alla dashboard tramite pubblicazione messaggio
        if codice != "-":
            message = "Codice in uso, attendere che sia inserito per modificarne la lunghezza"
            client.publish(MQTT_TOPIC_ERRORE, message)
        else:
            l_codice = int(message)
            
    elif topic == MQTT_TOPIC_RESET:
        
        #nel caso in cui il garage non sia libero, si impedisce il reset del sistema
        #comunicandolo alla dashboard tramite pubblicazione messaggio
        if not stato == Stato.LIBERO:
            message = "Garage non libero, impossibile eseguire il reset del sistema"
            client.publish(MQTT_TOPIC_ERRORE, message)
        else:
            message = ""
            client.publish(MQTT_TOPIC_RESET_ESP, message)        #si comunica il reset all'ESP secondaria
            reconnect()
            
    elif topic == MQTT_TOPIC_ALLARME:
        if int(message):
            
            #si inizializza la seguente variabile utilizzata
            #per determinare la durata dell'emergenza solo se non è già iniziata
            if not tempoAllarme:
                tempoAllarme = time.time()
                
            stato_di_allarme = True
            allarme_manuale = True
            
        #se il garage non è stato evacuato o la temperatura supera la soglia prevista si impedisce la conclusione forzata
        #dello stato di emergenza, inviando un messaggio di notifica alla dashboard
        elif stato_di_allarme == True and (not stato == Stato.LIBERO or temp >= sogliaTemperatura):
            message = "Evacuazione non conclusa o incendio in corso, impossibile terminare lo stato di emergenza"
            client.publish(MQTT_TOPIC_ERRORE, message)
            
        else:
            stato_di_allarme = False
            allarme_manuale = False
            
    elif topic == MQTT_TOPIC_INTERVALLO_COUNTER_ENTRATE:
        intervalloCounter = int(message)
            
#funzione utilizzata per istanziare il client, effettuare la connessione e la sottoscrizione ai vari topic
def connect_and_subscribe():
    
    global client_id, mqtt_server, MQTT_TOPIC_VELOCITA_SBARRA, MQTT_TOPIC_SBARRA, MQTT_TOPIC_SOGLIA_DISTANZA, MQTT_TOPIC_SOGLIA_TEMPERATURA, MQTT_TOPIC_LUNGHEZZA_CODICE, MQTT_TOPIC_RESET, MQTT_TOPIC_ALLARME, MQTT_TOPIC_INTERVALLO_COUNTER_ENTRATE 
    
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(sub_func)
    client.connect()
    client.subscribe(MQTT_TOPIC_VELOCITA_SBARRA)
    client.subscribe(MQTT_TOPIC_SBARRA)
    client.subscribe(MQTT_TOPIC_SOGLIA_DISTANZA)
    client.subscribe(MQTT_TOPIC_SOGLIA_TEMPERATURA)
    client.subscribe(MQTT_TOPIC_LUNGHEZZA_CODICE)
    client.subscribe(MQTT_TOPIC_RESET)
    client.subscribe(MQTT_TOPIC_ALLARME)
    client.subscribe(MQTT_TOPIC_INTERVALLO_COUNTER_ENTRATE)
    
    return client

#funzione per effettuare il reset dell'ESP, utilizzata nei blocchi try-except
def reconnect():
    
    global distanza1, distanza2, sogliaDistanza, sbarra_alzata
    
    display_interno.fill()
    display_interno.print_text("Reset del sistema!", 0, 20)
    
    #si impedisce il reset del sistema finchè è presente un veicolo di fronte ai sensori di rilevamento
    while distanza1 < sogliaDistanza or distanza2 < sogliaDistanza:
        distanza1 = sensore1.distance_cm()
        distanza2 = sensore2.distance_cm()
        time.sleep(0.5)
    
    #nel caso la sbarra sia alzata si procede ad abbassarla prima di effettuare il reset del sistema
    if sbarra_alzata:
        motore.falling(velocita_sbarra)
        
    time.sleep(3)
    machine.reset()
      
#istanziamento componenti del sistema
rows_pin = [13,12,14,27]
cols_pin = [26,25,33,32]  
keypad_values = [
    ['1','2','3','A'],
    ['4','5','6','B'],
    ['7','8','9','C'],
    ['*','0','#','D']
]
motor_pin = [23,19,18,17]
step_sequence = [
    [1, 0, 0, 1],
    [1, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 1],
]
tastierino = Keypad(rows_pin,cols_pin,keypad_values)
motore = StepMotor(motor_pin,step_sequence)
sensore1 = HCSR04(4,35)
sensore2 = HCSR04(2,34)
dht22 = SensorDHT(15)
display_interno = Oled(128,64,22,21)
display_interno.fill()

#inizializzazione variabili 
stato = Stato.LIBERO
controllo_codice = False
key = ""
codice = "-"
stato_semaforo = StatoSemaforo.VERDE
tempoAllarme = 0
velocita_sbarra=0.005
sogliaDistanza = 10.0
sogliaTemperatura = 30.0
l_codice = 4
lastDHT = 0
lastCounter = 0
counter = 0
intervalloCounter = 60
temp = 0
humidity = 0
distanza1 = 0
distanza2 = 0
stato_di_allarme = False
allarme_manuale = False
sbarra_alzata = False

#funzione per la generazione randomica del codice
def genera_codice_numerico(l_codice):
    codice = ""
    for i in range(l_codice):
        codice += str(random.randint(0,9))
    return codice

#funzione per comunicazione lo stato all'ESP secondaria
def send_message_semaforo(message):
    client.publish(MQTT_TOPIC_SEMAFORO, message)

#funzione per comunicare lo stato del sistema alla dashboard
def send_message_stato_garage():
    
    global stato, codice
    
    messageStatus = ujson.dumps({
        "stato": stato,
        "codice": codice,
      })
    client.publish(MQTT_TOPIC_STATO_GARAGE, messageStatus)

#funzione per comunicare misurazioni temperatura/umidità alla dashboard
def send_message_misurazioni(temp,humidity):
    
    message = ujson.dumps({
        "temp": temp,
        "humidity": humidity,
      })
    client.publish(MQTT_TOPIC_MISURAZIONI, message)

#funzione per mostrare sul display interno le informazioni riguardanti le misurazioni
def print_info(temp,humidity):
    
    display_interno.fill()
    valTemp = "Temp: " + str(temp) + " C"
    valHum = "Umidita': " + str(humidity) + "%"
    display_interno.print_text(valTemp, 0, 10)
    display_interno.print_text(valHum, 0, 20)

#creazione messaggio per l'inizializzazione della dashboard con i valori di default
messageInit = ujson.dumps({
    "velocita_sbarra": velocita_sbarra,
    "sogliaDistanza": sogliaDistanza,
    "sogliaTemperatura": sogliaTemperatura,
    "l_codice": l_codice,
    "intervallo": intervalloCounter,
  })

#tentativo di connessione client,in caso di fallimento si effettua il reset con conseguente tentativo di riconessione
try:
    client = connect_and_subscribe()
except OSError as e:
    reconnect()

#inizializzazione della dashboard
client.publish(MQTT_TOPIC_INIZIALIZZAZIONE, messageInit)
send_message_stato_garage()

while True:
    try:
        client.check_msg()
        send_message_semaforo(stato_semaforo)
        
        distanza1 = sensore1.distance_cm()
        distanza2 = sensore2.distance_cm()
        
        #timer per evitare errori nell'esecuzione della lettura delle misurazioni da parte del sensore dht22
        if (time.time()-lastDHT)> 1:
            dht22.read_measure()
            temp = dht22.read_temperature()
            humidity = dht22.read_humidity()
            send_message_misurazioni(temp,humidity)
            lastDHT=time.time()
        
        #controllo allarme generato da temperature superiori alla soglia prestabilita
        if temp >= sogliaTemperatura:
            stato_di_allarme = True
            
        if stato_di_allarme == False:
            
            print_info(temp,humidity)
            
            #primo sensore -> sensore posto all'esterno del garage
            #secondo sensore -> sensore posto all'interno del garage
            
            #stato attuale LIBERO, veicolo rilevato dal primo sensore, passaggio da stato LIBERO a RILEVATO1
            if distanza1<sogliaDistanza and stato == Stato.LIBERO:
                stato_semaforo = StatoSemaforo.GIALLO
                send_message_semaforo(stato_semaforo)
                stato = Stato.RILEVATO1
                if not sbarra_alzata:
                    motore.raising(velocita_sbarra)
                    sbarra_alzata = True
            
            #stato attuale RILEVATO1, veicolo rilevato dal secondo sensore, passaggio da stato RILEVATO1 a IN_ENTRATA  
            if distanza2<sogliaDistanza and stato == Stato.RILEVATO1:
                stato = Stato.IN_ENTRATA
            
            #stato attuale RILEVATO1, veicolo non rilevato da nessun sensore, passaggio da stato RILEVATO1 a LIBERO
            if distanza1>sogliaDistanza and stato == Stato.RILEVATO1:
                if sbarra_alzata:
                    motore.falling(velocita_sbarra)
                    sbarra_alzata = False
                stato_semaforo = StatoSemaforo.VERDE
                send_message_semaforo(stato_semaforo)
                stato = Stato.LIBERO
                send_message_stato_garage()
            
            #stato attuale IN_ENTRATA, veicolo rilevato dal primo sensore e non dal secondo, passaggio da stato IN_ENTRATA a RILEVATO1
            if distanza1<sogliaDistanza and distanza2>sogliaDistanza and stato == Stato.IN_ENTRATA:
                stato = Stato.RILEVATO1
            
            #stato attuale IN_ENTRATA, veicolo non rilevato da nessun sensore, passaggio da stato IN_ENTRATA a OCCUPATO
            if distanza2>sogliaDistanza and stato == Stato.IN_ENTRATA:
                stato = Stato.OCCUPATO
                counter += 1                              #incremento counter veicoli entrati
                if sbarra_alzata:
                    motore.falling(velocita_sbarra)
                    sbarra_alzata = False
                codice = genera_codice_numerico(l_codice) #generazione codice per uscita
                send_message_stato_garage()
                stato_semaforo = StatoSemaforo.ROSSO
                send_message_semaforo(stato_semaforo)
                
            #stato attuale OCCUPATO, veicolo rilevato dal secondo sensore e codice inserito correttamente
            #passaggio da stato OCCUPATO a RILEVATO2
            if distanza2<sogliaDistanza and stato == Stato.OCCUPATO and controllo_codice:
                stato_semaforo = StatoSemaforo.GIALLO
                send_message_semaforo(stato_semaforo)
                stato = Stato.RILEVATO2
                if not sbarra_alzata:
                    motore.raising(velocita_sbarra)
                    sbarra_alzata = True  
                controllo_codice = False
            
            #stato attuale RILEVATO2, veicolo rilevato dal primo sensore, passaggio da stato RILEVATO2 a IN_USCITA
            if distanza1<sogliaDistanza and stato == Stato.RILEVATO2:
                stato = Stato.IN_USCITA
            
            #stato attuale IN_USCITA, veicolo rilevato dal secondo sensore e non dal primo, passaggio da stato IN_USCITA a RILEVATO2
            if distanza1>sogliaDistanza and distanza2<sogliaDistanza and stato == Stato.IN_USCITA:
                stato = Stato.RILEVATO2
            
            #stato attuale IN_USCITA, veicolo non rilevato da nessun sensore, passaggio da stato IN_USCITA a LIBERO    
            if distanza1>sogliaDistanza and stato == Stato.IN_USCITA:
                stato = Stato.LIBERO
                codice = "-"
                if sbarra_alzata:
                    motore.falling(velocita_sbarra)
                    sbarra_alzata = False
                send_message_stato_garage()
                stato_semaforo = StatoSemaforo.VERDE
                send_message_semaforo(stato_semaforo)
            
            #stato attuale OCCUPATO, codice non ancora inserito correttamente, controllo continuo dell'inserimento
            #del codice e gestione feedback sul display interno
            if stato == Stato.OCCUPATO and not controllo_codice:
                
                strCodice = "Codice: " + str(codice)
                display_interno.print_text(strCodice, 0, 30)
                display_interno.print_text("Inserire codice uscita", 0, 40)
                strAsterischi = ""
                
                #nel caso scatti l'allarme si interrompe l'esecuzione del ciclo per passare alla gestione dell'emergenza
                while (len(key) < l_codice and not stato_di_allarme):
                    
                    #interruzione utilizzata nel caso di apertura garage da remoto
                    if controllo_codice:
                        break
                    
                    distanza1 = sensore1.distance_cm()
                    distanza2 = sensore2.distance_cm()
                    
                    #timer per evitare errori nell'esecuzione della lettura delle misurazioni da parte del sensore dht22
                    if (time.time()-lastDHT)> 1:
                        client.check_msg()
                        dht22.read_measure()
                        temp = dht22.read_temperature()
                        humidity = dht22.read_humidity()
                        
                        if temp > sogliaTemperatura:
                            stato_di_allarme = True
                        
                        send_message_misurazioni(temp,humidity)
                        print_info(temp,humidity)
                        display_interno.print_text(strCodice, 0, 30)
                        display_interno.print_text("Inserire codice uscita", 0, 40)
                        display_interno.print_text(strAsterischi, 0, 50)
                        lastDHT=time.time()
                    
                    char = tastierino.read_value()
                    
                    #gestione tasti premuti sul keypad
                    if char:
                        key += char
                        strAsterischi += "* "
                        
                        display_interno.print_text(strAsterischi, 0, 50)
                    
                    time.sleep(0.1)
                
                #gestione caso inserimento codice corretto
                if key == codice:
                    display_interno.fill()
                    display_interno.print_text("Codice corretto", 0, 30)
                    display_interno.print_text("Arrivederci", 15, 40)
                    controllo_codice = True
                
                #gestione caso inserimento codice errato
                elif not stato_di_allarme and not controllo_codice:
                    display_interno.fill()
                    display_interno.print_text("Codice errato", 0, 30)
                    display_interno.print_text("Riprovare", 15, 40)
                    
                key = ""
                time.sleep(0.5)
        else:
            
            #si inizializza la seguente variabile utilizzata
            #per determinare la durata dell'emergenza solo se non è già iniziata
            if not tempoAllarme:
                tempoAllarme = time.time()
            
            #comunicazione stato emergenza
            stato_appoggio = stato
            codice = "-"
            message = ujson.dumps({
                "stato": Stato.EMERGENZA,
                "codice": codice,
              })
            client.publish(MQTT_TOPIC_STATO_GARAGE, message)
            
            stato_semaforo = StatoSemaforo.EMERGENZA
            send_message_semaforo(stato_semaforo)
            
            display_interno.fill()
            display_interno.print_text("EMERGENZA!", 15, 30)
            display_interno.print_text("EVACUARE!", 15, 40)
            
            #se stato attuale OCCUPATO si procede all'apertura del garage per l'evacuazione
            if stato == Stato.OCCUPATO:
                controllo_codice = True
                if not sbarra_alzata:
                    motore.raising(velocita_sbarra)
                    sbarra_alzata = True
            
            #ciclo per gestione allarme, lo stato di emergenza non può concludersi finchè:
            #la temperatura rilevata è maggiore della soglia prestabilita,
            #l'evacuazione non è stata conclusa,
            #nel caso l'allarme sia stato avviato da remoto, la fine deve essere confermata da remoto
            
            #Effettuata l'evacuazione, si procede alla chiusura del garage e
            #si impedisce l'entrata di altri veicoli fino al termine dello stato di emergenza
            while temp >= sogliaTemperatura or not stato == Stato.LIBERO or allarme_manuale == True:
                
                distanza1 = sensore1.distance_cm()
                distanza2 = sensore2.distance_cm()
                
                #timer per evitare errori nell'esecuzione della lettura delle misurazioni da parte del sensore dht22
                if (time.time()-lastDHT)> 1:
                    dht22.read_measure()
                    temp = dht22.read_temperature()
                    humidity = dht22.read_humidity()
                    send_message_misurazioni(temp,humidity)
                    lastDHT=time.time() 
                
                #gestione stati garage per garantire l'evacuazione
                #le casistiche vengono gestite dalla variabile stato_appoggio per non compromettere la condizione
                #di uscita del ciclo
                
                #stato attuale RILEVATO1, veicolo non rilevato da nessun sensore, passaggio da stato RILEVATO1 a LIBERO 
                if distanza1>sogliaDistanza and stato_appoggio == Stato.RILEVATO1:
                    stato_appoggio = Stato.LIBERO
                    stato = stato_appoggio
                
                #stato attuale RILEVATO1, veicolo rilevato dal secondo sensore, passaggio da stato RILEVATO1 a IN_ENTRATA
                if distanza2<sogliaDistanza and stato_appoggio == Stato.RILEVATO1:
                    stato_appoggio = Stato.IN_ENTRATA
                
                #stato attuale IN_ENTRATA, veicolo rilevato dal primo sensore e non dal secondo, passaggio da stato IN_ENTRATA a RILEVATO1
                if distanza2>sogliaDistanza and distanza1<sogliaDistanza and stato_appoggio == Stato.IN_ENTRATA:
                    stato_appoggio = Stato.RILEVATO1
                
                #stato attuale IN_ENTRATA, veicolo non rilevato da nessun sensore, passaggio da stato IN_ENTRATA a OCCUPATO
                if distanza2>sogliaDistanza and stato_appoggio == Stato.IN_ENTRATA:
                    stato_appoggio = Stato.OCCUPATO
                
                #stato attuale OCCUPATO, veicolo rilevato dal secondo sensore, passaggio da stato OCCUPATO a RILEVATO2
                if distanza2<sogliaDistanza and stato_appoggio == Stato.OCCUPATO:
                    stato_appoggio = Stato.RILEVATO2
                
                #stato attuale RILEVATO2, veicolo rilevato dal primo sensore, passaggio da stato RILEVATO2 a IN_USCITA
                if distanza1<sogliaDistanza and stato_appoggio == Stato.RILEVATO2:
                    stato_appoggio = Stato.IN_USCITA
                
                #stato attuale RILEVATO2, veicolo non rilevato da nessun sensore, passaggio da stato RILEVATO2 a OCCUPATO
                if distanza1>sogliaDistanza and distanza2>sogliaDistanza and stato_appoggio == Stato.RILEVATO2:
                    stato_appoggio = Stato.OCCUPATO
                
                #stato attuale IN_USCITA, veicolo rilevato dal secondo sensore e non dal primo, passaggio da stato IN_USCITA a RILEVATO2
                if distanza1>sogliaDistanza and distanza2<sogliaDistanza and stato == Stato.IN_USCITA:
                    stato = Stato.RILEVATO2
                
                #stato attuale IN_USCITA, veicolo non rilevato da nessun sensore, passaggio da stato IN_USCITA a LIBERO
                if distanza1>sogliaDistanza and stato_appoggio == Stato.IN_USCITA:
                    stato_appoggio = Stato.LIBERO
                    stato = stato_appoggio
                
                #stato attuale LIBERO, si procede alla chiusura del garage e si imposta lo stato_appoggio a EMERGENZA per non rientrare in questo caso
                if stato_appoggio == Stato.LIBERO:
                    if sbarra_alzata:
                        motore.falling(velocita_sbarra)
                        sbarra_alzata = False
                    stato_appoggio = Stato.EMERGENZA
                    
                time.sleep(0.5)
                client.check_msg()
            
            #uscita dal ciclo implica conclusione emergenza, si procede alla reinizializzazione delle seguenti variabili
            stato_di_allarme = False
            controllo_codice = False
            
            #calcolo durata stato emergenza e invio messaggio alla dashboard per storicizzazione dati dell'emergenza
            durata = time.time() - tempoAllarme
            messageEmergenza = str(durata)
            client.publish(MQTT_TOPIC_STORICO_EMERGENZE, messageEmergenza)
            
            #comunicazione termine emergenza
            stato_semaforo = StatoSemaforo.VERDE
            send_message_semaforo(stato_semaforo)
            send_message_stato_garage()
            
        #timer per gestione pubblicazione del numero di entrate nel garage ogni intervallo di tempo prestabilito        
        if (time.time()-lastCounter)> intervalloCounter:
            
            client.publish(MQTT_TOPIC_CONTEGGIO_ENTRATE, str(counter))
            counter = 0
            lastCounter=time.time()
        
        time.sleep(0.5)
        
    except OSError as e:
        reconnect()