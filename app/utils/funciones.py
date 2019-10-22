#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import glob
import os
import re
import time
from pathlib import Path  # nueva forma de trabajar con rutas
from typing import List, NoReturn

import feedparser
import requests
import unidecode
import urllib3
from bs4 import BeautifulSoup

from app import logger
from app.utils.connect_sqlite import execute_script_sqlite, dump_database
from app.utils.settings import DIRECTORY_WORKING, DIRECTORY_LOCAL, PATH_DATABASE

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def create_directory_work() -> NoReturn:
    """
    Funcion encargada de checkear el correcto estado del directorio de trabajo
    Si el directorio no existe lo crea y crea la base de datos dejandola vacia
    
    Si el directorio existe comprueba que exista la base de datos y que no este vacia
    """

    if not DIRECTORY_WORKING.exists():
        logger.debug(f"NO EXISTE DIRECTORIO TRABAJO, CREANDOLO: {DIRECTORY_WORKING}")
        Path.mkdir(DIRECTORY_WORKING)
        template_database()  # crea db con la estructura adecuada
        # template_file_conf()
    else:
        if not PATH_DATABASE.exists() or Path.stat(PATH_DATABASE).st_size == 0:
            logger.info(1)
            template_database()  # crea db con la estructura adecuada
        # if not os.path.exists(SYNC_SQLITE) or os.stat(SYNC_SQLITE).st_size == 0:
        #    logger.info(2)
        #    template_file_conf()


def create_file(fichero) -> NoReturn:
    with open(fichero, 'w') as f:
        f.write("")


def change_bars(texto) -> str:
    return texto.replace('\\', '/')


'''
def template_file_conf() -> NoReturn:
    """
    Si hay una configuracion en la la carpeta del programa la mueve a la carpeta
    de configuracion, sino la hay comprueba si existe el fichero, si existe y esta
    vacio o no existe lo pone a 1
    """

    fichero_conf = f'{DIRECTORY_LOCAL}/{SYNC_SQLITE.split("/")[-1]}'
    if os.path.exists(SYNC_SQLITE):
        logger.debug(f'{SYNC_SQLITE} & {fichero_conf}')
        os.rename(SYNC_SQLITE, fichero_conf)
    else:
        if os.path.exists(fichero_conf):
            if os.stat(fichero_conf).st_size == 0:
                with open(fichero_conf, 'w') as f:
                    f.write("1")
        else:
            with open(fichero_conf, 'w') as f:
                f.write("1")
'''


def template_database() -> NoReturn:
    """
    Funcion encargada de checkear el correcto estado de la base de datos, si no existe la base de datos o esta vacia le
    cargo la estructura basica
    """

    ficheros_sql = glob.glob(f'{DIRECTORY_LOCAL}/SQL/*estructura.sql')
    print(DIRECTORY_LOCAL)
    print(ficheros_sql)

    if not PATH_DATABASE.exists() or not Path.stat(PATH_DATABASE).st_size > 50000:  # estructura pesa 72Kb
        logger.debug("creando db")
        with open(change_bars(ficheros_sql[-1]), 'r') as f:
            plantilla = f.read()
        execute_script_sqlite(PATH_DATABASE, plantilla)


def create_full_backup_db() -> NoReturn:
    """
    Funcion encargada de generar backup de la base de datos y guardarlo 
    """

    data = dump_database(PATH_DATABASE)
    if data is None:
        logger.error(f'database {PATH_DATABASE} not exists')
        return
    try:
        with open(f'{DIRECTORY_LOCAL}/SQL/{time.strftime("%Y%m%d")}.sql', "w") as f:
            f.write(data)
    except Exception as e:
        logger.error(f'error al hacer backup: {e}')


def calculate_day_week() -> str:
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
        return remove_tildes(a)
    # en linux en algunas distriuciones sale el dia en castellano, por eso lo paso directamente
    # poniendo la primera letra en mayusculas
    except KeyError:
        a = fecha.strftime('%A').capitalize()
        return remove_tildes(a)


def date_to_number(dia: str) -> List[str]:
    """
    Convierte el dia de la semana a un numero, y luego te crea una lista ordenada
    de los dias de la semana de mas cerca a menos cerca
    """

    dia_nombre = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    lista: List[str] = list()
    num = dia_nombre.index(dia)  # localizo en indice del dia en el que estoy
    # guardo la parte de la derecha de la semana y luego la izq
    lista.extend(dia_nombre[num:])
    lista.extend(dia_nombre[:num])
    return lista


def remove_tildes(cadena):
    """ http:/guimi.net/blogs/hiparco/funcion-para-eliminar-acentos-en-python/5"""
    # s = ''.join((c for c in unicodedata.normalize('NFD',unicode(cadena)) if unicodedata.category(c) != 'Mn'))
    # return s.decode()
    # return ''.join((c for c in unicodedata.normalize('NFD', str(cadena)) if unicodedata.category(c) != 'Mn'))
    # https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
    return unidecode.unidecode(cadena)


def download_file(url, destino, libreria='requests'):
    if libreria == 'urllib2':
        import urllib2
        f = urllib2.urlopen(url)
        data = f.read()
        with open(destino, "wb") as code:
            code.write(data)

    elif libreria == 'requests':
        r = requests.get(url, verify=False)
        logger.debug(f'Descargo el fichero: {destino}')
        with open(destino, "wb") as code:
            code.write(r.content)

    elif libreria == 'wget':
        import wget
        wget.download(url, destino)


# YA NO ES VALIDA
def _descarga_url_torrent(direcc, bot=None, message=None):
    """
    Funcion que obtiene la url torrent del la dirreccion que recibe,hay que tener en cuenta que la url que recibe es la 
    del feed y que no es la apgina que contiene el torrent, pero como todas tienen la misma forma se modifica la url 
    poniendole descarga-torrent

    :param str direcc: Dirreccion de la pagina web que contiene el torrent
    :param obj bot: bot 
    :param obj message: instancia del mensaje recibido

    :return str: Nos devuelve el string con la url del torrent
    """

    if not re.match(r"^(http://).*", direcc):
        direcc = 'http://' + direcc

    logger.debug(direcc)

    if not re.match(r"^(http://).*", direcc):
        direcc = 'http://' + direcc

    regex_recursion = "(tumejortorrent|newpct1|newpct)"

    if re.search("torrentlocura", direcc):
        if bot is not None and message is not None:
            bot.reply_to(message, 'Buscando torrent en torrentlocura.com')
        session = requests.session()

        comp1 = _descarga_url_torrent_aux(
            session.get(direcc.replace('torrentlocura.com/', 'torrentlocura.com/descarga-torrent/'), verify=False).text)
        if comp1 is not None:
            return comp1

        # opcion 2
        comp2 = _descarga_url_torrent_aux(
            session.get(direcc.replace('torrentlocura.com/', 'torrentlocura.com/descargar-seriehd/'),
                        verify=False).text)
        if comp2 is not None:
            return comp2

        return None

    elif re.search(regex_recursion, direcc):
        return _descarga_url_torrent(re.sub(regex_recursion, "torrentlocura", direcc), message)


# YA NO ES VALIDA
def _descarga_url_torrent_aux(page):
    try:
        sopa = BeautifulSoup(page, 'html.parser')
        result = sopa.find('a', {"class": "btn-torrent"})['href']
        # Si obtenemos una url es correcto sino buscamos en el codigo html
        regex = r"^(http://www\.|https://www\.|http://|https://)?[a-z0-9]+([\-\.][a-z0-9]+)*\.[a-z]{2,5}" \
                r"(:[0-9]{1,5})?(\/.*)?$"
        if re.match(regex, result):
            return result
        else:  # FIXME USAR selenium para simular navegador
            """ si tiene puesto en href "javascript:void(0)" llamara a la funcion openTorrent() que tiene en la variable
            window.location.href la url del torrent a descaegar, por lo que lo buscamos a pelo en el html y eliminamos
            lo sobrante, feo pero funcional
            """
            javascript = re.findall(r'window\.location\.href = \".*\";', page)
            return javascript[0].replace("window.location.href = \"", "").replace("\";", "")
            # return sopa.find('div', {"id": "tab1"}).a['href']
    except Exception as e:
        print(e)
        return None


# YA NO ES VALIDA
def _descarga_url_torrent_pctnew(direcc, bot=None, message=None):
    """
    Funcion que obtiene la url torrent del la dirreccion que recibe,hay que tener en cuenta que la url que recibe es la 
    del feed y que no es la apgina que contiene el torrent, pero como todas tienen la misma forma se modifica la url 
    poniendole descarga-torrent

    :param str direcc: Dirreccion de la pagina web que contiene el torrent
    :param obj bot: bot 
    :param obj message: instancia del mensaje recibido

    :return str: Nos devuelve el string con la url del torrent
    """

    if not re.match(r"^(https?://).*", direcc):
        direcc = 'https://' + direcc

    logger.debug(direcc)

    if re.search("pctnew", direcc):
        if bot is not None and message is not None:
            bot.reply_to(message, 'Buscando torrent en pctnew.com')
        session = requests.session()

        my_url = direcc.replace('pctnew.com/', 'pctnew.com/descarga-torrent/')
        logger.debug(my_url)
        comp1 = _descarga_url_torrent_aux_pctnew(session.get(my_url, verify=False).text)
        if comp1 is not None:
            return comp1

        # opcion 2
        comp2 = _descarga_url_torrent_aux_pctnew(
            session.get(direcc.replace('pctnew.com/', 'pctnew.com/descargar-seriehd/'), verify=False).text)
        if comp2 is not None:
            return comp2

        return None


# YA NO ES VALIDA
def _descarga_url_torrent_aux_pctnew(page):
    try:
        sopa = BeautifulSoup(page, 'html.parser')
        result = sopa.find('a', {"class": "btn-torrent"})['href']
        # Si obtenemos una url es correcto sino buscamos en el codigo html
        regex = r"^(https?://www\.|https://www\.|http://|https://)?[a-z0-9]+([\-\.][a-z0-9]+)*\.[a-z]{2,5}" \
                r"(:[0-9]{1,5})?(\/.*)?$"
        if re.match(regex, result):
            return result
        else:  # FIXME USAR selenium para simular navegador
            """ si tiene puesto en href "javascript:void(0)" llamara a la funcion openTorrent() que tiene en la variable
            window.location.href la url del torrent a descaegar, por lo que lo buscamos a pelo en el html y eliminamos
            lo sobrante, feo pero funcional
            """
            javascript = re.findall(r'window\.location\.href = \".*\";', page)
            return javascript[0].replace("window.location.href = \"", "").replace("\";", "")
            # return sopa.find('div', {"id": "tab1"}).a['href']
    except Exception as e:
        print(e)
        return None


# YA NO ES VALIDA
def _busca_torrent_antiguo(direcc):  # para newpct
    """
    Funcion que obtiene la url torrent del la dirreccion que recibe

    :param str direcc: Dirreccion de la pagina web que contiene el torrent

    :return str: Nos devuelve el string con la url del torrent
    """

    session = requests.session()
    page = session.get(direcc, verify=False).text
    sopa = BeautifulSoup(page, 'html.parser')

    return sopa.find('span', id="content-torrent").a['href']


def get_url_torrent_dontorrent(direcc, bot=None, message=None):
    """
    Funcion que obtiene la url torrent del la dirreccion que recibe,hay que tener en cuenta que la url que recibe es la
    del feed y que no es la apgina que contiene el torrent, pero como todas tienen la misma forma se modifica la url
    poniendole descarga-torrent

    :param str direcc: Dirreccion de la pagina web que contiene el torrent
    :param obj bot: bot
    :param obj message: instancia del mensaje recibido

    :return str: Nos devuelve el string con la url del torrent
    """

    if not re.match(r"^(https?://).*", direcc):
        direcc = 'https://' + direcc

    if re.search("dontorrent", direcc):
        if bot is not None and message is not None:
            bot.reply_to(message, 'Buscando torrent en pctnew.com')

        req_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
                       'Content-Type': 'application/x-www-form-urlencoded'}

        session = requests.session()
        login = session.get(direcc, headers=req_headers, verify=False)
        sopa = BeautifulSoup(login.text, 'html.parser')
        mtable = sopa.findAll('table', {"class": "table table-sm table-striped text-center"})

        # urls = re.findall(r'href\=\"(.*)" ', str(mtable)) # misma regex pero generica
        urls = re.findall(r'href=\"((\/\w*)*.torrent)\"', str(mtable))

        new_urls = list()
        for i in urls:
            new_urls.append(f'https://dontorrent.com{i[0]}')

        return new_urls


def get_url_torrent_dontorrent_direct(direcc, bot=None, message=None):
    """
    es similar a al ade arriba pero solo busca un torrent especifdico en un a
    """

    if not re.match(r"^(https?://).*", direcc):
        direcc = 'https://' + direcc

    # if modo_debug:
    #    print(direcc)

    if re.search("dontorrent", direcc):
        if bot is not None and message is not None:
            bot.reply_to(message, 'Buscando torrent en pctnew.com')

        req_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
                       'Content-Type': 'application/x-www-form-urlencoded'}

        session = requests.session()
        login = session.get(direcc, headers=req_headers, verify=False)
        sopa = BeautifulSoup(login.text, 'html.parser')
        mtable = sopa.find('a', {"class": "text-white bg-primary rounded-pill d-block shadow text-decoration-none p-1"})
        print(mtable)
        print(mtable['href'])

        return f'https://dontorrent.com{mtable["href"]}'


def feed_parser(url):
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


def show_message(label, texto='Texto plantilla', estado=True):
    """
    Muestra una determinada label con rojo o verde (depende del estado) y con el texto indicado
    """

    label.setText(texto)
    if estado:
        label.setStyleSheet('color: green')
    else:
        label.setStyleSheet('color: red')


def scapes_parenthesis(texto):
    """
    No he probado si funciona con series como powers
    """
    return texto.replace('(', '\\(').replace(')', '\\)')


def internet_on():
    try:
        session = requests.session()
        session.get('http://www.google.com', verify=False)
        return True
    except requests.exceptions.ConnectionError:
        return False