#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import PurePath, Path  # nueva forma de trabajar con rutas
from typing import NoReturn, Optional, List

import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: str = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

from app import logger
from app.models.model_t_feedparser import FeedParser
from app.models.model_t_torrent import Torrent
from app.models.model_t_feed import Feed

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class FeedparserDonTorrent(FeedParser):
    def __init__(self) -> NoReturn:
        self.entries: List[Feed] = list()

    @staticmethod
    def parse(url: str = 'https://dontorrent.com/series/hd') -> FeedParser:
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
        f = FeedparserDonTorrent()
        for day in days:
            if not day.findAll('h5'):  # si tiene h5 signigica que es una caja de imagenes de las series
                print(day)
                print(day.findAll('h5'))
                print("#############")
                for serie, capitulo in zip(day.findAll('a'), day.findAll('b')):
                    if not re.match('[A-Z]|TODOS', serie.text):
                        logger.debug(serie.text)
                        logger.debug(serie.contents)
                        logger.debug(serie['href'])
                        logger.debug(capitulo.text)
                        url = f'https://dontorrent.com{serie["href"]}'
                        # obtenemos todos los episodios y mandamos unicammente el ultimo
                        season = re.findall('\d+', str(capitulo.text))
                        # FIXME CAMBIAR 88 POR EL chapter CORRESPONDIENTE
                        f.add(serie.text, int(season[-1]), 88, url)

        [logger.debug(f'-> {i}') for i in f.entries]
        return f


@dataclass
class DonTorrent(Torrent):
    """
    """

    def download_file_torrent(self) -> NoReturn:

        url_torrent_serie: List = self.get_url_torrent()
        url_torrent_peli: str = self.get_url_torrent_dontorrent_direct()

        if url_torrent_serie is None and url_torrent_peli is None:
            print("No se encuentra la url del torrent")
            return

        # Peliculas tienen 1 link
        if url_torrent_peli is not None:
            logger.debug('Download peli')
            self.path_file_torrent: Path = Path(self.path_download, f'{self.title}.torrent')
            self.url_torrent = url_torrent_peli
            self._download_file()
        # Series tienen lista de links
        else:
            logger.debug('Download serie')
            for i in url_torrent_serie:
                # obtengo unicamente el nombre del torrent
                self.title = i.split('/')[-1].split('.')[0]
                self.url_torrent = i
                self.path_file_torrent: Path = Path(self.path_download, f'{self.title}.torrent')
                self._download_file()

    def get_url_torrent(self, bot=None, message: str = None) -> Optional[List[str]]:
        """
        Funcion que obtiene la url torrent del la dirreccion que recibe,hay que tener en cuenta que la url que recibe es la
        del feed y que no es la apgina que contiene el torrent, pero como todas tienen la misma forma se modifica la url
        poniendole descarga-torrent

        :param str direcc: Dirreccion de la pagina web que contiene el torrent
        :param obj bot: bot
        :param obj message: instancia del mensaje recibido

        :return str: Nos devuelve el string con la url del torrent
        """
        if re.search("dontorrent", self.url_web):
            if bot is not None and message is not None:
                bot.reply_to(message, 'Buscando torrent en pctnew.com')

            req_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
                           'Content-Type': 'application/x-www-form-urlencoded'}

            session = requests.session()
            login = session.get(self.url_web, headers=req_headers, verify=False)
            sopa = BeautifulSoup(login.text, 'html.parser')
            mtable = sopa.findAll('table', {"class": "table table-sm table-striped text-center"})

            urls = re.findall(r'href=\"(//.*\.torrent)\"', str(mtable))

            new_urls: list = list()
            for i in urls:
                new_urls.append(f'https:{i}')
            return new_urls

        return None

    def get_url_torrent_dontorrent_direct(self, bot=None, message: str = None) -> Optional[str]:
        """
        es similar a al ade arriba pero solo busca un torrent especifico en un "a"
        """

        if re.search("dontorrent", self.url_web):
            if bot is not None and message is not None:
                bot.reply_to(message, 'Buscando torrent en pctnew.com')

            req_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
                           'Content-Type': 'application/x-www-form-urlencoded'}

            session = requests.session()
            login = session.get(self.url_web, headers=req_headers, verify=False)
            sopa = BeautifulSoup(login.text, 'html.parser')
            mtable = sopa.find('a',
                               {"class": "text-white bg-primary rounded-pill d-block shadow text-decoration-none p-1"})

            if mtable is not None:
                print(mtable['href'])
                print("################")
                return f'https:{mtable["href"]}'
            return None


if __name__ == '__main__':
    url1 = 'https://dontorrent.org/pelicula/21371/Mongol'
    url1 = 'https://dontorrent.org/serie/63845/63846/Batwoman-1-Temporada-720p'
    t = DonTorrent('test1', url1, PurePath('/home/procamora/Documents/Gestor-Series/'))
    print(t)
    print(t.get_url_torrent())
    print(t.get_url_torrent_dontorrent_direct())
    t.download_file_torrent()
    print(t)
