#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import glob
import logging
import os
import re
import time

import colorlog  # https://medium.com/@galea/python-logging-example-with-color-formatting-file-handlers-6ee21d363184
import feedparser
import requests
import unidecode
import urllib3
from bs4 import BeautifulSoup

try:
    from .connect_sqlite import conectionSQLite, ejecutaScriptSqlite, dumpDatabase
    from .settings import directorio_trabajo, directorio_local, nombre_db, ruta_db, sync_sqlite, sync_gdrive, \
        modo_debug
except:
    from connect_sqlite import conectionSQLite, ejecutaScriptSqlite, dumpDatabase
    from settings import directorio_trabajo, directorio_local, nombre_db, ruta_db, sync_sqlite, sync_gdrive, \
        modo_debug

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def getLogger(verbose, name='Series'):
    # Desabilita log de modulos
    # for _ in ("boto", "elasticsearch", "urllib3"):
    #    logging.getLogger(_).setLevel(logging.CRITICAL)

    logFormat = '%(levelname)s - %(module)s - %(message)s'

    bold_seq = '\033[1m'
    colorlog_format = (
        f'{bold_seq} '
        '%(log_color)s '
        f'{logFormat}'
    )

    colorlog.basicConfig(format=colorlog_format)
    # logging.basicConfig(format=colorlog_format)
    log = logging.getLogger(name)

    if verbose:
        log.setLevel(logging.DEBUG)
        log.debug('logging in mode DEBUG')
    else:
        log.setLevel(logging.INFO)
        log.info('logging in mode INFO')

    return log


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
    """ http:/guimi.net/blogs/hiparco/funcion-para-eliminar-acentos-en-python/5"""
    # s = ''.join((c for c in unicodedata.normalize('NFD',unicode(cadena)) if unicodedata.category(c) != 'Mn'))
    # return s.decode()
    # return ''.join((c for c in unicodedata.normalize('NFD', str(cadena)) if unicodedata.category(c) != 'Mn'))
    # https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
    return unidecode.unidecode(cadena)


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
        r = requests.get(url, verify=False)
        print('Descargo el fichero: {}'.format(destino))
        with open(destino, "wb") as code:
            code.write(r.content)

    if libreria == 'wget':
        import wget
        # print "downloading with wget"
        wget.download(url, destino)


# YA NO ES VALIDA
def __descargaUrlTorrent(direcc, bot=None, message=None):
    """
    Funcion que obtiene la url torrent del la dirreccion que recibe,hay que tener en cuenta que la url que recibe es la 
    del feed y que no es la apgina que contiene el torrent, pero como todas tienen la misma forma se modifica la url 
    poniendole descarga-torrent

    :param str direcc: Dirreccion de la pagina web que contiene el torrent
    :param obj bot: bot 
    :param obj message: instancia del mensaje recibido

    :return str: Nos devuelve el string con la url del torrent
    """

    if not re.match(r"^(http:\/\/).*", direcc):
        direcc = 'http://' + direcc

    if modo_debug:
        print(direcc)

    if not re.match(r"^(http:\/\/).*", direcc):
        direcc = 'http://' + direcc

    regexRecursion = "(tumejortorrent|newpct1|newpct)"

    if re.search("torrentlocura", direcc):
        if bot is not None and message is not None:
            bot.reply_to(message, 'Buscando torrent en torrentlocura.com')
        session = requests.session()

        comp1 = __descargaUrlTorrentAux(
            session.get(direcc.replace('torrentlocura.com/', 'torrentlocura.com/descarga-torrent/'), verify=False).text)
        if comp1 is not None:
            return comp1

        # opcion 2
        comp2 = __descargaUrlTorrentAux(
            session.get(direcc.replace('torrentlocura.com/', 'torrentlocura.com/descargar-seriehd/'),
                        verify=False).text)
        if comp2 is not None:
            return comp2

        return None

    elif re.search(regexRecursion, direcc):
        return __descargaUrlTorrent(re.sub(regexRecursion, "torrentlocura", direcc), message)


# YA NO ES VALIDA
def __descargaUrlTorrentAux(page):
    try:
        sopa = BeautifulSoup(page, 'html.parser')
        result = sopa.find('a', {"class": "btn-torrent"})['href']
        # Si obtenemos una url es correcto sino buscamos en el codigo html
        if re.match(
                r"^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$",
                result):
            # print(result)
            return result
        else:  # FIXME USAR selenium para simular navegador
            """ si tiene puesto en href "javascript:void(0);" llamara a la funcion openTorrent() que tiene en la variable
            window.location.href la url del torrent a descaegar, por lo que lo buscamos a pelo en el html y eliminamos
            lo sobrante, feo pero funcional
            """
            javascript = re.findall(r'window\.location\.href\ =\ \".*\"\;', page)
            return javascript[0].replace("window.location.href = \"", "").replace("\";", "")
            # return sopa.find('div', {"id": "tab1"}).a['href']
    except:
        return None


# YA NO ES VALIDA
def __descargaUrlTorrentPctnew(direcc, bot=None, message=None):
    """
    Funcion que obtiene la url torrent del la dirreccion que recibe,hay que tener en cuenta que la url que recibe es la 
    del feed y que no es la apgina que contiene el torrent, pero como todas tienen la misma forma se modifica la url 
    poniendole descarga-torrent

    :param str direcc: Dirreccion de la pagina web que contiene el torrent
    :param obj bot: bot 
    :param obj message: instancia del mensaje recibido

    :return str: Nos devuelve el string con la url del torrent
    """

    if not re.match(r"^(https?:\/\/).*", direcc):
        direcc = 'https://' + direcc

    if modo_debug:
        print(direcc)

    if re.search("pctnew", direcc):
        if bot is not None and message is not None:
            bot.reply_to(message, 'Buscando torrent en pctnew.com')
        session = requests.session()

        myUrl = direcc.replace('pctnew.com/', 'pctnew.com/descarga-torrent/')
        print(myUrl)
        comp1 = descargaUrlTorrentAuxPctnew(session.get(myUrl, verify=False).text)
        if comp1 is not None:
            return comp1

        # opcion 2
        comp2 = descargaUrlTorrentAuxPctnew(
            session.get(direcc.replace('pctnew.com/', 'pctnew.com/descargar-seriehd/'), verify=False).text)
        if comp2 is not None:
            return comp2

        return None


# YA NO ES VALIDA
def __descargaUrlTorrentAuxPctnew(page):
    try:
        sopa = BeautifulSoup(page, 'html.parser')
        result = sopa.find('a', {"class": "btn-torrent"})['href']
        # Si obtenemos una url es correcto sino buscamos en el codigo html
        if re.match(
                r"^(https?:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$",
                result):
            # print(result)
            return result
        else:  # FIXME USAR selenium para simular navegador
            """ si tiene puesto en href "javascript:void(0);" llamara a la funcion openTorrent() que tiene en la variable
            window.location.href la url del torrent a descaegar, por lo que lo buscamos a pelo en el html y eliminamos
            lo sobrante, feo pero funcional
            """
            javascript = re.findall(r'window\.location\.href\ =\ \".*\"\;', page)
            return javascript[0].replace("window.location.href = \"", "").replace("\";", "")
            # return sopa.find('div', {"id": "tab1"}).a['href']
    except Exception as e:
        return None


# YA NO ES VALIDA
def __buscaTorrentAntiguo(direcc):  # para newpct
    """
    Funcion que obtiene la url torrent del la dirreccion que recibe

    :param str direcc: Dirreccion de la pagina web que contiene el torrent

    :return str: Nos devuelve el string con la url del torrent
    """

    session = requests.session()
    page = session.get(direcc, verify=False).text
    sopa = BeautifulSoup(page, 'html.parser')

    return sopa.find('span', id="content-torrent").a['href']


def descargaUrlTorrentDonTorrent(direcc, bot=None, message=None):
    """
    Funcion que obtiene la url torrent del la dirreccion que recibe,hay que tener en cuenta que la url que recibe es la
    del feed y que no es la apgina que contiene el torrent, pero como todas tienen la misma forma se modifica la url
    poniendole descarga-torrent

    :param str direcc: Dirreccion de la pagina web que contiene el torrent
    :param obj bot: bot
    :param obj message: instancia del mensaje recibido

    :return str: Nos devuelve el string con la url del torrent
    """

    if not re.match(r"^(https?:\/\/).*", direcc):
        direcc = 'https://' + direcc

    # if modo_debug:
    #    print(direcc)

    if re.search("dontorrent", direcc):
        if bot is not None and message is not None:
            bot.reply_to(message, 'Buscando torrent en pctnew.com')
        session = requests.session()

        req_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
                       'Content-Type': 'application/x-www-form-urlencoded'}

        session = requests.session()
        login = session.get(direcc, headers=req_headers, verify=False)
        sopa = BeautifulSoup(login.text, 'html.parser')
        mtable = sopa.findAll('table', {"class": "table table-sm table-striped text-center"})

        # urls = re.findall(r'href\=\"(.*)" ', str(mtable)) # misma regex pero generica
        urls = re.findall(r'href\=\"((\/\w*)*.torrent)\"', str(mtable))

        newUrls = list()
        for i in urls:
            newUrls.append('https://dontorrent.com{}'.format(i[0]))

        # print(newUrls)
        return newUrls


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
