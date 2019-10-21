#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# Como ha dejado de funcionar el feed de torrentlocura he creado uno nuevo haciendo scraping web de la pagina de
ultimos capitulos

"""

from __future__ import annotations

import logging
import os
import re
import sys
import time

import feedparser
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
from typing import List, NoReturn, Dict
from dataclasses import dataclass

new_path = '../../'
if new_path not in sys.path:
    sys.path.append(new_path)

from app.modulos import funciones
from app.modulos.connect_sqlite import execute_script_sqlite
from app.modulos.mail2 import ML2
from app.modulos.pushbullet2 import PB2
from app.modulos.settings import DIRECTORY_WORKING, PATH_DATABASE, FILE_LOG_FEED, FILE_LOG_FEED_VOSE, FILE_LOG_DOWNLOADS
from app.modulos.telegram2 import Telegram
from app import logger
import app.controller.Controller as Controller
from app.models.model_query import Query
from app.models.model_notifications import Notifications
from app.models.model_serie import Serie
from app.models.model_preferences import Preferences

SERIE_DEBUG = "SEAL Team"


# https://gist.github.com/kaotika/e8ca5c340ec94f599fb2

@dataclass
class Feed:
    title: str
    link: str
    chapter: int
    name: str = str()
    season: int = int()
    epi: str = str()  # formato de temporada y sesion TxS

    def update_fields(self) -> NoReturn:
        self.name = self.title.split('-')[0]
        season = re.search(r'(\d+). Temporada', self.title)
        if season is not None:
            self.season = int(season.group(1))
        else:  # por ejeplo una miniserie no tiene temporada
            self.season = 1

        self.epi = re.findall(r'\d+', str(self.chapter))[-1]
        # self.cap = "{}x{}".format(self.temp, self.epi)

    def __str__(self) -> NoReturn:
        return f'{self.title} - {self.chapter} - {self.link}'


class FeedparserPropio:
    def __init__(self) -> NoReturn:
        self.entries: List[Feed] = list()

    def add(self, title: str, cap: int, link: str) -> NoReturn:
        # print(cap)
        f = Feed(title.strip(), link, cap)
        f.update_fields()
        self.entries.append(f)

    @staticmethod
    def parse(logger: logging, url: str = 'https://dontorrent.com/series/hd') -> FeedparserPropio:
        """
        """
        req_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
                       'Content-Type': 'application/x-www-form-urlencoded'}

        session = requests.session()
        login = session.get(url, headers=req_headers, verify=False)

        if login.status_code != 200:
            logger.critical(f"Status code get({login}) is: {login.status_code}")
            sys.exit(1)

        sopa = BeautifulSoup(login.text, 'html.parser')
        # sopa = BeautifulSoup(fichero, 'html.parser')
        days = sopa.findAll('div', {"class": "card-body"})
        # result = sopa.findAll('ul', {"class": "noticias-series"})

        f = FeedparserPropio()
        for day in days:
            if not day.findAll('h5'):  # si tiene h5 signigica que es una caja de imagenes de las series
                for serie, capitulo in zip(day.findAll('a'), day.findAll('b')):
                    if not re.match('[A-Z]|TODOS', serie.text):
                        # logger.debug(serie.text)
                        # logger.debug(serie.contents)
                        # logger.debug(serie['href'])
                        # logger.debug(capitulo.text)
                        url = f'https://dontorrent.com{serie["href"]}'
                        # obtenemos todos los episodios y mandamos unicammente el ultimo
                        chapters = re.findall('\d+', str(capitulo.text))
                        f.add(serie.text, int(chapters[-1]), url)

        # [logger.debug(f'-> {i}') for i in f.entries]
        return f


class DescargaAutomaticaCli:
    def __init__(self, database: str = None) -> NoReturn:
        if funciones.internet_on():
            self._logger = logger
            self._logger.debug('Start')

            if database is None:  # en herencia no mando ruta
                self.db = PATH_DATABASE
            else:
                self.db = database

            self.notificaciones: List[Notifications] = self.show_notifications()  # variable publica

            self.listaNotificaciones = str()
            self.actualizaDia = str()
            preferences: Query = Controller.get_database_configuration(self.db)
            self.preferences: Preferences = preferences.response[0]
            # urlNew = self.conf['UrlFeedNewpct']
            url_show = self.preferences.url_feed_vose

            # Diccionario con las series y capitulos para actualizar la bd el capitulo descargado
            self.capDescargado: Dict[str, str] = dict()
            self.consultaUpdate: str = str()
            self.rutlog: str = str()
            self.ultimaSerieNew: str = str()
            self.ultimaSerieShow: str = str()
            self.titleSerie: str = str()

            self.feedNew = FeedparserPropio.parse(self._logger)

            try:
                self.feedShow = feedparser.parse(url_show)
            except TypeError:  # Para el fallo en fedora
                self.feedShow = funciones.feed_parser(url_show)

            response_query: Query = Controller.get_series_follow(self.db)
            self.consultaSeries: List[Serie] = response_query.response

    def run(self) -> NoReturn:
        serie_actual_new = str()
        serie_actual_show = str()
        # SerieActualTemp = str()

        self.rutlog = rf'{DIRECTORY_WORKING}/log'

        if not os.path.exists(self.rutlog):
            os.mkdir(self.rutlog)

        if not os.path.exists(f'{self.rutlog}/{FILE_LOG_FEED}'):
            funciones.create_file(f'{self.rutlog}/{FILE_LOG_FEED}')

        if not os.path.exists(f'{self.rutlog}/{FILE_LOG_FEED_VOSE}'):
            funciones.create_file(f'{self.rutlog}/{FILE_LOG_FEED_VOSE}')

        with open(f'{self.rutlog}/{FILE_LOG_FEED}', 'r') as f:
            self.ultimaSerieNew = f.readline()

        with open(f'{self.rutlog}/{FILE_LOG_FEED_VOSE}', 'r') as f:
            self.ultimaSerieShow = f.readline()

        for serie in self.consultaSeries:
            try:
                self._logger.info(f'Revisa: {funciones.remove_tildes(serie.title)}')
                serie_actual_temp = self.parser_feed(serie)
                if serie.vose:
                    serie_actual_show = serie_actual_temp
                else:
                    serie_actual_new = serie_actual_temp
            except Exception as e:
                self._logger.error(f'################ {serie.title} FALLO {e}')

        if len(self.ultimaSerieNew) != 0:  # or len(self.ultimaSerieShow) != 0:
            # self._logger.info(self.actualizaDia)
            # actualiza los dias en los que sale el capitulo
            execute_script_sqlite(self.db, self.actualizaDia)

            for notification in self.notificaciones:
                if notification.active:
                    if notification.name == 'Telegram':
                        self._logger.critical("TEST A")
                        tg3.send_tg(self.listaNotificaciones)
                        self._logger.critical("TEST B")
                    elif notification.name == 'Pushbullet':
                        pb3.send_text_pb('Gestor series', self.listaNotificaciones)

        # capitulos que descargo
        for serie in self.capDescargado.items():
            query = f'UPDATE Series SET Capitulo_Descargado={str(serie[1])} WHERE Nombre LIKE "{serie[0]}";\n'
            self.consultaUpdate += query

        self._logger.info(self.consultaUpdate)

        # actualiza el ultimo capitulo que he descargado
        execute_script_sqlite(self.db, self.consultaUpdate)

        # Guardar ultima serie del feed
        if serie_actual_show is not None and serie_actual_new is not None:
            with open(f'{self.rutlog}/{FILE_LOG_FEED}', 'w') as f:
                f.write(funciones.remove_tildes(serie_actual_new))
            with open(f'{self.rutlog}/{FILE_LOG_FEED_VOSE}', 'w') as f:
                f.write(funciones.remove_tildes(serie_actual_show))
        else:
            self._logger.error('PROBLEMA CON if SerieActualShow is not None and SerieActualNew is not None:')

    def parser_feed(self, serie: Serie) -> str:
        """Solo funciona con series de 2 digitos por la expresion regular"""
        cap = str(serie.chapter)
        if serie.vose:
            last_serie = self.ultimaSerieShow
            feed = self.feedShow
        else:
            last_serie = self.ultimaSerieNew
            feed = self.feedNew

        if not os.path.exists(self.preferences.path_download):
            os.mkdir(self.preferences.path_download)

        if len(str(cap)) == 1:
            cap = '0' + str(cap)

        for entrie in feed.entries:
            self.titleSerie = funciones.remove_tildes(entrie.title)
            # cuando llegamos al ultimo capitulo pasamos a la siguiente serie
            # self._logger.info(self.titleSerie, ".........", ultimaSerie, ".FIN")
            if self.titleSerie == last_serie:
                # retornamos el valor que luego usaremos en ultima serie para guardarlo en el fichero
                pass
                # return funciones.eliminaTildes(d.entries[0].title)  # FIXME DESCOMENTAR

            regex_vose = rf'{funciones.scapes_parenthesis(serie.title.lower())} (\d+).*'
            # regex_cast = r'(?i){}.*Temporada( )?({}|{}|{}).*Capitulo( )?\d+.*'.format(
            #    funciones.escapaParentesis(serie.lower()), tem, tem + 1, tem + 2)
            regex_cast = rf'{funciones.scapes_parenthesis(serie.title.lower())}'

            if serie.title.lower() == SERIE_DEBUG.lower():
                self._logger.info(f"{regex_cast} - {self.titleSerie}")
                self._logger.info(entrie.link)

            estado = False
            if serie.vose:
                if re.search(regex_vose, self.titleSerie, re.IGNORECASE):
                    estado = True
            else:
                if re.search(regex_cast, self.titleSerie, re.IGNORECASE):
                    self._logger.debug(f'DESCARGA: {entrie}')
                    estado = True

            if estado:
                title_serie = self.titleSerie  # conversion necesaria para usar como str
                if serie.vose:
                    torrents = list(entrie.link)
                else:
                    torrents = funciones.get_url_torrent_dontorrent(entrie.link)

                try:  # arreglar problema codificacion de algunas series
                    self._logger.info(title_serie)
                except Exception:
                    title_serie = title_serie.replace(u"\uFFFD", "?")

                # fixme revisar si funciona antes habia u'...'
                if not os.path.exists(f'{self.preferences.path_download}{title_serie}.torrent'):
                    with open(f'{self.rutlog}/{FILE_LOG_DOWNLOADS}', 'a') as f:
                        f.write(f'{time.strftime("%Y%m%d")} {title_serie}\n')

                    if serie.vose:
                        self.extra_action(title_serie)
                        # creo un string para solo mandar una notificacion
                        self.listaNotificaciones += f'{title_serie}\n'
                    else:
                        self.extra_action(f'{entrie.name} {entrie.chapter}')
                        # creo un string para solo mandar una notificacion
                        self.listaNotificaciones += f'{entrie.name} {entrie.chapter}\n'

                    self._logger.critical(f'++{torrents}')
                    for torrent in torrents:
                        funciones.download_file(torrent, rf'{self.preferences.path_download}/{torrent.split("/")[-1]}.torrent')
                        # Diccionario con todos los capitulos descargados, para actualizar la bd con los capitulos por
                        # donde voy regex para coger el capitulo unicamente
                    self.actualizaDia += f'''\nUPDATE series SET Dia="{funciones.calculate_day_week()}" 
                                            WHERE Nombre LIKE "{serie.title}";'''
                    self.capDescargado[serie.title] = entrie.epi

                self._logger.info(f'DESCARGANDO: {serie.title}')

        return funciones.remove_tildes(feed.entries[0].title)

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

    @staticmethod
    def show_notifications() -> List[Notifications]:
        """
        poner las api de la base de datos
        """
        response_query: Query = Controller.get_notifications(PATH_DATABASE)
        notifications: List[Notifications] = response_query.response
        global tg3, pb3, ml3, api_ml3
        logger.info(notifications)
        for i in notifications:
            if i.active:
                if i.name == 'Telegram':
                    tg3 = Telegram(i.api)

                elif i.name == 'Pushbullet':
                    pb3 = PB2(i.api)

                elif i.name == 'Email':
                    ml3 = ML2('test1notificaciones@gmail.com', 'i(!f!Boz_A&YLY]q')
                    api_ml3 = api_ml3
        return notifications


def main():
    d = DescargaAutomaticaCli(database=PATH_DATABASE)
    d.run()
    # feedparserPropio.parse()


if __name__ == '__main__':
    main()
    # feed('Strike Back - Temporada 7 Capitulo 10', 'https://pcttemporada-1/capitulo-04/')
