#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import NoReturn, List

from app import logger
from app.models.model_credentials import Credentials
from app.models.model_notifications import Notifications
from app.models.model_preferences import Preferences
from app.models.model_query import Query
from app.models.model_serie import Serie
from app.models.model_states import States
from app.modulos.connect_sqlite import conection_sqlite, execute_script_sqlite
from app.modulos.settings import SYNC_SQLITE


def execute_query_select(sql_query: str, database: str, to_class: object = None) -> Query:
    logger.debug(sql_query)
    response = conection_sqlite(database, sql_query, True, to_class)
    response_query = Query(sql_query, response)
    return response_query


def execute_query(sql_query: str, database: str) -> NoReturn:
    logger.debug(sql_query)
    conection_sqlite(database, sql_query, False)


def execute_query_script_sqlite(sql_query, database: str) -> NoReturn:
    logger.debug(sql_query)
    execute_script_sqlite(database, sql_query)


def get_series_all(database: str, extra: str) -> Query:
    query_str = f'''SELECT * FROM Series  {extra} '''
    return execute_query_select(query_str, database, Serie())


def get_series_follow_active(database: str) -> Query:
    query_str = '''SELECT * FROM Series  WHERE Siguiendo = "Si" AND Capitulo <> 0 AND Estado="Activa"'''
    return execute_query_select(query_str, database, Serie())


def get_series_follow(database: str) -> Query:
    query_str = '''SELECT * FROM Series WHERE Siguiendo = "Si" ORDER BY Nombre'''
    return execute_query_select(query_str, database, Serie())


def get_series_start_season(database: str) -> Query:
    query_str = '''SELECT Nombre FROM Series WHERE Estado LIKE "En Espera" AND Capitulo LIKE 0'''
    return execute_query_select(query_str, database, Serie())


def get_series_finished(database: str) -> Query:
    query_str = '''SELECT ID, Nombre, Estado, imdb_Finaliza FROM Series WHERE imdb_Finaliza <> "????" AND Capitulo 
            LIKE imdb_Capitulos AND Estado <> "Finalizada"'''
    return execute_query_select(query_str, database, Serie())


def get_series_finished_season(database: str) -> Query:
    query_str = '''SELECT ID, Nombre, Estado, imdb_Finaliza FROM Series WHERE imdb_Finaliza LIKE "????" AND Capitulo 
            LIKE imdb_Capitulos'''
    return execute_query_select(query_str, database, Serie())


def get_series_finished2(database: str) -> Query:
    query_str = '''SELECT ID, Nombre, Temporada, Capitulo, imdb_Temporada, imdb_Capitulos FROM Series WHERE Estado 
            LIKE "Finalizada" AND Acabada LIKE "Si" AND (Capitulo <> imdb_Capitulos OR Temporada <> imdb_Temporada)'''
    return execute_query_select(query_str, database, Serie())


def get_series_name(name: str, database: str) -> Query:
    query_str = f'SELECT * FROM Series WHERE Nombre LIKE "%%{name}%%"'
    return execute_query_select(query_str, database, Serie())


def get_states(database: str) -> Query:
    query_str = 'SELECT * FROM ID_Estados'
    return execute_query_select(query_str, database, States())


def get_credentials_fileconf(id_fich: str, database: str) -> Query:
    query_str = f'SELECT * FROM Configuraciones, Credenciales WHERE ID LIKE {id_fich} LIMIT 1'
    return execute_query_select(query_str, database)


def get_credentials(database: str) -> Query:
    query_str = 'SELECT * FROM Credenciales'
    return execute_query_select(query_str, database, Credentials())


def get_preferences(database: str) -> Query:
    query_str = 'SELECT * FROM Configuraciones'
    return execute_query_select(query_str, database, Preferences())


def get_preferences_id(database: str, id_db: int) -> Query:
    query_str = f'SELECT * FROM Configuraciones WHERE id IS {id_db}'
    return execute_query_select(query_str, database, Preferences())


def get_notifications(database: str) -> Query:
    query_str = 'SELECT * FROM Notificaciones'
    return execute_query_select(query_str, database, Notifications())


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


def update_series_finished(title: str, database: str) -> NoReturn:
    query_str = f'''UPDATE series SET Temporada=imdb_Temporada, Capitulo=imdb_Capitulos 
                    WHERE Nombre LIKE "{title}"'''
    execute_query(query_str, database)


def update_preferences(preferences: Preferences, database: str) -> NoReturn:
    query_str = f'''UPDATE Configuraciones SET UrlFeedNewpct="{preferences.url_feed}", 
                UrlFeedShowrss="{preferences.url_feed_vose}", RutaDescargas="{preferences.path_download}"
                WHERE ID LIKE {preferences.id}'''
    execute_query(query_str, database)


def insert_preferences(preferences: Preferences, database: str) -> NoReturn:
    query_str = f'''INSERT INTO Configuraciones(UrlFeedNewpct, UrlFeedShowrss, RutaDescargas) 
                VALUES ("{preferences.url_feed}", "{preferences.url_feed_vose}", "{preferences.path_download}")'''
    execute_query(query_str, database)


def update_notifications(notifications: List[Notifications], database: str) -> NoReturn:
    query_str: str = str()
    for notification in notifications:
        if notification.api == 'NULL' or notification.api == 'None':
            query_str += f'''\nUPDATE Notificaciones SET API=NULL, Activo="{notification.active}" 
            WHERE Nombre LIKE "{notification.name}";'''
        else:
            query_str += f'''\nUPDATE Notificaciones SET API="{notification.api}", Activo="{notification.active}" 
            WHERE Nombre LIKE "{notification.name}";'''
    execute_query_script_sqlite(query_str, database)


def get_database_configuration(database: str) -> Query:
    """
    Funcion que obtiene los valores de la configuracion de un programa, devuelve el diciconario con los datos

    :return dict: Nos devuelve un diccionario con los datos
    """

    try:
        with open(SYNC_SQLITE, 'r') as f:
            id_db = f.readline()
    except Exception:
        logger.warning('fallo en dbConfiguarion')
        id_db = 1

    response_query: Query = get_preferences_id(database, id_db)
    # response_query: Query = get_preferences_id(f'{directorio_trabajo}/{nombre_db}', id_db)
    return response_query
