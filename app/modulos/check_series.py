#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import List

try:  # Ejecucion desde Series.py
    from .connect_sqlite import conection_sqlite, execute_script_sqlite
    from .settings import modo_debug, ruta_db
    from app import logger
except ModuleNotFoundError as e:  # Ejecucion local
    new_path = '../../'
    if new_path not in sys.path:
        sys.path.append(new_path)
    from app import logger

    logger.debug(e)
    from app.modulos.connect_sqlite import conection_sqlite, execute_script_sqlite
    from app.modulos.settings import modo_debug, ruta_db


def finished(write: bool = False) -> str:
    queryAcabada = 'SELECT * FROM Series WHERE Acabada LIKE "Si" AND Estado <> "Finalizada"'
    query = conection_sqlite(ruta_db, queryAcabada, True)
    update = 'UPDATE Series SET Estado="Finalizada" WHERE Nombre LIKE "{}";\n'

    queryUpdate = make_update(query, update, write)

    return queryUpdate


def imdb(write: bool = False) -> str:
    """
    Busca las series que tienen una fecha de finalizacion en imdb pero sigo intentando actualizarlas
    """
    queryImdb = 'SELECT * FROM Series WHERE imdb_finaliza <> "????" AND imdb_seguir LIKE "Si"'
    query = conection_sqlite(ruta_db, queryImdb, True)
    update = 'UPDATE Series SET imdb_seguir="No" WHERE Nombre LIKE "{}";\n'

    queryUpdate = make_update(query, update, write)

    return queryUpdate


def make_update(query: List, update: str, write: bool = False) -> str:
    """
    Recibe una lista con los resultados de los datos a cambiar, y el update a falta del nombre
    """
    queryUpdate = str()
    for i in query:
        update.format(i['Nombre'])
        queryUpdate += update

    logger.debug(queryUpdate)

    if write and len(queryUpdate) != 0:
        logger.info('ejecutar script')
        execute_script_sqlite(ruta_db, queryUpdate)

    return queryUpdate


if __name__ == '__main__':
    # logger.info(finished(write=False))
    # logger.info(imdb(write=False))
    pass
