import re
import os
import time

import requests
import feedparser
from bs4 import BeautifulSoup

from modulos.connect_sqlite import conectionSQLite, ejecutaScriptSqlite
from modulos.pushbullet2 import PB2
from modulos.telegram2 import TG2
from modulos.mail2 import ML2
from modulos.settings import modo_debug, directorio_trabajo, ruta_db
import funciones


def descargaTorrent(direcc):  # PARA NEWPCT1
    '''
    Funcion que obtiene la url torrent del la dirreccion que recibe

    :param str direcc: Dirreccion de la pagina web que contiene el torrent

    :return str: Nos devuelve el string con la url del torrent
    '''

    session = requests.session()
    page = session.get(direcc, verify=False).text
    # page = urllib.urlopen(direcc).read()
    sopa = BeautifulSoup(page, 'html.parser')
    #print(sopa.findAll('div', {"id": "tab1"}))
    print(sopa.find_all("a", class_="btn-torrent")[0]['href'])
    return sopa.find('div', {"id": "tab1"}).a['href']



url = "http://tumejortorrent.com/descargar-seriehd/arrow/capitulo-58/hdtv-720p-ac3-5-1/"

descargaTorrent(url)