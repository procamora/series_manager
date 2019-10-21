#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import logging
import os

import colorlog  # https://medium.com/@galea/python-logging-example-with-color-formatting-file-handlers-6ee21d363184

__all__ = [os.path.basename(
    f)[:-3] for f in glob.glob(os.path.dirname(__file__) + "/*.py")]

from app.modulos.settings import MODE_DEBUG


def get_logger(verbose, name='Series'):
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
