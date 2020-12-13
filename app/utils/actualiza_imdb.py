#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
from pathlib import PurePath  # nueva forma de trabajar con rutas

import requests
from imdbpie import Imdb
from imdbpie.objects import Title

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: str = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

from app import logger

import app.controller.Controller as Controller
from app.utils.settings import PATH_DATABASE
from app.models.model_query import Query
from app.models.model_serie import Serie
from app.models.model_serie_imdb import SerieImdb


class UpdateImdb:
    def __init__(self):
        self.imdb = Imdb()
        self.database = PATH_DATABASE
        self.preferences = Controller.get_database_configuration()
        # self.imdb = Imdb(cache=True, cache_dir='/tmp/imdbpie-cache-here', anonymize=False)

    @staticmethod
    def check_data(imdb: SerieImdb, serie: Serie):
        if serie.imdb_season == imdb.season and serie.imdb_finished == imdb.year and serie.imdb_chapter == imdb.chapter:
            return True
        else:
            return False

    @staticmethod
    def check_data_partial(imdb: SerieImdb, serie: Serie):
        if serie.imdb_season == imdb.chapter and serie.imdb_finished == imdb.year:
            return True
        else:
            return False

    @staticmethod
    def search_chapter(id_imdb) -> int:
        # Para buscar el capitulo en vez de coger el la primera temporada, coger la ultima
        # problema de que la ultima temporada no este completa
        url = f'http://www.imdb.com/title/{id_imdb}/episodes?season=1'
        session = requests.session()
        html = session.get(url, verify=True).text
        a = re.findall('S1, Ep[0-9]+', html)
        return int(re.findall('[0-9]+', a[-1])[-1])

    def get_serie_imdb(self, imdb_id) -> SerieImdb:
        """
        Metodo usado por tres funciones apra obtener los datos de imdb de una serie
        :param imdb_id:
        :return:
        """
        title: Title = None
        try:
            title = self.imdb.get_title_by_id(imdb_id)
            if title.data['seasons'][-1] == 'unknown':  # en algunas series la ultima temporada pone unknown
                season = title.data['seasons'][-2]
            else:
                season = title.data['seasons'][-1]
            chapter = self.search_chapter(imdb_id)

            return SerieImdb(title.data['title'], season, chapter, title.data['year_end'], imdb_id)
        except Exception as e:
            logger.error(e)
            logger.error(f'FALLO: {imdb_id}')
            if title is not None:
                logger.error(f'FALLO: {title.data["title"]}')

    def update_season(self):  # tarda mucho
        # para actualizar_insertar series con mod parcial
        response_query: Query = Controller.get_series_following_imdb()

        for serie in response_query.response:
            logger.info(serie.title)
            data_imdb: SerieImdb = self.get_serie_imdb(serie.imdb_id)

            if not self.check_data_partial(data_imdb, serie):
                logger.info(data_imdb)
                Controller.update_serie_partial_imdb(data_imdb)

    def update_completed(self):
        """
        busca las series que tienen vacios los cambios de imdb y los actualiza por primera vez
        """
        response_query: Query = Controller.get_series_completed_imdb()
        logger.info(response_query.response)

        for serie in response_query.response:
            data_imdb: SerieImdb = self.get_serie_imdb(serie.imdb_id)
            if not self.check_data(data_imdb, serie):
                # logger.info('completo')
                Controller.update_serie_imdb(data_imdb)

    def update_series(self, imdb_id: str):
        logger.info(imdb_id)
        data_imdb: SerieImdb = self.get_serie_imdb(imdb_id)
        Controller.update_serie_imdb(data_imdb)

    def check_title(self, imdb_id):
        """
        Comprueba si el titulo pasado existe o no en la base de datos de imdb
        """
        try:
            self.imdb.get_title_by_id(imdb_id)
        except Exception as e:
            print(e)
            logger.error(e)
            return False
        return True

    def series_finished(self):
        """
        busca las series finalizadas que tienen el imdb_seguir a si y lo actualiza a no para
        hacer mas rapidas las futuras actualizaciones
        """
        Controller.update_series_finished_imdb()


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
