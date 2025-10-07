
#classe utilizzata per emulare un'enumerazione,
#le cui variabili statiche vengono utilizzata
#per comunicare all'ESP secondaria lo stato corrente del sistema

class StatoSemaforo:
    VERDE = "Garage libero"
    GIALLO = "Sbarra in movimento"
    ROSSO = "Garage occupato"
    EMERGENZA = "Emergenza! Attenzione uscire dal garage!"