#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# Como ha dejado de funcionar el feed de torrentlocura he creado uno nuevo haciendo scraping web de la pagina de
ultimos capitulos

"""

from __future__ import annotations

import os
import re
import sys
import time
from abc import abstractmethod
from pathlib import Path  # nueva forma de trabajar con rutas
from pathlib import PurePath  # nueva forma de trabajar con rutas
from typing import List, NoReturn, Dict, Optional

import feedparser
import urllib3

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: str = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

import app.controller.Controller as Controller
from app import logger
from app.utils import funciones
from app.utils.mail2 import ML2
from app.utils.pushbullet2 import PB2
from app.utils.settings import FILE_LOG_FEED, FILE_LOG_FEED_VOSE, FILE_LOG_DOWNLOADS
from app.utils.telegram2 import Telegram
from app.models.model_query import Query
from app.models.model_notifications import Notifications
from app.models.model_serie import Serie
from app.models.model_preferences import Preferences
from app.models.model_grantorrent import FeedparserPropio, GranTorrent

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
SERIE_DEBUG = "SEAL Team"


# https://gist.github.com/kaotika/e8ca5c340ec94f599fb2


class DescargaAutomaticaCli:
    def __init__(self) -> NoReturn:
        if funciones.internet_on():
            logger.debug('Start')
            self.tg3: Telegram
            self.pb3: PB2
            self.ml3: ML2

            self.notificaciones: List[Notifications] = self.show_notifications()  # variable publica

            self.listaNotificaciones: str = str()
            self.actualizaDia: str = str()
            preferences: Query = Controller.get_database_configuration()
            self.preferences: Preferences = preferences.response[0]
            # urlNew = self.conf['UrlFeedNewpct']
            url_show: str = self.preferences.url_feed_vose

            # Diccionario con las series y capitulos para actualizar la bd el capitulo descargado
            self.capDescargado: Dict[str, str] = dict()
            self.consultaUpdate: str = str()
            self.ultimaSerieNew: str = str()
            self.ultimaSerieShow: str = str()
            self.titleSerie: str = str()

            self.feedNew: FeedparserPropio = FeedparserPropio.parse()
            try:
                self.feedShow = feedparser.parse(url_show)
            except TypeError:  # Para el fallo en fedora
                self.feedShow = funciones.feed_parser(url_show)

            response_query: Query = Controller.get_series_follow()
            self.consultaSeries: List[Serie] = response_query.response

    def run(self) -> NoReturn:
        serie_actual_new: str = str()
        serie_actual_show: str = str()
        # SerieActualTemp = str()

        if FILE_LOG_FEED.exists():
            self.ultimaSerieNew = FILE_LOG_FEED.read_text()  # FIXME REVISAR
        else:
            FILE_LOG_FEED.write_text('')
            self.ultimaSerieNew = ''

        if FILE_LOG_FEED_VOSE.exists():
            self.ultimaSerieShow = FILE_LOG_FEED_VOSE.read_text()  # FIXME REVISAR
        else:
            FILE_LOG_FEED_VOSE.write_text('')
            self.ultimaSerieShow = ''

        for serie in self.consultaSeries:
            try:
                logger.info(f'Revisa: {funciones.remove_tildes(serie.title)}')
                serie_actual_temp = self.parser_feed(serie)
                if serie.vose:
                    serie_actual_show = serie_actual_temp
                else:
                    serie_actual_new = serie_actual_temp
            except Exception as e:
                logger.error(f'################ {serie.title} FALLO {e}')

        if len(self.listaNotificaciones) != 0:
            # logger.info(self.actualizaDia)
            # actualiza los dias en los que sale el capitulo
            Controller.execute_query_script_sqlite(self.actualizaDia)  # fixme meter a controlador

            for notification in self.notificaciones:
                if notification.active:
                    if notification.name == 'Telegram':
                        logger.critical("TEST A")
                        self.tg3.send_tg(self.listaNotificaciones)
                        logger.critical("TEST B")
                    elif notification.name == 'Pushbullet':
                        self.pb3.send_text_pb('Gestor series', self.listaNotificaciones)

        # capitulos que descargo
        for serie in self.capDescargado.items():
            query = f'UPDATE Series SET Capitulo_Descargado={str(serie[1])} WHERE Nombre LIKE "{serie[0]}";\n'
            self.consultaUpdate += query

        # actualiza el ultimo capitulo que he descargado
        Controller.execute_query_script_sqlite(self.consultaUpdate)

        # Guardar ultima serie del feed
        if serie_actual_show is not None and serie_actual_new is not None:
            FILE_LOG_FEED.write_text(funciones.remove_tildes(serie_actual_new))  # FIXME REVISAR
            FILE_LOG_FEED_VOSE.write_text(funciones.remove_tildes(serie_actual_show))
        else:
            logger.error('PROBLEMA CON if SerieActualShow is not None and SerieActualNew is not None:')

    def parser_feed(self, serie: Serie) -> Optional[str]:
        """Solo funciona con series de 2 digitos por la expresion regular"""
        # cap = str(serie.chapter)
        if serie.vose:
            last_serie = self.ultimaSerieShow
            feed = self.feedShow
        else:
            last_serie = self.ultimaSerieNew
            feed = self.feedNew

        if not self.preferences.path_download.exists():
            Path.mkdir(self.preferences.path_download)

        # if len(str(cap)) == 1:
        #    cap = '0' + str(cap)
        for entrie in feed.entries:
            self.titleSerie = funciones.remove_tildes(entrie.title)
            # cuando llegamos al ultimo capitulo pasamos a la siguiente serie
            # logger.info(self.titleSerie, ".........", ultimaSerie, ".FIN")
            if self.titleSerie == last_serie:
                # retornamos el valor que luego usaremos en ultima serie para guardarlo en el fichero
                pass
                return funciones.remove_tildes(entrie.title)  # FIXME DESCOMENTAR

            regex_vose = rf'{funciones.scapes_parenthesis(serie.title.lower())} (\d+).*'
            # regex_cast = r'(?i){}.*Temporada( )?({}|{}|{}).*Capitulo( )?\d+.*'.format(
            #    funciones.escapaParentesis(serie.lower()), tem, tem + 1, tem + 2)
            regex_cast = rf'{funciones.scapes_parenthesis(serie.title.lower())}'

            if serie.title.lower() == SERIE_DEBUG.lower():
                logger.info(f"{regex_cast} - {self.titleSerie}")
                logger.info(entrie.link)

            estado: bool = False
            if serie.vose:
                if re.search(regex_vose, self.titleSerie, re.IGNORECASE):
                    estado = True
            else:
                if re.search(regex_cast, self.titleSerie, re.IGNORECASE):
                    logger.debug(f'DESCARGA: {entrie}')
                    estado = True

            if estado:
                title_serie = self.titleSerie  # conversion necesaria para usar como str
                try:  # arreglar problema codificacion de algunas series
                    logger.info(title_serie)
                except Exception as e:
                    print(e)
                    title_serie = title_serie.replace(u"\uFFFD", "?")

                if serie.vose:
                    torrents = list(entrie.link)
                else:
                    torrents = GranTorrent(title_serie, entrie.link, self.preferences.path_download)

                FILE_LOG_DOWNLOADS.write_text(f'{time.strftime("%Y%m%d")} {title_serie}\n')

                if serie.vose:
                    # self.extra_action(title_serie)
                    # creo un string para solo mandar una notificacion
                    self.listaNotificaciones += f'{title_serie}\n'
                else:
                    # self.extra_action(f'{entrie.title} {entrie.chapter}')
                    # creo un string para solo mandar una notificacion
                    self.listaNotificaciones += f'{entrie.title} {entrie.chapter}\n'

                logger.debug(f'{torrents}')
                if isinstance(torrents, GranTorrent):
                    torrents.download_file_torrent()
                else:
                    for torrent in torrents:
                        funciones.download_file(torrent,
                                                rf'{self.preferences.path_download}/{torrent.split("/")[-1]}.torrent')
                    # Diccionario con todos los capitulos descargados, para actualizar la bd con los capitulos por
                    # donde voy regex para coger el capitulo unicamente
                if entrie.season != 99:
                    self.actualizaDia += f'''\nUPDATE series SET Dia="{funciones.calculate_day_week()}" WHERE Nombre LIKE "{serie.title}";'''
                    self.capDescargado[serie.title] = entrie.season

                logger.info(f'DESCARGANDO: {serie.title}')

        if len(feed.entries) > 0:
            return funciones.remove_tildes(feed.entries[0].title)
        else:
            logger.warning("feed.entries is empty")
            return None

    @abstractmethod
    def extra_action(self, serie: str) -> NoReturn:
        """
        Metodo que no hace nada en esta clase pero que en herencia es usado para usar el entorno ggrafico que QT
        :return:
        """
        pass

    def get_series(self) -> List[Serie]:
        return self.consultaSeries

    def get_actual_serie(self) -> str:
        return self.titleSerie

    def show_notifications(self) -> List[Notifications]:
        """
        poner las api de la base de datos
        """
        response_query: Query = Controller.get_notifications()
        notifications: List[Notifications] = response_query.response
        logger.info(notifications)
        for i in notifications:
            if i.active:
                if i.name == 'Telegram':
                    self.tg3 = Telegram(i.api)
                elif i.name == 'Pushbullet':
                    self.pb3 = PB2(i.api)
                elif i.name == 'Email':
                    self.ml3 = ML2('test1notificaciones@gmail.com', 'i(!f!Boz_A&YLY]q')
        return notifications


def main():
    d = DescargaAutomaticaCli()
    d.run()
    # feedparserPropio.parse()


if __name__ == '__main__':
    main()
    # feed('Strike Back - Temporada 7 Capitulo 10', 'https://pcttemporada-1/capitulo-04/')
