#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import PurePath  # nueva forma de trabajar con rutas
from typing import List, Dict

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: str = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

from app import logger
from app.utils.settings import PATH_DATABASE
import app.controller.Controller as Controller


def finished(write: bool = False) -> str:
    query_finished = 'SELECT * FROM Series WHERE Acabada LIKE "Si" AND Estado <> "Finalizada"'
    response_query = conection_sqlite(PATH_DATABASE, query_finished, True)
    update = 'UPDATE Series SET Estado="Finalizada" WHERE Nombre LIKE "{}";\n'

    query_update = make_update(response_query, update, write)
    return query_update


def imdb(write: bool = False) -> str:
    """
    Busca las series que tienen una fecha de finalizacion en imdb pero sigo intentando actualizarlas
    """
    query_imdb = 'SELECT * FROM Series WHERE imdb_finaliza <> "????" AND imdb_seguir LIKE "Si"'
    query_response = conection_sqlite(PATH_DATABASE, query_imdb, True)
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
        Controller.execute_query_script_sqlite(query_update_str)

    return query_update_str


if __name__ == '__main__':
    # logger.info(finished(write=False))
    # logger.info(imdb(write=False))
    pass
