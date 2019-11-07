#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import PurePath, Path  # nueva forma de trabajar con rutas
from typing import Optional, List

import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: str = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

from app.utils.settings import REQ_HEADERS
from app.models.model_t_torrent import Torrent
from app.models.model_t_feedparser import FeedParser
from app import logger

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


@dataclass
class FeedparserGranTorrent(FeedParser):
    NUMBER: int = 99  # INDICA QUE ES UNA TEMPORADA COMPLETA

    @staticmethod
    def parse(url: str = 'https://grantorrent.tv/series-2/') -> FeedParser:
        """
        """
        session = requests.session()
        login = session.get(url, headers=REQ_HEADERS, verify=False)

        if login.status_code != 200:
            logger.critical(f"Status code get({login}) is: {login.status_code}")
            sys.exit(1)

        sopa = BeautifulSoup(login.text, 'html.parser')
        all_box = sopa.findAll('div', {"class": "contenedor-home"})
        f = FeedparserGranTorrent()

        for box in all_box[1].findAll('div', {'class': 'imagen-post'}):
            url = box.a['href']
            name = box.find("div", {"class": "bloque-inferior"}).text.strip()
            regex = r'(.*)( )+((\d+).(\d+))'
            regex_response = re.search(regex, name)
            # logger.debug(name)
            # Series con capitulo o capitulos: Navy  17×02 or Keeping 2×05-06
            if regex_response is not None:
                chapter = int(re.search(regex, name).group(5))
            # Series que tiene la temporada completa
            else:
                regex = r'(.*)( )+(Temporada (\d+) Completa)'
                regex_response = re.search(regex, name)
                chapter = FeedparserGranTorrent.NUMBER

            title = regex_response.group(1)
            season = int(re.search(regex, name).group(4))
            f.add(title, season, chapter, url)

        [logger.debug(f'-> {i}') for i in f.entries]
        return f


@dataclass
class GranTorrent(Torrent):
    """
    """

    def download_file_torrent(self) -> bool:
        """
        Metodo para descargar un fichero torrent, primero obtiene la url donde se encuentra
        :return: bool indicando si se ha obtenido con existo o no
        """
        url_torrent_serie = self.get_url_torrent()

        if url_torrent_serie is None:
            return False

        for i in url_torrent_serie:
            # obtengo unicamente el nombre del torrent
            self.title = i.split('/')[-1].split('.')[0]
            self.url_torrent = i
            self.path_file_torrent: Path = Path(self.path_download, f'{self.title}.torrent')
            self._download_file()
        return True

    def get_url_torrent(self, bot=None, message: str = None) -> Optional[List[str]]:
        """
        Funcion que obtiene la url torrent del la dirreccion que recibe,hay que tener en cuenta que la url que recibe es la
        del feed y que no es la apgina que contiene el torrent, pero como todas tienen la misma forma se modifica la url
        poniendole descarga-torrent

        :param obj bot: bot
        :param obj message: instancia del mensaje recibido

        :return str: Nos devuelve el string con la url del torrent
        """
        if re.search("grantorrent", self.url_web):
            if bot is not None and message is not None:
                bot.reply_to(message, 'Buscando torrent en grantorrent.tv')

            session = requests.session()
            login = session.get(self.url_web, headers=REQ_HEADERS, verify=False)
            sopa = BeautifulSoup(login.text, 'html.parser')
            mtable = sopa.findAll('table', {"class": "demo"})
            new_urls: list = list()

            if len(mtable) == 0:  # Si es 0 falla al parseo de la web, puede que este mal la url
                return None

            for tr in mtable[0].findAll('tr', {"class": "lol"}):
                tds = tr.findAll('td')
                # Series
                if re.search('720p', tds[2].text, re.IGNORECASE):
                    # print(tds[1].text) # Episodio
                    # print(tds[2].text) # Calidad
                    # print(tds[3].a['href']) #Enlace
                    new_urls.append(tds[3].a['href'])
                # Peliculas
                if re.search('MicroHD-1080p', tds[1].text, re.IGNORECASE):
                    new_urls.append(tds[3].a['href'])
            return new_urls

        return None


if __name__ == '__main__':
    # url1 = 'https://grantorrent.tv/series-2/jack-ryan-temporada-2/'
    # url1 = 'https://grantorrent.tv/series-2/gotham-temporada-5/'
    url1 = 'https://grantorrent.tv/toy-story-4/'
    url1 = 'https://grantorrent.tv/series-2/la-materiada-1/'
    t = GranTorrent('test1', url1, PurePath('/home/procamora/Documents/Gestor-Series/'))
    print(t.get_url_torrent())
    t.download_file_torrent()
    print(t)
    print("##############")
    FeedparserGranTorrent.parse()
