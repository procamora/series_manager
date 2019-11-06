#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from pathlib import Path  # nueva forma de trabajar con rutas
from typing import NoReturn, List, Optional, Tuple

from app import logger
from app.models.model_credentials import Credentials
from app.models.model_notifications import Notifications
from app.models.model_preferences import Preferences
from app.models.model_query import Query
from app.models.model_serie import Serie
from app.models.model_serie_imdb import SerieImdb
from app.models.model_states import States
from app.utils.connect_sqlite import conection_sqlite, execute_script_sqlite, dump_database
from app.utils.settings import DATABASE_ID, PATH_DATABASE, MODE_DEBUG


def format_text(param_text: bytes) -> Optional[str]:
    if param_text is not None:
        text = param_text.decode('utf-8')
        return str(text)
        # return text.replace('\n', '')
    return param_text


def execute_command(command: str) -> Tuple[str, str, subprocess.Popen]:
    execute = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = execute.communicate()
    return format_text(stdout), format_text(stderr), execute


def execute_query_select(sql_query: str, database: Path, to_class: object = None) -> Query:
    logger.debug(sql_query)
    response = conection_sqlite(database, sql_query, True, to_class)
    response_query = Query(sql_query, response)
    return response_query


def execute_query(sql_query: str, database: Path) -> NoReturn:
    logger.debug(sql_query)
    conection_sqlite(database, sql_query, False)


def execute_dump() -> Optional[str]:
    return dump_database(PATH_DATABASE)


def execute_query_script_sqlite(sql_query, database: Path = None) -> NoReturn:
    logger.debug(sql_query)
    if database is None:
        database = PATH_DATABASE
    execute_script_sqlite(database, sql_query)


def get_series_all(extra: str) -> Query:
    query_str = f'''SELECT * FROM Series  {extra} '''
    return execute_query_select(query_str, PATH_DATABASE, Serie())


def get_series_follow_active() -> Query:
    query_str = '''SELECT * FROM Series  WHERE Siguiendo = "Si" AND Capitulo <> 0 AND Estado="Activa"'''
    return execute_query_select(query_str, PATH_DATABASE, Serie())


def get_series_follow() -> Query:
    query_str = '''SELECT * FROM Series WHERE Siguiendo = "Si" ORDER BY Nombre'''
    return execute_query_select(query_str, PATH_DATABASE, Serie())


def get_series_start_season() -> Query:
    query_str = '''SELECT Nombre FROM Series WHERE Estado LIKE "En Espera" AND Capitulo LIKE 0'''
    return execute_query_select(query_str, PATH_DATABASE, Serie())


def get_series_finished() -> Query:
    query_str = '''SELECT ID, Nombre, Estado, imdb_Finaliza FROM Series WHERE imdb_Finaliza <> "????" AND Capitulo 
            LIKE imdb_Capitulos AND Estado <> "Finalizada"'''
    return execute_query_select(query_str, PATH_DATABASE, Serie())


def get_series_finished_season() -> Query:
    query_str = '''SELECT ID, Nombre, Estado, imdb_Finaliza FROM Series WHERE imdb_Finaliza LIKE "????" AND Capitulo 
            LIKE imdb_Capitulos'''
    return execute_query_select(query_str, PATH_DATABASE, Serie())


def get_series_finished2() -> Query:
    query_str = '''SELECT ID, Nombre, Temporada, Capitulo, imdb_Temporada, imdb_Capitulos FROM Series WHERE Estado 
            LIKE "Finalizada" AND Acabada LIKE "Si" AND (Capitulo <> imdb_Capitulos OR Temporada <> imdb_Temporada)'''
    return execute_query_select(query_str, PATH_DATABASE, Serie())


def get_series_name(name: str) -> Query:
    query_str = f'SELECT * FROM Series WHERE Nombre LIKE "%%{name}%%"'
    return execute_query_select(query_str, PATH_DATABASE, Serie())


def get_series_finished_imdb() -> Query:
    query_str = 'SELECT * FROM Series Where Estado LIKE "Finalizada" AND imdb_seguir LIKE "Si"'
    return execute_query_select(query_str, PATH_DATABASE, Serie())


def get_series_completed_imdb() -> Query:
    query_str = 'SELECT * FROM Series WHERE imdb_seguir LIKE "Si" AND (imdb_id IS NULL OR imdb_Finaliza IS NULL) AND ' \
                'NOT imdb_id IS NULL'  # para nuevas series con mod completa
    return execute_query_select(query_str, PATH_DATABASE, Serie())


def get_series_following_imdb() -> Query:
    query_str = 'SELECT * FROM Series WHERE imdb_Finaliza LIKE "????" AND imdb_seguir LIKE "Si" ORDER BY Nombre'
    return execute_query_select(query_str, PATH_DATABASE, Serie())


def get_states() -> Query:
    query_str = 'SELECT * FROM ID_Estados'
    return execute_query_select(query_str, PATH_DATABASE, States())


def get_credentials_fileconf() -> Query:
    query_str = f'SELECT * FROM Configuraciones, Credenciales WHERE ID LIKE {DATABASE_ID} LIMIT 1'
    return execute_query_select(query_str, PATH_DATABASE)


def get_credentials() -> Query:
    query_str = 'SELECT * FROM Credenciales LIMIT 1'
    response_query = execute_query_select(query_str, PATH_DATABASE, Credentials())
    if not response_query.is_empty() and MODE_DEBUG:
        # bot de pruebas
        response_query.response[0].api_telegram = '694076475:AAFfiSVSnuf387hnvJOIjQOHP6w7veZbO-M'
    return response_query


def get_preferences() -> Query:
    query_str = 'SELECT * FROM Configuraciones'
    return execute_query_select(query_str, PATH_DATABASE, Preferences())


def get_preferences_id(id_preferences: int = None) -> Query:
    if id_preferences is None:
        id_preferences = DATABASE_ID
    query_str = f'SELECT * FROM Configuraciones WHERE id IS {id_preferences}'
    return execute_query_select(query_str, PATH_DATABASE, Preferences())


def get_notifications() -> Query:
    query_str = 'SELECT * FROM Notificaciones'
    return execute_query_select(query_str, PATH_DATABASE, Notifications())


def get_query_update_serie(serie: Serie, title_original: str) -> NoReturn:
    return f'''UPDATE series SET Nombre="{serie.title}", Temporada={serie.season}, 
                    Capitulo={serie.chapter}, Siguiendo="{serie.following}", Dia="{serie.day}", VOSE="{serie.vose}", 
                    Acabada="{serie.finished}", Estado="{serie.state}",imdb_id={serie.imdb_id} 
                    WHERE Nombre="{title_original}"'''


def get_query_insert_serie(serie: Serie) -> NoReturn:
    return f'''INSERT INTO series(Nombre, Temporada, Capitulo, Siguiendo, Dia, VOSE, Acabada, Estado, 
                    imdb_id) VALUES ("{serie.title}", {serie.season}, {serie.chapter}, "{serie.following}", 
                    "{serie.day}", "{serie.vose}", "{serie.finished}", "{serie.state}", {serie.imdb_id})'''


def update_list_series(series: List[str], finished_season: bool, begins: bool, wait: bool, finished: bool) -> str:
    query_str: str = str()
    for title in series:
        if finished_season:
            query_str += f'''UPDATE series SET Temporada=Temporada+1, Capitulo="00", Estado="En Espera" WHERE Nombre
                LIKE "{title}";\n'''
        elif begins:
            query_str += f'UPDATE series SET Capitulo="01", Estado="Activa" WHERE Nombre LIKE "{title}";\n'
        elif wait:
            query_str += f'UPDATE series SET Estado="Pausada" WHERE Nombre LIKE "{title}";\n'
        elif finished:
            query_str += f'UPDATE series SET Estado="Finalizada", Acabada="Si" WHERE Nombre LIKE "{title}";\n'
    return query_str


def update_series_finished(title: str) -> NoReturn:
    query_str = f'''UPDATE series SET Temporada=imdb_Temporada, Capitulo=imdb_Capitulos 
                    WHERE Nombre LIKE "{title}"'''
    execute_query(query_str, PATH_DATABASE)


def update_serie_imdb(imdb: SerieImdb):
    query_str = f'UPDATE series SET imdb_Temporada="{imdb.season}", imdb_Finaliza="{imdb.year}", ' \
                f'imdb_Capitulos="{imdb.chapter}" WHERE imdb_id Like "{imdb.id}"'
    logger.info(query_str)
    execute_query(query_str, PATH_DATABASE)


def update_serie_partial_imdb(imdb: SerieImdb):
    query_str = f'UPDATE series SET imdb_Temporada="{imdb.season}", imdb_Finaliza="{imdb.year}" ' \
                f'WHERE imdb_id Like "{imdb.id}"'
    logger.info(query_str)
    execute_query(query_str, PATH_DATABASE)


def update_series_finished_imdb() -> NoReturn:
    """
    busca las series finalizadas que tienen el imdb_seguir a si y lo actualiza a no para
    hacer mas rapidas las futuras actualizaciones
    """
    response_query: Query = get_series_finished_imdb()
    query_all: str = str()

    for serie in response_query.response:
        query = f'UPDATE series SET imdb_seguir="No" WHERE Nombre LIKE "{serie["Nombre"]}";'
        query_all += '\n' + query

    # logger.info(queryCompleta)
    execute_script_sqlite(PATH_DATABASE, query_all)


def update_preferences(preferences: Preferences) -> NoReturn:
    query_str = f'''UPDATE Configuraciones SET UrlFeedNewpct="{preferences.url_feed}", 
                UrlFeedShowrss="{preferences.url_feed_vose}", RutaDescargas="{preferences.path_download}"
                WHERE ID LIKE {preferences.id}'''
    execute_query(query_str, PATH_DATABASE)


def insert_preferences(preferences: Preferences) -> NoReturn:
    query_str = f'''INSERT INTO Configuraciones(UrlFeedNewpct, UrlFeedShowrss, RutaDescargas) 
                VALUES ("{preferences.url_feed}", "{preferences.url_feed_vose}", "{preferences.path_download}")'''
    execute_query(query_str, PATH_DATABASE)


def update_notifications(notifications: List[Notifications]) -> NoReturn:
    query_str: str = str()
    for notification in notifications:
        if notification.api == 'NULL' or notification.api == 'None':
            query_str += f'''\nUPDATE Notificaciones SET API=NULL, Activo="{notification.active}" 
            WHERE Nombre LIKE "{notification.name}";'''
        else:
            query_str += f'''\nUPDATE Notificaciones SET API="{notification.api}", Activo="{notification.active}" 
            WHERE Nombre LIKE "{notification.name}";'''
    execute_query_script_sqlite(query_str, PATH_DATABASE)


def get_database_configuration() -> Query:
    """
    Funcion que obtiene los valores de la configuracion de un programa, devuelve el diciconario con los datos

    :return dict: Nos devuelve un diccionario con los datos
    """

    response_query: Query = get_preferences_id()
    # Si falla al obtener datos para el id indicado obtenemos la primera fila
    if response_query.is_empty():
        return get_preferences_id(1)
    # response_query: Query = get_preferences_id(f'{directorio_trabajo}/{nombre_db}', id_db)
    return response_query
