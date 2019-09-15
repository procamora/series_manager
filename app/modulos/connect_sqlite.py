#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
from typing import Dict, Union, Iterable, List


def conection_sqlite(db: str, query: str, is_dict: bool = False, to_class:object=None) -> List:
    if os.path.exists(db):
        conn = sqlite3.connect(db)
        if is_dict:
            conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute(query)

        if query.upper().startswith('SELECT'):
            data = cursor.fetchall()  # Traer los resultados de un select
        else:
            conn.commit()  # Hacer efectiva la escritura de datos
            data = None

        cursor.close()
        conn.close()

        response = list()
        if to_class is not None:
            for i in data:
                a = to_class.__class__
                response.append(a.load(i))
            return response

        return data


def dict_factory(cursor, row) -> Dict:
    d = dict()
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def execute_script_sqlite(db: str, script: str) -> None:
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.executescript(script)
    conn.commit()
    cursor.close()
    conn.close()


def dump_database(db: str) -> Union[Iterable[str], None]:
    """
    Hace un dump de la base de datos y lo retorna
    :param db: ruta de la base de datos
    :return dump: volcado de la base de datos 
    """
    if os.path.exists(db):
        con = sqlite3.connect(db)
        return '\n'.join(con.iterdump())
