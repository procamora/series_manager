#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import logging
import os
import platform
from pathlib import Path, PurePath  # nueva forma de trabajar con rutas

import colorlog  # https://medium.com/@galea/python-logging-example-with-color-formatting-file-handlers-6ee21d363184

sample_config = """
# Fichero de configuracion del gestor de series
[BASICS]
NAME_DATABASE = Series.db
NAME_WORKDIR = Gestor-Series
FILE_LOG_DOWNLOADS = descargas.log
FILE_LOG_FEED = feedNewpct.log
FILE_LOG_FEED_VOSE = feedShowrss.log

[CONFIGURABLE]
# Identificador que se usa para acceder a las preferencias de la base de datos donde se tienen las rutas de trabajo
DATABASE_ID = 1
# No distinge entre mayusculas y minusculas, si esta en false usa como directorio para la base de datos
# el directorio marcado en WORKDIR, si esta en True en windows usa %appdata% y en linux $HOME
WORKDIR_DEFAULT = True
# No se usa por defecto
WORKDIR = /tmp/
"""

FILE_CONFIG = 'settings.ini'


def get_logger(verbose, name='Series'):
    log_format = '%(levelname)s - %(module)s - %(message)s'

    bold_seq = '\033[1m'
    colorlog_format = (
        f'{bold_seq} '
        '%(log_color)s '
        f'{log_format}'
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


MODE_DEBUG: bool = True
logger = get_logger(MODE_DEBUG, 'series')

absolut_path = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
# print(absolut_path.parent)# ruta adsoluta del directorio donde esta el fichero
# retroceder 2 niveles para la raiz del proyecto
PATH_FILE_CONFIG: Path = Path('{}/../../{}'.format(absolut_path.parent, FILE_CONFIG))
print(PATH_FILE_CONFIG)

config = configparser.ConfigParser()

if Path(PATH_FILE_CONFIG).exists():
    config.read(PATH_FILE_CONFIG)
else:
    config.read_string(sample_config)
    with open(FILE_CONFIG, 'w') as configfile:
        print("escribo en settings")
        config.write(configfile)

basics = config["BASICS"]
configurable = config["CONFIGURABLE"]

SYSTEM: str = platform.system()

# opcion: Path = Path('{}/../{}'.format(os.path.dirname(os.path.realpath(__file__)), config['DEFAULTS']['SYNC_GDRIVE']))

# Inicializacion
DIRECTORY_WORKING: Path
DIRECTORY_LOCAL: Path = Path(str(absolut_path.parent) + '/../')

# directorio personalizado
if not configurable.getboolean('WORKDIR_DEFAULT'):
    dir_drive = configurable.get('WORKDIR')  # lineas_fich[1].replace('\n', '')
    DIRECTORY_WORKING = Path(f'{dir_drive}/{basics.get("NAME_WORKDIR")}')
    if SYSTEM == "Windows":
        # tengo que eliminar /modulos para que coga ../ y no este directorio
        # para cuando lo ejecuto con el exe
        # if DIRECTORY_LOCAL.split('/')[-1] == 'library.zip':
        if str(DIRECTORY_LOCAL.name) == 'library.zip':  # fixme funciona bien??
            DIRECTORY_LOCAL += '/..'


# directorio por defecto
else:
    if SYSTEM == "Windows":
        DIRECTORY_WORKING = Path(f'{os.environ["LOCALAPPDATA"]}/{basics.get("NAME_WORKDIR")}')
        # para cuando lo ejecuto con el exe
        # if DIRECTORY_LOCAL.split('/')[-1] == 'library.zip':
        if str(DIRECTORY_LOCAL.name) == 'library.zip':  # fixme funciona bien??
            DIRECTORY_LOCAL += '/.2.'
    else:
        DIRECTORY_WORKING = Path(f'{os.environ["HOME"]}/.{basics.get("NAME_WORKDIR")}')

DATABASE_ID: int = configurable.getint("DATABASE_ID")

PATH_DATABASE: Path = Path(f'{DIRECTORY_WORKING}/{basics["NAME_DATABASE"]}')

FILE_LOG_DOWNLOADS: str = basics['FILE_LOG_DOWNLOADS']
FILE_LOG_FEED: str = basics['FILE_LOG_FEED']
FILE_LOG_FEED_VOSE: str = basics['FILE_LOG_FEED_VOSE']

logger.debug(f'DIRECTORY_LOCAL: {DIRECTORY_LOCAL}')
logger.debug(f'DIRECTORY_WORKING: {DIRECTORY_WORKING}')
logger.debug(f'PATH_DATABASE: {PATH_DATABASE}')
