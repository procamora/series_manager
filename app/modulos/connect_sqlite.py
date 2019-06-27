#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3


def conectionSQLite(db, query, dict=False, toClass=None) -> list:
    if os.path.exists(db):
        conn = sqlite3.connect(db)
        if dict:
            conn.row_factory = __dictFactory
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
        if toClass is not None:
            for i in data:
                a = toClass.__class__
                response.append(a.load(i))
            return response

        return data


def __dictFactory(cursor, row) -> dict:
    d = dict()
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def ejecutaScriptSqlite(db, script) -> None:
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.executescript(script)
    conn.commit()
    cursor.close()
    conn.close()


def dumpDatabase(db) -> str:
    """
    Hace un dump de la base de datos y lo retorna
    :param db: ruta de la base de datos
    :return dump: volcado de la base de datos 
    """
    if os.path.exists(db):
        con = sqlite3.connect(db)
        return '\n'.join(con.iterdump())
