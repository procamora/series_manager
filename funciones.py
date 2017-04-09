#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import datetime
import unicodedata
import requests
import glob
import re

import feedparser
from bs4 import BeautifulSoup

from modulos.connect_sqlite import conectionSQLite, ejecutaScriptSqlite, dumpDatabase
from modulos.settings import directorio_trabajo, directorio_local, nombre_db, ruta_db, sync_sqlite, sync_gdrive, \
    modo_debug


def creaDirectorioTrabajo():
    """
    Funcion encargada de checkear el correcto estado del directorio de trabajo
    Si el directorio no existe lo crea y crea la base de datos dejandola vacia
    
    Si el directorio existe comprueba que exista la base de datos y que no este vacia
    """

    if not os.path.exists(directorio_trabajo):
        if modo_debug:
            print("NO EXISTE DIRECTORIO TRABAJO")
        os.mkdir(directorio_trabajo)
        plantillaDatabase()
        plantillaFicheroConf()
    else:
        ruta_id = '{}/{}'.format(directorio_local, sync_sqlite)
        if not os.path.exists(ruta_db) or os.stat(ruta_db).st_size == 0:
            print(1)
            plantillaDatabase()
        if not os.path.exists(ruta_id) or os.stat(ruta_id).st_size == 0:
            print(2)
            plantillaFicheroConf()


def crearFichero(fichero):
    with open(fichero, 'w') as f:
        f.write("")


def cambiaBarras(texto):
    return texto.replace('\\', '/')


def dbConfiguarion():
    """
    Funcion que obtiene los valores de la configuracion de un programa, devuelve el diciconario con los datos

    :return dict: Nos devuelve un diccionario con los datos
    """

    try:
        with open(r'{}/{}'.format(directorio_local, sync_sqlite), 'r') as f:
            id_db = f.readline()
    except:
        print('fallo en dbConfiguarion')
        id_db = 1

    query = 'SELECT * FROM Configuraciones WHERE id IS {}'.format(id_db)
    # print u'{}/{}'.format(creaDirectorioTrabajo(),name_db)
    consulta = conectionSQLite('{}/{}'.format(directorio_trabajo, nombre_db), query, True)[0]
    return consulta


def plantillaFicheroConf():
    """
    Si hay una configuracion en la la carpeta del programa la mueve a la carpeta
    de configuracion, sino la hay comprueba si existe el fichero, si existe y esta
    vacio o no existe lo pone a 1
    """

    fichero_conf = '{}/{}'.format(directorio_local, sync_sqlite)
    if os.path.exists(sync_sqlite):
        if modo_debug:
            print(sync_sqlite, fichero_conf)
        os.rename(sync_sqlite, fichero_conf)
    else:
        if os.path.exists(fichero_conf):
            if os.stat(fichero_conf).st_size == 0:
                with open(fichero_conf, 'w') as f:
                    f.write("1")
        else:
            with open(fichero_conf, 'w') as f:
                f.write("1")


def plantillaDatabase():
    """
    Funcion encargada de checkear el correcto estado de la base de datos, si no existe la base de datos o esta vacia le
    cargo la estructura basica
    """

    ficheros_sql = glob.glob('{}/SQL/*estructura.sql'.format(directorio_local))
    fichero_db = '{}/{}'.format(directorio_trabajo, nombre_db)

    if not os.path.exists(fichero_db) or not os.stat(fichero_db).st_size > 50000:  # estructura pesa 72Kb
        if modo_debug:
            print("creando db")
        with open(cambiaBarras(ficheros_sql[-1]), 'r') as f:
            plantilla = f.read()
        ejecutaScriptSqlite(fichero_db, plantilla)


def crearBackUpCompletoDB():
    """
    Funcion encargada de generar backup de la base de datos y guardarlo 
    """

    data = dumpDatabase(ruta_db)
    try:
        with open('{}/SQL/{}.sql'.format(directorio_local, time.strftime("%Y%m%d")), 'w') as f:
            f.write(data)
    except:
        print('error al hacer backup')


def calculaDiaSemana():
    """
    Te dice el dia de la semana en el que estamos, lo uso para ordenar serie de mas cerca a mas lejos
    """

    x = datetime.datetime.now()
    dicdias = {'MONDAY': 'Lunes',
               'TUESDAY': 'Martes',
               'WEDNESDAY': 'Miercoles',
               'THURSDAY': 'Jueves',
               'FRIDAY': 'Viernes',
               'SATURDAY': 'Sabado',
               'SUNDAY': 'Domingo'}

    anho = x.year
    mes = x.month
    dia = x.day

    fecha = datetime.date(anho, mes, dia)

    try:
        a = dicdias[fecha.strftime('%A').upper()]
        return eliminaTildes(a)
    # en linux en algunas distriuciones sale el dia en castellano, por eso lo paso directamente
    # poniendo la primera letra en mayusculas
    except KeyError:
        a = fecha.strftime('%A').capitalize()
        return eliminaTildes(a)


def fechaToNumero(dia):
    """
    Convierte el dia de la semana a un numero, y luego te crea una lista ordenada
    de los dias de la semana de mas cerca a menos cerca
    """

    DiaNombre = ["Lunes", "Martes", "Miercoles",
                 "Jueves", "Viernes", "Sabado", "Domingo"]
    lista = list()
    num = DiaNombre.index(dia)  # localizo en indice del dia en el que estoy
    # guardo la parte de la derecha de la semana y luego la izq
    lista.extend(DiaNombre[num:])
    lista.extend(DiaNombre[:num])
    return lista


def eliminaTildes(cadena):
    """	http:/guimi.net/blogs/hiparco/funcion-para-eliminar-acentos-en-python/5"""
    # s = ''.join((c for c in unicodedata.normalize('NFD',unicode(cadena)) if unicodedata.category(c) != 'Mn'))
    # return s.decode()
    return ''.join((c for c in unicodedata.normalize('NFD', str(cadena)) if unicodedata.category(c) != 'Mn'))


def descargaFichero(url, destino, libreria='requests'):
    if libreria == 'urllib':
        import urllib
        # print "downloading with urllib"
        urllib.urlretrieve(url, destino)

    if libreria == 'urllib2':
        import urllib2
        # print "downloading with urllib2"
        f = urllib2.urlopen(url)
        data = f.read()
        with open(destino, "wb") as code:
            code.write(data)

    if libreria == 'requests':
        # print "downloading with requests"
        r = requests.get(url)
        with open(destino, "wb") as code:
            code.write(r.content)

    if libreria == 'wget':
        import wget
        # print "downloading with wget"
        wget.download(url, destino)


def descargaUrlTorrent(direcc, bot=None, message=None):  # PARA NEWPCT1
    """
    Funcion que obtiene la url torrent del la dirreccion que recibe,hay que tener en cuenta que la url que recibe es la 
    del feed y que no es la apgina que contiene el torrent, pero como todas tienen la misma forma se modifica la url 
    poniendole descarga-torrent

    :param str direcc: Dirreccion de la pagina web que contiene el torrent
    :param obj bot: bot 
    :param obj message: instancia del mensaje recibido

    :return str: Nos devuelve el string con la url del torrent
    """

    if re.search("newpct1", direcc):
        if bot is not None and message is not None:
            bot.reply_to(message, 'Buscando torrent en newpct1')
        session = requests.session()
        page = session.get(direcc.replace('newpct1.com/', 'newpct1.com/descarga-torrent/'), verify=False).text
        sopa = BeautifulSoup(page, 'html.parser')
        return sopa.find('div', {"id": "tab1"}).a['href']

    elif re.search("tumejortorrent", direcc):
        # han cambiado la pagina, modifico tumejortorrent por newpct1
        """
        bot.reply_to(message, 'Buscando torrent en tumejortorrent')
        session = requests.session()
        page = session.get(direcc, verify=False).text
        sopa = BeautifulSoup(page, 'html.parser')
        # print(sopa.findAll('div', {"id": "tab1"}))
        print(sopa.find_all("a", class_="btn-torrent")[0]['href'])
        return sopa.find('div', {"id": "tab1"}).a['href']
        """
        return descargaUrlTorrent(direcc.replace("tumejortorrent", "newpct1"), message)


def buscaTorrentAntiguo(direcc):  # para newpct
    """
    Funcion que obtiene la url torrent del la dirreccion que recibe

    :param str direcc: Dirreccion de la pagina web que contiene el torrent

    :return str: Nos devuelve el string con la url del torrent
    """

    session = requests.session()
    page = session.get(direcc, verify=False).text
    sopa = BeautifulSoup(page, 'html.parser')

    return sopa.find('span', id="content-torrent").a['href']


def feedParser(url):
    """
    Da un fallo en fedora 23, por eso hace falta esta funcion
    https://github.com/kurtmckee/feedparser/issues/30
    """

    try:
        return feedparser.parse(url)
    except TypeError:
        if 'drv_libxml2' in feedparser.PREFERRED_XML_PARSERS:
            feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2')
            return feedparser.parse(url)
        else:
            raise

def muestraMensaje(label, texto='Texto plantilla', estado=True):
    """
    Muestra una determinada label con rojo o verde (depende del estado) y con el texto indicado
    """

    label.setText(texto)
    if estado:
        label.setStyleSheet('color: green')
    else:
        label.setStyleSheet('color: red')


def escapaParentesis(texto):
    """
    No he probado si funciona con series como powers
    """
    return texto.replace('(', '\\(').replace(')', '\\)')

def internetOn():
    try:
        session = requests.session()
        session.get('http://www.google.com', verify=False)
        return True
    except requests.exceptions.ConnectionError:
        return False
