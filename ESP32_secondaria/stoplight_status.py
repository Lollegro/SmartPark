
#classe utilizzata per emulare un'enumerazione, le cui variabili statiche
#vengono utilizzate per memorizzare gli stati che il sistema può assumere

class StoplightStatus:
    
    VERDE =b"Garage libero"
    GIALLO =b"Sbarra in movimento"
    ROSSO = b"Garage occupato"
    EMERGENZA = b"Emergenza! Attenzione uscire dal garage!"
    