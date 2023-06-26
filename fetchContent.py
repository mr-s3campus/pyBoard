from requests import request, ConnectionError, ReadTimeout
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json as j
import os, shutil

# Variabili di utilità
today = datetime.today()
mesi = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]

# Uso queste due liste per ovviare a un bug per cui la raccolta degli orari di tutti gli indirizzi presenta lezioni errate
# NB: GLI ELEMENTI DELLE LISTE SONO STATI TRATTI DAL MANIFESTO DEGLI STUDI DISPONIBILE SUL SITO DELL'UNIVERSITÀ
LM2035_1_796_FirstPer_allowed = [
    'BIG DATA C.I. - TECNOLOGIE PER I BIG DATA (Modulo)', 'EMBEDDED SYSTEMS', 'INTELLIGENZA ARTIFICIALE 1',
    'METODI DI ELABORAZIONE DEI SEGNALI', 'METODI NUMERICI AVANZATI', 'WIRELESS NETWORKS'
    ]
LM2035_1_796_SecondPer_allowed = [
    'BIG DATA C.I. - ANALISI PER BIG DATA (Modulo)', 'CRITTOGRAFIA', 'LINGUAGGI E TRADUTTORI',
    "TEORIA DELL'INFORMAZIONE E COMPRESSIONE DATI", 'WEB SYSTEMS DESIGN AND ARCHITECTURE'
    ]

LM2035_2_796_FirstPer_allowed = ['CYBERSICUREZZA','GESTIONE DEI DATI PERSONALI E FORENSI']
LM2035_2_796_SecondPer_allowed = []

LM2035_1_797_FirstPer_allowed = [
    'BIG DATA C.I. - TECNOLOGIE PER I BIG DATA (Modulo)', 'EMBEDDED SYSTEMS', 'INTELLIGENZA ARTIFICIALE 1',
    'METODI DI ELABORAZIONE DEI SEGNALI', 'METODI NUMERICI AVANZATI', 'WIRELESS NETWORKS'
    ]
LM2035_1_797_SecondPer_allowed = [
    'BIG DATA C.I. - ANALISI PER BIG DATA (Modulo)', 'LINGUAGGI E TRADUTTORI', "TEORIA DELL'INFORMAZIONE E COMPRESSIONE DATI", 
    'VISIONE ARTIFICIALE', 'WEB SYSTEMS DESIGN AND ARCHITECTURE'
]

LM2035_2_797_FirstPer_allowed = ['INTELLIGENZA ARTIFICIALE 2', 'ROBOTICA', 'ELABORAZIONE DEL LINGUAGGIO NATURALE']
LM2035_2_797_SecondPer_allowed = []

LM2035_2_Generic_FirstPer_allowed = [
    'INTELLIGENZA ARTIFICIALE', 'ROBOTICA', 'BIG DATA', "SICUREZZA DEI SISTEMI DI ELABORAZIONE DELL'INFORMAZIONE"
]
LM2035_2_Generic_SecondPer_allowed = ["SICUREZZA DEI SISTEMI DI ELABORAZIONE DELL'INFORMAZIONE"]

# URL per raccogliere i contenuti
# Calendario
calendarUrl = "https://offertaformativa.unipa.it/offweb/public/aula/weekCalendar.seam"
# Notizie
newsUrl = "https://www.unipa.it/dipartimenti/ingegneria/cds/ingegneriainformatica2035"

def getCalendar(aa, cc, aci, codInd):
    page = request(method="get",
                   url=calendarUrl,
                   params={
                       "aa": aa,
                       "cc": cc,
                       "aci": aci,
                       "codInd": codInd},
                   timeout=3
                   )

    # BeautifulSoup genera una rappresentazione manipolabile in Python di una pagina web
    soup = BeautifulSoup(page.content, "html.parser")
    a = soup.findAll("script")

    # Definiamo una variabile index per individuare il numero di eventi in calendario
    index = None
    for i in range(len(a)):
        if str(a[i]).find('var events = {"result"') != -1:
            index = i

    lessons = j.loads((str(str(a[index].getText()).split("\n")[2]).split("= ")[1])[:-1])["result"]

    return lessons


def get_orario_corso(date, aa, cc, aci, codInd):
    print('executing get_orario_corso with params:', date, aa, cc, aci, codInd)
    path_base_orari = os.path.curdir + "/static/orari/2035/"
    weekDays = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
    dateLessons = []
    date_object = datetime.strptime(date, "%Y-%m-%d")
    weekday = date_object.weekday()

    try:
        calendar = getCalendar(aa, cc, aci, codInd)

        if codInd == "796":
            path = os.path.join(path_base_orari, "1/", "796/", weekDays[weekday] + ".txt")
        elif codInd == "797":
            path = os.path.join(path_base_orari, "1/", "797/", weekDays[weekday] + ".txt")
        elif codInd is None:
            path = os.path.join(path_base_orari, "2/", weekDays[weekday] + ".txt")

        # Se la richiesta è andata bene, raccolgo i dati nella variabile
        print("Fetching lessons for " + cc + "-" + aci + "...")
        for lesson in calendar:
            if str(lesson["start"]).split(" ")[0] == date:
                dateLessons.append(lesson)        
                
        # Provo a vedere se devono essere salvati. Prima controllo se esiste il file
        try:
            # Se il file non esiste, lo creo
            print("Trying to create file " + path + "...")
            file = open(path, 'x')
            print("File " + path + " doesn't exist -> Creating it...")
            file.close()
        except FileExistsError:
            # Se il file esiste, continuo l'esecuzione per vedere se ha un contenuto diverso
            print("File " + path + " exists -> Continue")
            pass
        
        dateLessons = ripulisci_orario(date, dateLessons, aci, codInd)
        
        file = open(path, 'r')
        if file.read() == j.dumps(dateLessons):
            # Il contenuto è uguale, non faccio niente
            print("Equal content, do nothing")
            file.close()
        else:
            # Il contenuto è diverso, sovrascrivo
            print("Overwriting Local Files")
            file = open(path, 'w')
            file.write(j.dumps(dateLessons))
            file.close()
            

        return dateLessons
    except ConnectionError:
        # Errore di connessione, carico il file di default
        if codInd == "796":
            path = os.path.join(path_base_orari, "default/1/", "796/", weekDays[weekday] + ".txt")
        elif codInd == "797":
            path = os.path.join(path_base_orari, "default/1/", "797/", weekDays[weekday] + ".txt")
        elif codInd is None:
            path = os.path.join(path_base_orari, "default/2/", weekDays[weekday] + ".txt")

        print("A connection error occurred: using offline version of file @ " + path)
        file = open(path, "r")
        dateLessons = j.loads(file.read())
        
        # Rimozione preventiva dei duplicati sulla base del titolo della lezione
        dateLessons = list({lezione['title']: lezione for lezione in dateLessons}.values())
        
        file.close()
        return dateLessons
    except:
        # Errore generico, carico il file aggiornato in locale
        if codInd == "796":
            path = os.path.join(path_base_orari, "1/", "796/", weekDays[weekday] + ".txt")
        elif codInd == "797":
            path = os.path.join(path_base_orari, "1/", "797/", weekDays[weekday] + ".txt")
        elif codInd is None:
            path = os.path.join(path_base_orari, "2/", weekDays[weekday] + ".txt")    
            
        print("A generic error occurred: using local version of file @ " + path)
        file = open(path, "r")
        dateLessons = j.loads(file.read())
        
        # Rimozione preventiva dei duplicati sulla base del titolo della lezione
        dateLessons = list({lezione['title']: lezione for lezione in dateLessons}.values())
        
        file.close()
        return dateLessons
    

def ripulisci_orario(date, dateLessons, aci, codInd):
    """Questa funzione serve per rimediare ad alcuni possibili errori nell'inserimento degli
    orari nel sito di UniPa, tra cui la presenza di duplicati delle materie e la presenza di
    lezioni errate

    Args:
        date (str): La data il cui orario va 'ripulito'
        dateLessons (list): Lista di lezioni da ripulire
        aci (str): Anno del Corso di Laurea
        codInd (str): Codice dell'indirizzo (eventualmente None) dell'anno del Corso di Laurea

    Returns:
        list: La lista delle lezioni ripulita dagli errori
    """
    # Rimozione preventiva dei duplicati sulla base del titolo della lezione
    dateLessons = list({lezione['title']: lezione for lezione in dateLessons}.values())
    
    giorno_mese_anno = str(date).split("-")
    giorno = int(giorno_mese_anno[2])
    mese = int(giorno_mese_anno[1])
    anno = int(giorno_mese_anno[0])
    objectified_date = datetime(anno, mese, giorno)
    
    dateLessons_ripulito = []
    lista_materie = []
    
    if aci == "1":
        if codInd == "796":
            if objectified_date >= datetime(anno, 8, 15) and objectified_date <= datetime(anno, 12, 25):
                lista_materie = LM2035_1_796_FirstPer_allowed
            else:
                lista_materie = LM2035_1_796_SecondPer_allowed
        elif codInd == "797":
            if objectified_date >= datetime(anno, 8, 15) and objectified_date <= datetime(anno, 12, 25):
                lista_materie = LM2035_1_797_FirstPer_allowed
            else:
                lista_materie = LM2035_1_797_SecondPer_allowed
    else:
        if codInd == "796":
            if objectified_date >= datetime(anno, 8, 15) and objectified_date <= datetime(anno, 12, 25):
                lista_materie = LM2035_2_796_FirstPer_allowed
            else:
                lista_materie = LM2035_2_796_SecondPer_allowed
        elif codInd == "797":
            if objectified_date >= datetime(anno, 8, 15) and objectified_date <= datetime(anno, 12, 25):
                lista_materie = LM2035_2_797_FirstPer_allowed
            else:
                lista_materie = LM2035_2_797_SecondPer_allowed
        else:
            if objectified_date >= datetime(anno, 8, 15) and objectified_date <= datetime(anno, 12, 25):
                lista_materie = LM2035_2_Generic_FirstPer_allowed
            else:
                lista_materie = LM2035_2_Generic_SecondPer_allowed

    for lesson in dateLessons:
        for materia in lista_materie:
            # Per ogni lezione nella lista passata in input, vedo se è contenuta nelle materie previste,
            # in caso la mantengo
            if str(lesson["title"]).startswith(materia):
                dateLessons_ripulito.append(lesson)
                
    return dateLessons_ripulito
    
def get_tutte_news():
    """Funzione per raccogliere tutte le notizie dei corsi di Laurea Magistrale dal sito web di UniPa

    Returns:
        list[dict[str: Any]]: lista di notizie formattate in JSON
    """
    
    path = os.path.join(os.path.curdir + "/static/notizie/news.txt")
    defaultPath = os.path.join(os.path.curdir + "/static/notizie/defaultNews.txt")

    try:
        page = request(method="get", url=newsUrl, timeout=3)
        print("Fetching latest news...")
        soup = BeautifulSoup(page.content, "html.parser")

        newsContainer = soup.find(id="centercontainertemplate-end")
        section = newsContainer.findChildren("section")[1]
        
        titles = [i.getText() for i in section.findChildren("h2", {"class": "title"})]
        dates = [i.getText() for i in section.findChildren("p", {"class": "data-articolo"})]
        contents = [i.findParent().getText().split("\n")[3] for i in
                    section.findChildren("p", {"class": "data-articolo"})]
        fullContents = [
            get_testo_integrale(i['href']) for i in section.findChildren(attrs={"href": True})[5::]
        ]

        articles = [
            {
                "title": i[0],
                "date": i[1],
                "content": i[2],
                "fullContent": i[3]
            } for i in zip(titles, dates, contents, fullContents)
        ]

        try:
            print("Trying to create file " + path + "...")
            file = open(path, "x", encoding="utf8")
            print("File @ " + path + " doesn't exist -> Creating it...")
            file.close()
        except (FileNotFoundError, FileExistsError):
            print("File @ " + path + " not found/exists -> Continue")
            pass

        articoli_JSON = j.dumps(articles, ensure_ascii=False).encode()

        try:
            shutil.copy2(path, defaultPath)
            print("File @ " + path + " backed up...")
        except IOError:
            print("Couldn't back up file @ " + path)

        file = open(path, "w")
        file.write(articoli_JSON.decode())
        file.close()
        print("File @ " + path + " overwritten...")

        return articles
    except ConnectionError:
        print("A connection error occurred: using local copy of file @ " + path)
        file = open(defaultPath, "r", encoding="utf8")
        articles = j.loads(file.read())
        file.close()
        return articles
    

def get_testo_integrale(link):
    try:
        page = request(method="get", url=link, timeout=10)
        print("Fetching full news text @ ", link, "...")
        soup = BeautifulSoup(page.content, "html.parser")
        content = soup.find('div', {'id': 'readcontent'}).findChildren('p')

        text = ''
        text = text.join(str(x) for x in content[1::])

        if text == "":
            content = soup.find('div', {'id': 'readcontent'}).findChildren('div')
            text = text.join(str(x) for x in content[3:4:])

        return text
    except ReadTimeout:
        # La richiesta richiede troppo tempo per essere esaudita
        raise ConnectionError
        

def news_piu_recenti(notizie:list[dict], n_giorni:int):
    
    data_massima = today - timedelta(days=n_giorni)
    
    recenti = []
    
    for notizia in notizie:
        stringa_data_articolo = notizia["date"]
        
        giorno_mese_anno = str(stringa_data_articolo).split("-")
        giorno = int(giorno_mese_anno[0])
        mese = int(list(mesi).index(giorno_mese_anno[1]) + 1)
        anno = int(giorno_mese_anno[2])
        
        data_articolo = datetime(anno, mese, giorno)
        
        if data_massima <= data_articolo:
            recenti.append(notizia)
    
    return recenti
       

def get_avvisi_urgenti():
    path = os.path.join(os.path.curdir + "/static/avvisi/avvisi.txt")

    print("Opening file @ " + path + "...")
    file = open(path, "r", encoding="utf8")
    alerts = j.loads(file.read())
    
    if len(alerts) == 0:
        return None

    return alerts 