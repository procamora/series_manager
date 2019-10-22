#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from pathlib import Path, PurePath  # nueva forma de trabajar con rutas

import colorlog  # https://medium.com/@galea/python-logging-example-with-color-formatting-file-handlers-6ee21d363184

from app.utils.settings import MODE_DEBUG

# Metodo para encontrarar todos los ficheros e importarlos
absolut_path = PurePath(__file__)  # Ruta absoluta de este fichero
# Path(absolut_path.parent)     # Obtenemos el directorio donde esta el fichero
# glob("*.py")                  # Buscamos todos los ficheros con extension py
# PurePath(str(f)).stem         # Para cada fichero solo obtenemos su nombre (sin extension y ruta)
__all__ = [PurePath(str(f)).stem for f in Path(absolut_path.parent).glob("*.py")]


def get_logger(verbose: bool, name: str = 'Series') -> logging:
    # Desabilita log de modulos
    # for _ in ("boto", "elasticsearch", "urllib3"):
    #    logging.getLogger(_).setLevel(logging.CRITICAL)

    log_format = '%(levelname)s - %(module)s - %(funcName)s - %(message)s'

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
    else:
        log.setLevel(logging.INFO)

    return log


logger = get_logger(MODE_DEBUG, 'series')
