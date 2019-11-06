#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import PurePath  # nueva forma de trabajar con rutas
from typing import NoReturn, Optional, List

import requests
from bs4 import BeautifulSoup

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: str = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

from app.models.model_t_torrent import Torrent
from app.models.model_t_feedparser import FeedParser
from app.models.model_t_feed import Feed
from app import logger


class FeedparserTorrentLocura(FeedParser):
    def __init__(self) -> NoReturn:
        self.entries: List[Feed] = list()

    @staticmethod
    def parse(url='https://torrentlocura.cc/ultimas-descargas/', category='1469',
              dat='Hoy') -> FeedparserTorrentLocura:
        """
        category='1469' series en hd
        """
        formdata = {'categoryIDR': category, 'date': dat}
        req_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
                       'Content-Type': 'application/x-www-form-urlencoded'}

        session = requests.session()
        login = session.post(url, data=formdata, headers=req_headers, verify=False)

        logger.critical(login)
        sopa = BeautifulSoup(login.text, 'html.parser')
        # sopa = BeautifulSoup(fichero, 'html.parser')
        result = sopa.findAll('ul', {"class": "noticias-series"})
        f = FeedparserTorrentLocura()
        for ul in result:
            for li in ul.findAll('li'):
                logger.critical(li.div.find('h2').text)
                logger.critical(li.a['href'])
                # FIXME CAMBIAR 44 Y 33 POR season Y chapter
                f.add(li.div.find('h2').text, 44, 33, li.a['href'])
                # f.add(li.a['title'], li.a['href'])
                # f.add(serie.text, int(chapters[-1]), url)

        logger.debug(f)

        # for i in f.entries:
        #    print(i.title)
        #    print(i.cap)
        #    print()

        return f


@dataclass
class TorrentLocura(Torrent):
    """
    """

    def download_file_torrent(self) -> NoReturn:
        self.url_torrent = self.get_url_torrent()
        self._download_file()

    def get_url_torrent(self, bot=None, message: str = None) -> Optional[str]:
        """
        Funcion que obtiene la url torrent del la dirreccion que recibe,hay que tener en cuenta que la url que recibe es
        la del feed y que no es la pagina que contiene el torrent, pero como todas tienen la misma forma se modifica la
        url poniendole descarga-torrent

        :param str direcc: Dirreccion de la pagina web que contiene el torrent
        :param obj bot: bot
        :param obj message: instancia del mensaje recibido

        :return str: Nos devuelve el string con la url del torrent
        """
        print(self.url_web)
        regex_recursion = "(tumejortorrent|newpct1|newpct)"

        if re.search("torrentlocura", self.url_web):
            if bot is not None and message is not None:
                bot.reply_to(message, 'Buscando torrent en torrentlocura.com')
            session = requests.session()

            comp1 = self.descarga_url_torrent_aux(
                session.get(self.url_web.replace('torrentlocura.cc/', 'torrentlocura.com/descarga-torrent/'),
                            verify=False).text)
            if comp1 is not None:
                return comp1

            # opcion 2
            comp2 = self.descarga_url_torrent_aux(
                session.get(self.url_web.replace('torrentlocura.cc/', 'torrentlocura.com/descargar-seriehd/'),
                            verify=False).text)
            if comp2 is not None:
                return comp2

            return None

        elif re.search(regex_recursion, self.url_web):
            return self.get_url_torrent(re.sub(regex_recursion, "torrentlocura", self.url_web), message)

    @staticmethod
    def descarga_url_torrent_aux(html_page: str) -> Optional[str]:
        try:
            sopa = BeautifulSoup(html_page, 'html.parser')
            result = sopa.find('a', {"class": "btn-torrent"})['href']
            # Si obtenemos una url es correcto sino buscamos en el codigo html
            regex = r"^(http://www\.|https://www\.|http://|https://)?[a-z0-9]+([\-\.][a-z0-9]+)*\.[a-z]{2,5}" \
                    r"(:[0-9]{1,5})?(\/.*)?$"
            if re.match(regex, result):
                return result
            else:  # FIXME USAR selenium para simular navegador
                """ si tiene puesto en href "javascript:void(0)" llamara a la funcion openTorrent() que tiene en la variable
                window.location.href la url del torrent a descaegar, por lo que lo buscamos a pelo en el html y eliminamos
                lo sobrante, feo pero funcional
                """
                javascript = re.findall(r'window\.location\.href = \".*\";', html_page)
                return javascript[0].replace("window.location.href = \"", "").replace("\";", "")
                # return sopa.find('div', {"id": "tab1"}).a['href']
        except Exception as e:
            print(e)
            return None


if __name__ == '__main__':
    url1 = 'torrentlocura.cc/descargar/cine-alta-definicion-hd/tolkien/'
    t = TorrentLocura('test1', url1, PurePath('/home/procamora/Documents/Gestor-Series/'))
    print(t)
    t.download_file_torrent()
    print(t)
