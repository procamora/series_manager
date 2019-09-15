#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import NoReturn

from app.models.model_query import Query
from app.models.model_serie import Serie
from app.modulos.connect_sqlite import conection_sqlite, execute_script_sqlite
# from app import logger


def execute_query(sql_query: str, database: str, to_class: object = None) -> Query:
    response = conection_sqlite(database, sql_query, True, to_class)
    response_query = Query(sql_query, response)
    return response_query


def execute_query_script_sqlite(sql_query, database: str) -> NoReturn:
    execute_script_sqlite(database, sql_query)


def get_all_series(database: str) -> Query:
    query = '''SELECT Nombre, Temporada, Capitulo, Dia, Capitulo_Descargado FROM Series 
                    WHERE Siguiendo = "Si" AND Capitulo <> 0 AND Estado="Activa"'''
    return execute_query(query, database, Serie())


def get_credentials(id_fich: str, database: str) -> Query:
    query = 'SELECT * FROM Configuraciones, Credenciales WHERE ID LIKE {} LIMIT 1'.format(id_fich)
    return execute_query(query, database)
