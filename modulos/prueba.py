import re
import requests
from bs4 import BeautifulSoup

def descargaTorrent(direcc, message):  # PARA NEWPCT1
    """
    Funcion que obtiene la url torrent del la dirreccion que recibe

    :param str direcc: Dirreccion de la pagina web que contiene el torrent

    :return str: Nos devuelve el string con la url del torrent
    """
    if re.search("newpct1", direcc):
        session = requests.session()
        page = session.get(direcc, verify=False).text
        sopa = BeautifulSoup(page, 'html.parser')
        return sopa.find('div', {"id": "tab1"}).a['href']

    elif re.search("tumejortorrent", direcc):
        """
        session = requests.session()
        page = session.get(direcc, verify=False).text
        sopa = BeautifulSoup(page, 'html.parser')
        # print(sopa.findAll('div', {"id": "tab1"}))
        print(sopa.find_all("a", class_="btn-torrent")[0]['href'])
        return sopa.find('div', {"id": "tab1"}).a['href']
        """
        return descargaTorrent(direcc.replace("tumejortorrent", "newpct1"), message)

def descargaFichero(url, destino):
    r = requests.get(url)
    with open(destino, "wb") as code:
        code.write(r.content)


def handle_newpct1(message):
    # buscamos el genero
    regexGenero = re.search('descarga-torrent', message)
    if regexGenero:  # si hay find continua, sino retorno None el re.search
        urlPeli = message.text
    else:
        urlPeli = re.sub('(http://)?www.newpct1.com/', 'http://www.newpct1.com/descarga-torrent/', message)

    url = descargaTorrent(urlPeli, message)
    print(url)


handle_newpct1('http://www.tumejortorrent.com/descargar-pelicula/nevada-express/bluray-microhd/')