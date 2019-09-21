#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import List, Dict

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
    query_finished = 'SELECT * FROM Series WHERE Acabada LIKE "Si" AND Estado <> "Finalizada"'
    response_query = conection_sqlite(ruta_db, query_finished, True)
    update = 'UPDATE Series SET Estado="Finalizada" WHERE Nombre LIKE "{}";\n'

    query_update = make_update(response_query, update, write)
    return query_update


def imdb(write: bool = False) -> str:
    """
    Busca las series que tienen una fecha de finalizacion en imdb pero sigo intentando actualizarlas
    """
    query_imdb = 'SELECT * FROM Series WHERE imdb_finaliza <> "????" AND imdb_seguir LIKE "Si"'
    query_response = conection_sqlite(ruta_db, query_imdb, True)
    update = 'UPDATE Series SET imdb_seguir="No" WHERE Nombre LIKE "{}";\n'

    query_update = make_update(query_response, update, write)
    return query_update


def make_update(query: List[Dict], update: str, write: bool = False) -> str:
    """
    Recibe una lista con los resultados de los datos a cambiar, y el update a falta del nombre
    """
    query_update_str = str()
    for i in query:
        update.format(i['Nombre'])
        query_update_str += update

    logger.debug(query_update_str)

    if write and len(query_update_str) != 0:
        logger.info('ejecutar script')
        execute_script_sqlite(ruta_db, query_update_str)

    return query_update_str


if __name__ == '__main__':
    # logger.info(finished(write=False))
    # logger.info(imdb(write=False))
    pass
