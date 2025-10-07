
#classe utilizzata per emulare un'enumerazione,
#le cui variabili statiche vengono utilizzata
#per memorizzare gli stati che il sistema può assumere

class Stato:
    LIBERO = "Libero"
    OCCUPATO = "Occupato"
    RILEVATO1 = "Auto rilevata dal primo sensore"
    RILEVATO2 = "Auto rilevata dal secondo sensore"
    IN_ENTRATA = "Auto in entrata"
    IN_USCITA = "Auto in uscita"
    EMERGENZA = "Emergenza"