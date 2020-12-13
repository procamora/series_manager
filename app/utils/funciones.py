#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import glob
import time
from pathlib import Path  # nueva forma de trabajar con rutas
from typing import List, NoReturn

import requests
import unidecode
import urllib3

import app.controller.Controller as Controller
from app import logger
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
        with open(Path(ficheros_sql[-1]), 'r') as f:
            plantilla = f.read()
        Controller.execute_query_script_sqlite(plantilla)


def create_full_backup_db() -> NoReturn:
    """
    Funcion encargada de generar backup de la base de datos y guardarlo 
    """

    data = Controller.execute_dump()
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


'''
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
'''


def show_message(label, texto='Texto plantilla', estado=True) -> NoReturn:
    """
    Muestra una determinada label con rojo o verde (depende del estado) y con el texto indicado
    """

    label.setText(texto)
    if estado:
        label.setStyleSheet('color: green')
    else:
        label.setStyleSheet('color: red')


def internet_on() -> bool:
    try:
        session = requests.session()
        session.get('http://www.google.com', verify=False)
        return True
    except requests.exceptions.ConnectionError:
        return False
