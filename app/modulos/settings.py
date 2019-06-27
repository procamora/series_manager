#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import logging
import os
import platform

import colorlog  # https://medium.com/@galea/python-logging-example-with-color-formatting-file-handlers-6ee21d363184

FILE_CONFIG = 'settings.conf'


def getLogger(verbose, name='Series'):
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


modo_debug = True
logger = getLogger(modo_debug, 'series')

PATH_FILE_CONFIG = '{}/../../{}'.format(os.path.dirname(os.path.realpath(__file__)), FILE_CONFIG)
config = configparser.ConfigParser()
config.sections()
config.read(PATH_FILE_CONFIG)

gdrive = 0
sistema = platform.system()

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

    if sistema == "Windows":
        directorio_trabajo = '{}/{}'.format(dir_drive, 'Gestor-Series')
        directorio_local = os.path.dirname(os.path.realpath(__file__)).replace(
            '\\', '/').replace('/modulos', '')  # tengo que eliminar /modulos para que coga ../ y no este directorio
        # para cuando lo ejecuto con el exe
        if directorio_local.split('/')[-1] == 'library.zip':
            directorio_local += '/..'
    elif sistema == "Linux":
        directorio_trabajo = '{}/{}'.format(dir_drive, 'Gestor-Series')
        directorio_local = os.path.dirname(
            os.path.realpath(__file__)).replace('/modulos', '')
else:
    if sistema == "Windows":
        directorio_trabajo = '{}/{}'.format(
            (os.environ['LOCALAPPDATA']).replace('\\', '/'), 'Gestor-Series')
        directorio_local = os.path.dirname(os.path.realpath(__file__)).replace(
            '\\', '/').replace('/modulos', '')
        # para cuando lo ejecuto con el exe
        if directorio_local.split('/')[-1] == 'library.zip':
            directorio_local += '/.2.'
    elif sistema == "Linux":
        directorio_trabajo = '{}/.{}'.format(
            os.environ['HOME'], 'Gestor-Series')
        directorio_local = os.path.dirname(
            os.path.realpath(__file__)).replace('/modulos', '')

sync_gdrive = '{}/{}'.format(directorio_local, config['DEFAULTS']['SYNC_GDRIVE'])
sync_sqlite = '{}/{}'.format(directorio_local, config['DEFAULTS']['SYNC_SQLITE'])
nombre_db = config['DEFAULTS']['NOMBRE_DB']

ruta_db = '{}/{}'.format(directorio_trabajo, nombre_db)

logger.debug('Dir local: {}'.format(directorio_local))
logger.debug('Dir traba: {}'.format(directorio_trabajo))
logger.debug('Ruta db: {}'.format(ruta_db))
