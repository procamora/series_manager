#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys

import requests
from imdbpie import Imdb

try:  # Ejecucion desde Series.py
    from .connect_sqlite import conection_sqlite, execute_script_sqlite
    from .settings import MODE_DEBUG, PATH_DATABASE
    from app import logger
except ModuleNotFoundError as e:  # Ejecucion local
    new_path = '../../'
    if new_path not in sys.path:
        sys.path.append(new_path)
    from app import logger

    logger.debug(e)
    from app.modulos.connect_sqlite import conection_sqlite, execute_script_sqlite
    from app.modulos.settings import MODE_DEBUG, PATH_DATABASE

from Controller import get_database_configuration


class UpdateImdb:
    def __init__(self):
        self.imdb = Imdb()
        self.nombre_db = PATH_DATABASE
        self.preferences = get_database_configuration(self.nombre_db)
        # self.imdb = Imdb(cache=True, cache_dir='/tmp/imdbpie-cache-here', anonymize=False)

    @staticmethod
    def check_data(data, series):
        if str(series['imdb_Temporada']) == data['Temp'] and str(series['imdb_Finaliza']) == data['year'] and str(
                series['imdb_Capitulos']) == data['Cap']:
            return True
        else:
            return False

    @staticmethod
    def check_data_partial(data, series):
        if str(series['imdb_Temporada']) == data['Temp'] and str(series['imdb_Finaliza']) == data['year']:
            return True
        else:
            return False

    @staticmethod
    def search_chapter(id_imdb):
        # Para buscar el capitulo en vez de coger el la primera temporada, coger la ultima
        # problema de que la ultima temporada no este completa
        url = f'http://www.imdb.com/title/{id_imdb}/episodes?season=1'
        session = requests.session()
        html = session.get(url, verify=True).text
        a = re.findall('S1, Ep[0-9]+', html)
        return re.findall('[0-9]+', a[-1])[-1]

    def _update_serie(self, data):
        query = f'''UPDATE series SET imdb_Temporada="{data['Temp']}", imdb_Finaliza="{data['year']}", 
        imdb_Capitulos="{data['Cap']}" WHERE imdb_id Like "{data['id_imdb']}"'''
        conection_sqlite(self.nombre_db, query)
        logger.info(query)

    def _update_serie_partial(self, data):
        query = f'''UPDATE series SET imdb_Temporada="{data['Temp']}", imdb_Finaliza="{data['year']}" 
                    WHERE imdb_id Like "{data['id_imdb']}"'''
        conection_sqlite(self.nombre_db, query)
        logger.info(query)

    def update_season(self):  # tarda mucho
        # para actualizar_insertar series con mod parcial
        query = 'SELECT * FROM Series WHERE imdb_Finaliza LIKE "????" AND imdb_seguir LIKE "Si" ORDER BY Nombre'
        series = conection_sqlite(self.nombre_db, query, True)

        for i in series:
            try:
                logger.info(i['Nombre'])
                title = self.imdb.get_title_by_id(i['imdb_id'])

                if title.data['seasons'][-1] == 'unknown':  # en algunas series la ultima temporada pone unknown
                    season = title.data['seasons'][-2]
                else:
                    season = title.data['seasons'][-1]

                data_imdb = {'Titulo': title.data['title'], 'Temp': season, 'year': title.data['year_end'],
                             'id_imdb': i['imdb_id']}
                cap = self.search_chapter(i['imdb_id'])
                data_imdb['Cap'] = cap

                if not self.check_data_partial(data_imdb, i):
                    logger.info(data_imdb)
                    self._update_serie_partial(data_imdb)

            except Exception as e:
                logger.error(f'FALLO: {i["Nombre"]}')
                logger.error(e)

    """
    busca las series que tienen vacios los cambios de imdb y los actualiza por primera vez
    """

    def update_completed(self):
        query = 'SELECT * FROM Series WHERE imdb_seguir LIKE "Si" AND (imdb_id IS NULL OR imdb_Finaliza IS NULL) AND ' \
                'NOT imdb_id IS NULL'  # para nuevas series con mod completa
        series = conection_sqlite(self.nombre_db, query, True)
        logger.info(series)

        for i in series:
            try:
                logger.debug(i['Nombre'])
                title = self.imdb.get_title_by_id(i['imdb_id'])

                if title.data['seasons'][-1] == 'unknown':  # en algunas series la ultima temporada pone unknown
                    season = title.data['seasons'][-2]
                else:
                    season = title.data['seasons'][-1]

                data_imdb = {'Titulo': title.data['title'], 'Temp': season, 'year': title.data['year_end'],
                             'id_imdb': i['imdb_id']}
                cap = self.search_chapter(i['imdb_id'])
                data_imdb['Cap'] = cap

                if not self.check_data(data_imdb, i):
                    # logger.info('completo')
                    self._update_serie(data_imdb)

            except Exception as e:
                logger.error(f'FALLO: {i["Nombre"]}')
                logger.error(e)

    def update_series(self, imdb_id):
        logger.info(imdb_id)
        try:
            title = self.imdb.get_title_by_id(imdb_id)

            if title.data['seasons'][-1] == 'unknown':  # en algunas series la ultima temporada pone unknown
                temporada = title.data['seasons'][-2]
            else:
                temporada = title.data['seasons'][-1]

            datos_imdb = {'Titulo': title.data['title'], 'Temp': temporada, 'year': title.data['year_end'],
                          'id_imdb': imdb_id}
            cap = self.search_chapter(imdb_id)
            datos_imdb['Cap'] = cap

            self._update_serie(datos_imdb)

        except Exception as e:
            logger.error(f'FALLO: {title.data["title"]}')
            logger.error(e)

    def check_title(self, imdb_id):
        """
        Comprueba si el titulo pasado existe o no en la base de datos de imdb
        """
        try:
            self.imdb.get_title_by_id(imdb_id)
        except Exception:
            return False
        return True

    def series_finished(self):
        """
        busca las series finalizadas que tienen el imdb_seguir a si y lo actualiza a no para
        hacer mas rapidas las futuras actualizaciones
        """
        query = 'SELECT * FROM Series Where Estado LIKE "Finalizada" AND imdb_seguir LIKE "Si"'
        series = conection_sqlite(self.nombre_db, query, True)

        query_all = str()

        for i in series:
            query = f'UPDATE series SET imdb_seguir="No" WHERE Nombre LIKE "{i["Nombre"]}";'
            query_all += '\n' + query

        # logger.info(queryCompleta)
        execute_script_sqlite(self.nombre_db, query_all)


def main():
    a = UpdateImdb()
    # logger.info((a.compruebaTitulo('tt1475582')))
    # """
    logger.info('actualizaTemporadas')
    # actualizar_insertar series con mod parcial(todas lases series siguiendo,
    # tarda bastante)
    a.update_season()
    logger.info('actulizaCompleto')
    a.update_completed()
    logger.info('actualizaSerie')
    # a.actualizaSerie('tt3551096')
    # """				# actualizar_insertar series que no tienen datos de capitulo/temporada de imdb
    a.series_finished()


if __name__ == '__main__':
    main()
