#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:  # Ejecucion desde Series.py
    from .connect_sqlite import conectionSQLite, ejecutaScriptSqlite
    from .settings import modo_debug, ruta_db
except:  # Ejecucion local
    from app.modulos.connect_sqlite import conectionSQLite, ejecutaScriptSqlite
    from app.modulos.settings import modo_debug, ruta_db

from app import logger

def acabada(write=False):
    queryAcabada = 'SELECT * FROM Series WHERE Acabada LIKE "Si" AND Estado <> "Finalizada"'
    query = conectionSQLite(ruta_db, queryAcabada, True)
    update = 'UPDATE Series SET Estado="Finalizada" WHERE Nombre LIKE "{}";\n'

    queryUpdate = makeUpdate(query, update, write)

    return queryUpdate


def imdb(write=False):
    """
    Busca las series que tienen una fecha de finalizacion en imdb pero sigo intentando actualizarlas
    """
    queryImdb = 'SELECT * FROM Series WHERE imdb_finaliza <> "????" AND imdb_seguir LIKE "Si"'
    query = conectionSQLite(ruta_db, queryImdb, True)
    update = 'UPDATE Series SET imdb_seguir="No" WHERE Nombre LIKE "{}";\n'

    queryUpdate = makeUpdate(query, update, write)

    return queryUpdate


def makeUpdate(query, update, write=False):
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
        ejecutaScriptSqlite(ruta_db, queryUpdate)

    return queryUpdate


if __name__ == '__main__':
    logger.info(acabada(write=False))
    logger.info(imdb(write=False))
