
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, Response, request
import urllib.request
import simplejson as json
import io
import os

app = Flask(__name__)


def dataNetista():
    global data
    with urllib.request.urlopen('http://hazor.eu.pythonanywhere.com/2021/data2021.json') as response:
        data = json.load(response)

def dataKansiosta():
    global data
    tiedosto = io.open("c:/mytemp/kurssit/ties4080/vt1/data2021.json", encoding="UTF-8")
    data = json.load(tiedosto)


# kirjotetaan json tiedosto static filesiin pythonanywheressä
def kirjotaJSON(polku, tied, data):
    tiedosto_sij = polku + tied + '.json'
    with open(tiedosto_sij, 'w') as fp:
        json.dump(data, fp)

# tulostetaan taso 1 joukkuelistaus
def tulosta_joukkueet():
    lista = []
    teksti = ""
    for i in range(len(data['sarjat'])):
        for j in range(len(data['sarjat'][i]['joukkueet'])):
            lista.append(data['sarjat'][i]['joukkueet'][j]['nimi'].strip())
    lista.sort(key=str.lower)
    for k in range(len(lista)):
        teksti += lista[k] + '\n'

    return teksti

# tulostetaan taso 1 rastikoodit sivulle
def rastikoodit():
    ras_cod = ""
    lista = []
    for i in range(len(data['rastit'])):
        if data['rastit'][i]['koodi'][0] <= '9' :
            lista.append(data['rastit'][i]['koodi'])

    lista.sort()
    for j in range(len(lista)):
        ras_cod += lista[j] + ';'
    return ras_cod

# lisätään joukkue dataan
def lisaaJoukkue(sarja, joukkue):
    for i in range(len(data['sarjat'])):
        for j in range(len(data['sarjat'][i]['joukkueet'])):
            if joukkue.get('nimi').lower().strip() == data['sarjat'][i]['joukkueet'][j]['nimi'].lower().strip():
                return
    for sarjadata in data['sarjat']:
        if sarja.lower() == sarjadata['nimi'].lower() and joukkue.keys() == sarjadata['joukkueet'][0].keys():
            joukkue['id'] = joukkue_id()
            sarjadata['joukkueet'].append(joukkue)

# haetaan lisätylle joukkueelle uusi id (aina yhtä suurempi mitä edellinen suurin)
def joukkue_id():
    jid = 0
    for i in range(len(data['sarjat'])):
        for j in range(len(data['sarjat'][i]['joukkueet'])):
            if data['sarjat'][i]['joukkueet'][j]['id'] > jid:
                jid = data['sarjat'][i]['joukkueet'][j]['id']
    return jid+1

# Poistaa joukkueen
def poistaJoukkue(sarja, joukkue):
    for i in range(len(data['sarjat'])):
        if sarja.lower() == data['sarjat'][i]['nimi']:
            for j in range (len(data['sarjat'][i]['joukkueet'])):
                if joukkue.lower().strip() == data['sarjat'][i]['joukkueet'][j]['nimi'].lower().strip():
                    data['sarjat'][i]['joukkueet'].pop(j)
                    return

# Laittaa koodit joukkueen rastidictiin pisteen laskua varten
def rastikoodit_joukkueille():
    for j in range(len(data['sarjat'])):
        for k in range(len(data['sarjat'][j]['joukkueet'])):

            for i in range(len(data['sarjat'][j]['joukkueet'][k]['rastit'])):
                koodi = data['sarjat'][j]['joukkueet'][k]['rastit'][i]['rasti']
                for rasti in data['rastit']:
                    try:
                        if rasti.get('id') == int(koodi):
                            data['sarjat'][j]['joukkueet'][k]['rastit'][i]['koodi'] = rasti.get('koodi')
                    except:
                        continue

# lasketaan pisteet joukkueille
def pisteet_joukkueille():
    for j in range(len(data['sarjat'])):
        for k in range(len(data['sarjat'][j]['joukkueet'])):
            thisset = set()
            for i in range(len(data['sarjat'][j]['joukkueet'][k]['rastit'])):
                try:
                    thisset.add(data['sarjat'][j]['joukkueet'][k]['rastit'][i]['koodi'])
                except:
                    continue
            tulos = 0
            for i in thisset:
                if i[0:1] <= '9':
                    tulos += int(i[0:1])
            data['sarjat'][j]['joukkueet'][k]['pisteet'] = tulos

# Tulostaa sivulle taso 3 mukaisen listauksen (joukkueen nimi, pisteet ja joukkueen jäsenet
def tulosta_joukkueet_taso3():
    teksti = ""
    joukkueet = []
    jasenet = []
    for i in range(len(data['sarjat'])):
        for j in range(len(data['sarjat'][i]['joukkueet'])):
            joukkue_tiedot = {
                'nimi': "",
                'pisteet': 0,
                'jasenet': []
            }
            joukkue_tiedot['nimi'] = data['sarjat'][i]['joukkueet'][j]['nimi'].strip()
            joukkue_tiedot['pisteet'] = data['sarjat'][i]['joukkueet'][j]['pisteet']
            data['sarjat'][i]['joukkueet'][j].pop('pisteet', None)
            jasenet = data['sarjat'][i]['joukkueet'][j]['jasenet']
            jasenet.sort(key=str.lower)
            joukkue_tiedot['jasenet'] = jasenet
            joukkueet.append(joukkue_tiedot)

    jarjestetty = sorted(joukkueet, key=lambda k: (-k['pisteet'], k['nimi'].lower()), reverse=False)
    #print(jarjestetty)
    for i in range(len(jarjestetty)):
        teksti += jarjestetty[i]['nimi'] + " ("+str(jarjestetty[i]['pisteet'])+" p)"+'\n'
        for j in range(len(jarjestetty[i]['jasenet'])):
            teksti += " "+jarjestetty[i]['jasenet'][j]+'\n'

    kirjotaJSON('C:/MyTemp/kurssit/ties4080/vt1/','data2021',data)
    return teksti


# leimaustavat url parametreistä
def lisaaLeimat(leimat):
    joukkueen_leimat = []
    if len(leimat) < 1:
        return joukkueen_leimat
    if len(leimat) > 0:
        for i in range(len(leimat)):
            for k in range(len(data['leimaustapa'])):
                if leimat[i].lower() == data['leimaustapa'][k].lower():
                    joukkueen_leimat.append(k)

    jarj_leimat = sorted(joukkueen_leimat)
    return jarj_leimat


# tulostuksien reitti
@app.route('/vt1')
def vt1():
    if request.args.get("reset") == "1":
        dataNetista()
    if request.args.get("reset") == "0" or request.args.get("reset") == None:
        dataKansiosta()
    if request.args.get("nimi") and request.args.get("sarja") and (request.args.get("tila") == "insert" or request.args.get("tila") == None):
        joukkue = {
                    "nimi": request.args.get("nimi"),
                    "jasenet": request.args.getlist("jasen"),
                    "id": 0,
                    "leimaustapa": lisaaLeimat(request.args.getlist("leimaustapa")),
                    "rastit": []
                }
        print(joukkue)
        lisaaJoukkue(request.args.get("sarja"), joukkue)
    if request.args.get("nimi") and request.args.get("sarja") and request.args.get("tila") == "delete":
        poistaJoukkue(request.args.get("sarja"), request.args.get("nimi"))
    rastikoodit_joukkueille()
    pisteet_joukkueille()

    kirjotaJSON('C:/MyTemp/kurssit/ties4080/vt1/','data2021',data)
    return Response(tulosta_joukkueet() + '\n' + rastikoodit() + '\n' + '\n'+ tulosta_joukkueet_taso3(), mimetype="text/plain;charset=UTF-8")




@app.route('/data.json')
def jsondata():
    return data


if __name__ == '__main__':
    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", "5000")

    app.run(host=host, port=port)

