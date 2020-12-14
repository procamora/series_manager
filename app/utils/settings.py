#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import logging
import os
import platform
from pathlib import Path, PurePath  # nueva forma de trabajar con rutas
from typing import NoReturn, Text

import colorlog  # https://medium.com/@galea/python-logging-example-with-color-formatting-file-handlers-6ee21d363184

sample_config: Text = """
# Fichero de configuracion del gestor de series
[BASICS]
NAME_DATABASE = Series.db
NAME_WORKDIR = series_manager
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
# Cliente torrent que se usara como comando para añadir enlaces magnet
IP_CLIENT_TORRENT = 127.0.0.1
PORT_CLIENT_TORRENT = 9091
USER_CLIENT_TORRENT = pi
PASS_CLIENT_TORRENT = raspberry
CLIENT_TORRENT = transmission-remote ${IP_CLIENT_TORRENT}:${PORT_CLIENT_TORRENT} --auth=${USER_CLIENT_TORRENT}:${PASS_CLIENT_TORRENT}

[BOT]
BOT_TOKEN = 1069111113:AAHOk9K5TAAAAAAAAAAIY1OgA_LNpAAAAA
ADMIN = 1111111

[DEBUG]
BOT_TOKEN = 1069111113:AAHOk9K5TAAAAAAAAAAIY1OgA_LNpAAAAA
ADMIN = 1111111
BOT_DEBUG = 0
"""

FILE_CONFIG: Text = 'settings.cfg'


def get_logger(verbose: bool, name: str = 'Series') -> logging:
    log_format: Text = '%(levelname)s - %(module)s - %(message)s'

    bold_seq: Text = '\033[1m'
    colorlog_format: Text = (
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


def write_config(new_config: configparser.ConfigParser) -> NoReturn:
    """
    Metodo para escribir en el fichero de configuracion una nueva configuracion
    :param new_config:
    :return:
    """
    with open(PATH_FILE_CONFIG, 'w') as configfile:
        print("escribo en settings")
        new_config.write(configfile)


MODE_DEBUG: bool = True
logger: logging = get_logger(MODE_DEBUG, 'series')

absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
# print(absolut_path.parent)# ruta adsoluta del directorio donde esta el fichero
# retroceder 2 niveles para la raiz del proyecto
# PATH_FILE_CONFIG: Path = Path(f'{absolut_path.parent}/../../{FILE_CONFIG}')
PATH_FILE_CONFIG: Path = Path(absolut_path.parent, "../../", FILE_CONFIG)
logger.debug(PATH_FILE_CONFIG)

config: configparser.ConfigParser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())

if Path(PATH_FILE_CONFIG).exists():
    config.read(PATH_FILE_CONFIG)
else:
    config.read_string(sample_config)
    write_config(config)

basics = config["BASICS"]
configurable = config["CONFIGURABLE"]

SYSTEM: Text = platform.system()

# opcion: Path = Path('{}/../{}'.format(os.path.dirname(os.path.realpath(__file__)), config['DEFAULTS']['SYNC_GDRIVE']))

# Inicializacion
DIRECTORY_WORKING: Path
DIRECTORY_LOCAL: Path = Path(absolut_path.parent, '../')
logger.debug(absolut_path.parent)
logger.debug(DIRECTORY_LOCAL)

# directorio personalizado
if not configurable.getboolean('WORKDIR_DEFAULT'):
    dir_drive: Text = configurable.get('WORKDIR')  # lineas_fich[1].replace('\n', '')
    DIRECTORY_WORKING: Path = Path(dir_drive, basics.get("NAME_WORKDIR"))
    if SYSTEM == "Windows":
        # tengo que eliminar /modulos para que coga ../ y no este directorio
        # para cuando lo ejecuto con el exe
        # if DIRECTORY_LOCAL.split('/')[-1] == 'library.zip':
        if str(DIRECTORY_LOCAL.name) == 'library.zip':  # fixme funciona bien??
            DIRECTORY_LOCAL += '/..'


# directorio por defecto
else:
    if SYSTEM == "Windows":
        DIRECTORY_WORKING: Path = Path(os.environ["LOCALAPPDATA"], basics.get("NAME_WORKDIR"))
        # para cuando lo ejecuto con el exe
        # if DIRECTORY_LOCAL.split('/')[-1] == 'library.zip':
        if str(DIRECTORY_LOCAL.name) == 'library.zip':  # fixme funciona bien??
            DIRECTORY_LOCAL += '/.2.'
    else:
        DIRECTORY_WORKING = Path(os.environ["HOME"], basics.get("NAME_WORKDIR"))

# CLIENT TORRENT
CLIENT_TORRENT: Text = configurable.get('CLIENT_TORRENT')

# BASE DE DATOS
DATABASE_ID: int = configurable.getint("DATABASE_ID")
PATH_DATABASE: Path = Path(DIRECTORY_WORKING, basics["NAME_DATABASE"])

# DEFINICION DE DIRECTORIO DE LOGS con sus ficheros
directory_logs: Path = Path(DIRECTORY_WORKING, 'log')
FILE_LOG_DOWNLOADS: Path = Path(directory_logs, basics['FILE_LOG_DOWNLOADS'])
FILE_LOG_FEED: Path = Path(directory_logs, basics['FILE_LOG_FEED'])
FILE_LOG_FEED_VOSE: Path = Path(directory_logs, basics['FILE_LOG_FEED_VOSE'])
if not directory_logs.exists():  # Si no existe directorio se crea junto con los ficheros
    Path.mkdir(directory_logs)
    FILE_LOG_DOWNLOADS.write_text("")
    FILE_LOG_FEED.write_text("")
    FILE_LOG_FEED_VOSE.write_text("")

# BOT
BOT_TOK: Text = config["BOT"].get('BOT_TOKEN')
BOT_ADMIN: int = int(config["BOT"].get('ADMIN'))

BOT_DEBUG: bool = bool(int(config["DEBUG"].get('BOT_DEBUG')))
BOT_TOK_DEBUG: Text = config["DEBUG"].get('BOT_TOKEN')

logger.debug(f'DIRECTORY_LOCAL: {DIRECTORY_LOCAL}')
logger.debug(f'DIRECTORY_WORKING: {DIRECTORY_WORKING}')
logger.debug(f'PATH_DATABASE: {PATH_DATABASE}')

logger.debug(f'FILE_LOG_DOWNLOADS: {FILE_LOG_DOWNLOADS}')
logger.debug(f'FILE_LOG_FEED: {FILE_LOG_FEED}')
logger.debug(f'FILE_LOG_FEED_VOSE: {FILE_LOG_FEED_VOSE}')

logger.debug(f'DATABASE_ID: {DATABASE_ID}')
logger.debug(f'CLIENT_TORRENT: {CLIENT_TORRENT}')

REQ_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
               'Content-Type': 'application/x-www-form-urlencoded'}
