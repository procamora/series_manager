#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import logging
import os
import platform

import colorlog  # https://medium.com/@galea/python-logging-example-with-color-formatting-file-handlers-6ee21d363184

FILE_CONFIG = 'settings.conf'


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


MODE_DEBUG = True
logger = get_logger(MODE_DEBUG, 'series')

PATH_FILE_CONFIG = '{}/../../{}'.format(os.path.dirname(os.path.realpath(__file__)), FILE_CONFIG)
config = configparser.ConfigParser()
config.sections()
config.read(PATH_FILE_CONFIG)

gdrive = 0
SYSTEM = platform.system()

# opcion1 = '{}/{}'.format(os.path.dirname(os.path.realpath(__file__)), sync_gdrive)
opcion = '{}/../{}'.format(os.path.dirname(os.path.realpath(__file__)), config['DEFAULTS']['SYNC_GDRIVE'])

os.path.dirname(os.path.realpath(__file__))
if os.path.exists(opcion):
    with open(opcion, 'r') as f:
        lineas_fich = f.readlines()
        gdrive = int(lineas_fich[0].replace('\n', ''))
# elif os.path.exists(opcion2):
#    with open(opcion2, 'r') as f:
#        lineas_fich = f.readlines()
#        gdrive = int(lineas_fich[0].replace('\n', ''))

if gdrive:
    dir_drive = lineas_fich[1].replace('\n', '')

    if SYSTEM == "Windows":
        DIRECTORY_WORKING = f'{dir_drive}/{"Gestor-Series"}'
        DIRECTORY_LOCAL = os.path.dirname(os.path.realpath(__file__)).replace(
            '\\', '/').replace('/modulos', '')  # tengo que eliminar /modulos para que coga ../ y no este directorio
        # para cuando lo ejecuto con el exe
        if DIRECTORY_LOCAL.split('/')[-1] == 'library.zip':
            DIRECTORY_LOCAL += '/..'
    elif SYSTEM == "Linux":
        DIRECTORY_WORKING = f'{dir_drive}/{"Gestor-Series"}'
        DIRECTORY_LOCAL = os.path.dirname(os.path.realpath(__file__)).replace('/modulos', '')
else:
    if SYSTEM == "Windows":
        DIRECTORY_WORKING = '{}/{}'.format((os.environ["LOCALAPPDATA"]).replace("\\", "/"), "Gestor-Series")
        DIRECTORY_LOCAL = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/').replace('/modulos', '')
        # para cuando lo ejecuto con el exe
        if DIRECTORY_LOCAL.split('/')[-1] == 'library.zip':
            DIRECTORY_LOCAL += '/.2.'
    elif SYSTEM == "Linux":
        DIRECTORY_WORKING = f'{os.environ["HOME"]}/.{"Gestor-Series"}'
        DIRECTORY_LOCAL = os.path.dirname(os.path.realpath(__file__)).replace('/modulos', '')

SYNC_GDRIVE = f'{DIRECTORY_LOCAL}/{config["DEFAULTS"]["SYNC_GDRIVE"]}'
SYNC_SQLITE = f'{DIRECTORY_LOCAL}/{config["DEFAULTS"]["SYNC_SQLITE"]}'
NAME_DATABASE = config['DEFAULTS']['NOMBRE_DB']

PATH_DATABASE = f'{DIRECTORY_WORKING}/{NAME_DATABASE}'

FILE_LOG_DOWNLOADS = config['BASICS']['FILE_LOG_DOWNLOADS']
FILE_LOG_FEED = config['BASICS']['FILE_LOG_FEED']
FILE_LOG_FEED_VOSE = config['BASICS']['FILE_LOG_FEED_VOSE']

logger.debug(f'Dir local: {DIRECTORY_LOCAL}')
logger.debug(f'Dir traba: {DIRECTORY_WORKING}')
logger.debug(f'Ruta db: {PATH_DATABASE}')
