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

from app.modulos import funciones
from app.modulos.connect_sqlite import conection_sqlite, execute_script_sqlite
from app.modulos.mail2 import ML2
from app.modulos.pushbullet2 import PB2
from app.modulos.settings import directorio_trabajo, ruta_db
from app.modulos.telegram2 import Telegram
from app import logger

from typing import List, NoReturn, Dict
from dataclasses import dataclass

SERIE_DEBUG = "SEAL Team"


# https://gist.github.com/kaotika/e8ca5c340ec94f599fb2

@dataclass
class Feed:
    title: str
    link: str
    chapter: int
    name: str = str()
    season: int = int()
    epi: str = str()

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
        self.entries = list()

    def add(self, title: str, cap: str, link: str) -> NoReturn:
        print(cap)
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
            logger.critical("Status code get({}) is: {}".format(login, login.status_code))
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
                        url = '{}{}'.format('https://dontorrent.com', serie['href'])
                        f.add(serie.text, capitulo.text, url)

        for i in f.entries:
            logger.debug('-> {}'.format(i.toString()))

        return f


class DescargaAutomaticaCli:
    def __init__(self, database: str = None) -> NoReturn:
        if funciones.internet_on():
            self._logger = logger
            self._logger.debug('Start')

            if database is None:  # en herencia no mando ruta
                self.db = ruta_db
            else:
                self.db = database

            self.notificaciones = self.show_notifications()  # variable publica

            self.query = 'SELECT Nombre, Temporada, Capitulo, VOSE FROM Series WHERE Siguiendo = "Si" ' \
                         'ORDER BY Nombre ASC'
            self.series = conection_sqlite(self.db, self.query, True)

            self.listaNotificaciones = str()
            self.actualizaDia = str()
            self.conf = funciones.db_configuarion()

            # urlNew = self.conf['UrlFeedNewpct']
            url_show = self.conf['UrlFeedShowrss']

            # Diccionario con las series y capitulos para actualizar la bd el capitulo descargado
            self.capDescargado: Dict = dict()
            self.consultaUpdate: str = str()
            self.rutlog: str = str()
            self.ultimaSerieNew: str = str()
            self.ultimaSerieShow: str = str()
            self.titleSerie: str = str()

            self.feedNew = FeedparserPropio.parse(self._logger)
            """
            try:
                self.feedNew = feedparser.parse(urlNew)
            except TypeError:  # Para el fallo en fedora
                self.feedNew = funciones.feedParser(urlNew)
            """

            try:
                self.feedShow = feedparser.parse(url_show)
            except TypeError:  # Para el fallo en fedora
                self.feedShow = funciones.feed_parser(url_show)

            self.consultaSeries = conection_sqlite(self.db, self.query, True)

    def run(self) -> NoReturn:
        serie_actual_new = str()
        serie_actual_show = str()
        # SerieActualTemp = str()

        fich_newpct = self.conf['FicheroFeedNewpct']
        fich_showrss = self.conf['FicheroFeedShowrss']
        self.rutlog = r'{}/log'.format(directorio_trabajo)

        if not os.path.exists(self.rutlog):
            os.mkdir(self.rutlog)

        if not os.path.exists('{}/{}'.format(self.rutlog, fich_newpct)):
            funciones.create_file('{}/{}'.format(self.rutlog, fich_newpct))

        if not os.path.exists('{}/{}'.format(self.rutlog, fich_showrss)):
            funciones.create_file('{}/{}'.format(self.rutlog, fich_showrss))

        with open('{}/{}'.format(self.rutlog, fich_newpct), 'r') as f:
            self.ultimaSerieNew = f.readline()

        with open('{}/{}'.format(self.rutlog, fich_showrss), 'r') as f:
            self.ultimaSerieShow = f.readline()

        for i in self.consultaSeries:
            try:
                self._logger.info(('Revisa: {}'.format(funciones.remove_tildes(i['Nombre']))))
                serie_actual_temp = self.parser_feed(i['Nombre'], i['Temporada'], i['Capitulo'], i['VOSE'])
                if i['VOSE'] == 'Si':
                    serie_actual_show = serie_actual_temp
                else:
                    serie_actual_new = serie_actual_temp
            except Exception as e:
                self._logger.error('################ {} FALLO {}'.format(i['Nombre'], e))

        if len(self.ultimaSerieNew) != 0:  # or len(self.ultimaSerieShow) != 0:
            # self._logger.info(self.actualizaDia)
            # actualiza los dias en los que sale el capitulo
            execute_script_sqlite(self.db, self.actualizaDia)

            for notif in self.notificaciones:
                if notif['Activo'] == 'True':
                    if notif['Nombre'] == 'Telegram':
                        self._logger.critical("TEST A")
                        tg3.send_tg(self.listaNotificaciones)
                        self._logger.critical("TEST B")
                    elif notif['Nombre'] == 'Pushbullet':
                        pb3.send_text_pb('Gestor series', self.listaNotificaciones)

        # capitulos que descargo
        for i in self.capDescargado.items():
            query = 'UPDATE Series SET Capitulo_Descargado={} WHERE Nombre LIKE "{}";\n'.format(str(i[1]), i[0])
            self.consultaUpdate += query

        self._logger.info(self.consultaUpdate)

        # actualiza el ultimo capitulo que he descargado
        execute_script_sqlite(self.db, self.consultaUpdate)

        # Guardar ultima serie del feed
        if serie_actual_show is not None and serie_actual_new is not None:
            with open('{}/{}'.format(self.rutlog, fich_newpct), 'w') as f:
                f.write(funciones.remove_tildes(serie_actual_new))
            with open('{}/{}'.format(self.rutlog, fich_showrss), 'w') as f:
                f.write(funciones.remove_tildes(serie_actual_show))
        else:
            self._logger.error('PROBLEMA CON if SerieActualShow is not None and SerieActualNew is not None:')

    def parser_feed(self, serie: str, tem: str, cap: str, vose: str) -> str:
        """Solo funciona con series de 2 digitos por la expresion regular"""
        cap = str(cap)
        ruta = str(self.conf['RutaDescargas'])  # es unicode
        if vose == 'Si':
            last_serie = self.ultimaSerieShow
            d = self.feedShow
        else:
            last_serie = self.ultimaSerieNew
            d = self.feedNew

        if not os.path.exists(ruta):
            os.mkdir(ruta)

        if len(str(cap)) == 1:
            cap = '0' + str(cap)

        for i in d.entries:
            self.titleSerie = funciones.remove_tildes(i.title)
            # cuando llegamos al ultimo capitulo pasamos a la siguiente serie
            # self._logger.info(self.titleSerie, ".........", ultimaSerie, ".FIN")
            if self.titleSerie == last_serie:
                # retornamos el valor que luego usaremos en ultima serie para guardarlo en el fichero
                pass
                # return funciones.eliminaTildes(d.entries[0].title)  # FIXME DESCOMENTAR

            regex_vose = r'{} ({}|{}|{}).*'.format(funciones.scapes_parenthesis(serie.lower()), tem, tem + 1, tem + 2)
            # regex_cast = r'(?i){}.*Temporada( )?({}|{}|{}).*Capitulo( )?\d+.*'.format(
            #    funciones.escapaParentesis(serie.lower()), tem, tem + 1, tem + 2)
            regex_cast = r'{}'.format(funciones.scapes_parenthesis(serie.lower()))

            if serie.lower() == SERIE_DEBUG.lower():
                self._logger.info("{} - {}".format(regex_cast, self.titleSerie))
                self._logger.info(i.link)

            estado = False
            if vose == 'Si':
                if re.search(regex_vose, self.titleSerie, re.IGNORECASE):
                    estado = True
            else:
                if re.search(regex_cast, self.titleSerie, re.IGNORECASE):
                    self._logger.debug('DESCARGA: {}'.format(i.toString()))
                    estado = True

            if estado:
                title_serie = self.titleSerie  # conversion necesaria para usar como str
                if vose == 'Si':
                    torrents = list(i.link)
                else:
                    torrents = funciones.get_url_torrent_dontorrent(i.link)

                try:  # arreglar problema codificacion de algunas series
                    self._logger.info(title_serie)
                except Exception:
                    title_serie = title_serie.replace(u"\uFFFD", "?")

                if not os.path.exists(u'{}{}.torrent'.format(ruta, title_serie)):
                    fichero_descargas = self.conf['FicheroDescargas']
                    with open('{}/{}'.format(self.rutlog, fichero_descargas), 'a') as f:
                        f.write('{} {}\n'.format(time.strftime('%Y%m%d'), title_serie))

                    if vose == 'Si':
                        self.extra_action(title_serie)
                        # creo un string para solo mandar una notificacion
                        self.listaNotificaciones += '{}\n'.format(title_serie)
                    else:
                        self.extra_action('{} {}'.format(i.name, i.cap))
                        # creo un string para solo mandar una notificacion
                        self.listaNotificaciones += '{} {}\n'.format(i.name, i.cap)

                    self._logger.critical('++{}'.format(torrents))
                    for torrent in torrents:
                        funciones.download_file(torrent, r'{}/{}.torrent'.format(ruta, torrent.split('/')[-1]))
                        # Diccionario con todos los capitulos descargados, para actualizar la bd con los capitulos por
                        # donde voy regex para coger el capitulo unicamente
                    self.actualizaDia += """\nUPDATE series SET Dia="{}" WHERE Nombre LIKE "{}";""".format(
                        funciones.calculate_day_week(), serie)
                    self.capDescargado[serie] = i.epi

                self._logger.info(('DESCARGANDO: {}'.format(serie)))

        return funciones.remove_tildes(d.entries[0].title)

    def extra_action(self, serie: str) -> NoReturn:
        """
        Metodo que no hace nada en esta clase pero que en herencia es
        usado para usar el entorno ggrafico que QT
        :return:
        """
        pass

    def get_series(self) -> List:
        return self.consultaSeries

    def get_actual_serie(self) -> str:
        return self.titleSerie

    @staticmethod
    def show_notifications() -> List:
        """
        poner las api de la base de datos
        """
        query_n = 'SELECT * FROM notificaciones'
        datos = conection_sqlite(ruta_db, query_n, True)

        global tg3, pb3, ml3, api_ml3
        logger.info(datos)
        for i in datos:
            if i['Activo'] == 'True':
                if i['Nombre'] == 'Telegram':
                    tg3 = Telegram(i['API'])

                elif i['Nombre'] == 'Pushbullet':
                    pb3 = PB2(i['API'])

                elif i['Nombre'] == 'Email':
                    ml3 = ML2('test1notificaciones@gmail.com', 'i(!f!Boz_A&YLY]q')
                    api_ml3 = api_ml3

        return datos


def main():
    d = DescargaAutomaticaCli(database=ruta_db)
    d.run()
    # feedparserPropio.parse()


if __name__ == '__main__':
    main()
    # feed('Strike Back - Temporada 7 Capitulo 10', 'https://pcttemporada-1/capitulo-04/')
