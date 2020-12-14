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
import threading
import time
from abc import abstractmethod
from pathlib import Path  # nueva forma de trabajar con rutas
from pathlib import PurePath  # nueva forma de trabajar con rutas
from typing import List, NoReturn, Dict, Optional, AnyStr, Text

import urllib3

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: Text = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

import app.controller.Controller as Controller
from app import logger
from app.utils import funciones
from app.utils.mail2 import ML2
from app.utils.pushbullet2 import PB2
from app.utils.settings import FILE_LOG_FEED, FILE_LOG_FEED_VOSE, FILE_LOG_DOWNLOADS, CLIENT_TORRENT
from app.utils.telegram2 import Telegram, Notification
from app.models.model_query import Query
from app.models.model_notifications import Notifications
from app.models.model_serie import Serie
from app.models.model_preferences import Preferences
from app.models.model_t_torrent import Torrent
from app.models.model_t_pctmix import FeedparserPctmix, Pctmix
from app.models.model_t_showrss import FeedparserShowRss, ShowRss
from app.models.model_t_feedparser import FeedParser
from app.models.model_t_feed import Feed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
SERIE_DEBUG: Text = "--The Good Place"

# global global_response
global_response: Text = str()


# https://gist.github.com/kaotika/e8ca5c340ec94f599fb2


class DescargaAutomaticaCli:
    def __init__(self) -> NoReturn:
        if funciones.internet_on():
            logger.debug('Start')
            self.tg3: Telegram
            self.pb3: PB2
            self.ml3: ML2

            self.notifications: List[Notifications] = self.show_notifications()  # variable publica

            self.series_download_notification: Text = str()
            self.day_updated: Text = str()
            preferences: Query = Controller.get_database_configuration()
            self.preferences: Preferences = preferences.response[0]
            # urlNew = self.conf['UrlFeedNewpct']
            url_show: Text = self.preferences.url_feed_vose

            # Diccionario con las series y capitulos para actualizar la bd el capitulo descargado
            self.chapter_download: Dict[Text, Text] = dict()
            self.query_update: Text = str()
            self.last_serie_esp: Text = str()
            self.last_serie_eng: Text = str()
            self.title_serie: Text = str()

            self.feed_esp: FeedParser = FeedparserPctmix.parse()
            self.feed_eng: FeedParser = FeedparserShowRss.parse(url_show)

            response_query: Query = Controller.get_series_follow()
            self.query_series: List[Serie] = response_query.response

    def run(self) -> AnyStr:
        serie_actual_esp: Text = str()
        serie_actual_eng: Text = str()
        # SerieActualTemp = str()
        global global_response

        if FILE_LOG_FEED.exists():
            self.last_serie_esp: Text = FILE_LOG_FEED.read_text()  # FIXME REVISAR
        else:
            FILE_LOG_FEED.write_text('')
            self.last_serie_esp: Text = ''

        if FILE_LOG_FEED_VOSE.exists():
            self.last_serie_eng: Text = FILE_LOG_FEED_VOSE.read_text()  # FIXME REVISAR
        else:
            FILE_LOG_FEED_VOSE.write_text('')
            self.last_serie_eng: Text = ''

        for serie in self.query_series:
            try:
                logger.info(f'Revisa: {funciones.remove_tildes(serie.title)}')
                global_response += f'Revisa: {funciones.remove_tildes(serie.title)}\n'
                serie_actual_temp: Text = self.parser_feed(serie)
                if serie.vose:
                    serie_actual_eng: Text = serie_actual_temp
                else:
                    serie_actual_esp: Text = serie_actual_temp

                ############################################
                ############################################
                # if re.search(SERIE_DEBUG, serie.title, re.IGNORECASE):
                #    sys.exit(0)
                ############################################
                ############################################
            except Exception as e:
                logger.error(f'################ {serie.title} FALLO {e}')

        if len(self.series_download_notification) != 0:
            # logger.info(self.actualizaDia)
            # actualiza los dias en los que sale el capitulo
            Controller.execute_query_script_sqlite(self.day_updated)

            for notification in self.notifications:
                if notification.active:
                    if notification.name == 'Telegram':
                        logger.critical("TEST A")
                        self.tg3.send_tg(self.series_download_notification)
                        logger.critical("TEST B")
                    elif notification.name == 'Pushbullet':
                        self.pb3.send_text_pb('Gestor series', self.series_download_notification)

        # capitulos que descargo
        for serie in self.chapter_download.items():
            query: Text = f'UPDATE Series SET Capitulo_Descargado={str(serie[1])} WHERE Nombre LIKE "{serie[0]}";\n'
            self.query_update += query

        # actualiza el ultimo capitulo que he descargado
        Controller.execute_query_script_sqlite(self.query_update)

        # Guardar ultima serie del feed
        if serie_actual_eng is not None and serie_actual_esp is not None:
            FILE_LOG_FEED.write_text(funciones.remove_tildes(serie_actual_esp))  # FIXME REVISAR
            FILE_LOG_FEED_VOSE.write_text(funciones.remove_tildes(serie_actual_eng))
        else:
            logger.error('PROBLEMA CON if SerieActualShow is not None and SerieActualNew is not None:')

        return global_response

    def parser_feed(self, serie: Serie) -> Optional[Text]:
        """
        Metodo que comprueba para la serie proporcionada si se encuentra en el feed de nuevos capitulos publicados
        :param serie:
        :return:
        """
        # Contine el feed de series en español o vose segun el idioma en el que se ve la serie
        feed_parser: FeedParser
        global global_response

        if serie.vose:
            last_serie: Text = self.last_serie_eng
            feed_parser = self.feed_eng
        else:
            last_serie: Text = self.last_serie_esp
            feed_parser = self.feed_esp

        if not self.preferences.path_download.exists():
            Path.mkdir(self.preferences.path_download)

        # if len(str(cap)) == 1:
        #    cap = '0' + str(cap)
        entrie: Feed
        for entrie in feed_parser.entries:
            self.title_serie = funciones.remove_tildes(entrie.title)
            # cuando llegamos al ultimo capitulo pasamos a la siguiente serie
            # logger.info(f'@@@@@@@{entrie.original_name}###########{last_serie}$$$$FIN')
            if entrie.original_name == last_serie:
                # retornamos el valor que luego usaremos en ultima serie para guardarlo en el fichero
                return funciones.remove_tildes(feed_parser.entries[0].original_name)  # FIXME DESCOMENTAR

            regex_eng = rf'{re.escape(serie.title.lower())}'
            regex_esp = rf'{re.escape(serie.title.lower())}'

            if serie.title.lower() == SERIE_DEBUG.lower():
                logger.warning(f"{regex_esp} - {self.title_serie}")
                logger.warning(entrie.link)

            estado: bool = False
            if serie.vose:
                if re.search(regex_eng, self.title_serie, re.IGNORECASE):
                    logger.info(f'DESCARGA: {entrie}')
                    global_response += f'**DESCARGA: {entrie}** \n'
                    estado = True
            else:
                if re.search(regex_esp, self.title_serie, re.IGNORECASE):
                    logger.info(f'DESCARGA: {entrie}')
                    global_response += f'**DESCARGA: {entrie}** \n'
                    estado = True

            if estado:
                title_serie = self.title_serie  # conversion necesaria para usar como str
                try:  # arreglar problema codificacion de algunas series
                    logger.info(title_serie)
                except Exception as e:
                    print(e)
                    logger.critical("Si ves esto investiga porque ha salido")
                    title_serie = title_serie.replace(u"\uFFFD", "?")

                torrents: Torrent
                if serie.vose:
                    torrents = ShowRss(title_serie, entrie.link, self.preferences.path_download,
                                       client_torrent=CLIENT_TORRENT)
                else:
                    torrents: Pctmix = Pctmix(title_serie, entrie.link, self.preferences.path_download)

                FILE_LOG_DOWNLOADS.write_text(f'{time.strftime("%Y%m%d")} {title_serie}\n')
                self.series_download_notification += f'{entrie.title} {entrie.epi}\n'

                logger.debug(f'{torrents}')
                # Descargamos el/los torrents de la serie
                d = threading.Thread(target=torrents.download_file_torrent, name=f'Thread-{serie.title}')
                d.setDaemon(True)
                d.start()
                d.join()

                # Diccionario con todos los capitulos descargados, para actualizar la bd con los capitulos por
                # donde voy regex para coger el capitulo unicamente
                # chapter 99 implica que es una temporada completa
                if entrie.chapter != FeedparserPctmix.NUMBER:
                    self.day_updated += f'\nUPDATE series SET Dia="{funciones.calculate_day_week()}" ' \
                                        f'WHERE Nombre LIKE "{serie.title}";'
                    self.chapter_download[serie.title] = str(entrie.chapter)

                logger.debug(f'DESCARGANDO: {serie.title}')

        if len(feed_parser.entries) > 0:
            return funciones.remove_tildes(feed_parser.entries[0].original_name)
        else:
            logger.warning("feed.entries is empty")
            return None

    @abstractmethod
    def extra_action(self, serie: Text) -> NoReturn:
        """
        Metodo que no hace nada en esta clase pero que en herencia es usado para usar el entorno ggrafico que QT
        :return:
        """

    def get_series(self) -> List[Serie]:
        return self.query_series

    def get_actual_serie(self) -> Text:
        return self.title_serie

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
