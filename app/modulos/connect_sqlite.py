#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
from typing import Dict, List, Tuple, Optional, Union, NoReturn


# fixme cambiar de orden database y query
def conection_sqlite(database: str, query_str: str, is_dict: bool = False, to_class: object = None) -> \
        Union[List[List], List[object], List[Dict[str, object]], NoReturn]:
    try:
        data = None
        if os.path.exists(database):
            conn = sqlite3.connect(database)
            if is_dict:
                conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute(query_str)

            if query_str.upper().startswith('SELECT'):
                data = cursor.fetchall()  # Traer los resultados de un select
            else:
                conn.commit()  # Hacer efectiva la escritura de datos

            cursor.close()
            conn.close()

        response = list()
        if to_class is not None:
            for i in data:
                a = to_class.__class__
                # fixme usar introspeccion para confirmar que tiene el metodo load
                response.append(a.load(i))
            return response
        return data
    except sqlite3.OperationalError as e:
        print(f'LOCK "{query_str}", sorry...')
        print(e)
        return None


def dict_factory(cursor: sqlite3.Cursor, row: Tuple[str]) -> Dict[str, str]:
    d = dict()
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def execute_script_sqlite(database: str, script: str) -> None:
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.executescript(script)
    conn.commit()
    cursor.close()
    conn.close()


def dump_database(db: str) -> Optional[str]:
    """
    Hace un dump de la base de datos y lo retorna
    :param db: ruta de la base de datos
    :return dump: volcado de la base de datos 
    """
    if os.path.exists(db):
        con = sqlite3.connect(db)
        return '\n'.join(con.iterdump())
    return None
