#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import PurePath  # nueva forma de trabajar con rutas
from typing import NoReturn, Optional, List, Text, Dict

import requests
import urllib3
from bs4 import BeautifulSoup

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: Text = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

from app.models.model_t_torrent import Torrent
from app.models.model_t_feedparser import FeedParser
from app.models.model_t_feed import Feed
from app.utils.settings import REQ_HEADERS
from app import logger

urllib3.disable_warnings()

DOMAIN: Text = "descargas2020"
URL: Text = f'{DOMAIN}.org'


class FeedparserDescargas2020(FeedParser):
    def __init__(self: FeedparserDescargas2020) -> NoReturn:
        self.entries: List[Feed] = list()

    @staticmethod
    def parse(url: Text = f'https://{URL}/ultimas-descargas/', category: Text = '1469',
              dat: Text = 'Hoy') -> FeedparserDescargas2020:
        """
        category='1469' series en hd
        """
        formdata: Dict[Text] = {'categoryIDR': category, 'date': dat}
        session: requests.session = requests.session()
        login: session.post = session.post(url, data=formdata, headers=REQ_HEADERS, verify=False)

        # logger.critical(login)
        sopa: BeautifulSoup = BeautifulSoup(login.text, 'html.parser')
        # sopa = BeautifulSoup(fichero, 'html.parser')
        result: BeautifulSoup.element.ResultSet = sopa.findAll('ul', {"class": "noticias-series"})

        f: FeedparserDescargas2020 = FeedparserDescargas2020()
        ul: BeautifulSoup.element.Tag
        li: BeautifulSoup.element.Tag
        for ul in result:
            for li in ul.findAll('li'):
                # logger.critical(li.div.find('h2').text)
                # logger.critical(li.a['href'])
                # FIXME CAMBIAR 44 Y 33 POR season Y chapter
                f.add(li.div.find('h2').text, 44, 33, li.a['href'], li.div.find('h2').text)
                # f.add(li.a['title'], li.a['href'])
                # f.add(serie.text, int(chapters[-1]), url)

        logger.debug(f)

        # for i in f.entries:
        #    print(i.title)
        #    print(i.cap)
        #    print()

        return f


@dataclass
class Descargas2020(Torrent):
    """
    """

    def download_file_torrent(self: Descargas2020) -> NoReturn:
        self.url_torrent = self.get_url_torrent()
        self._download_file()

    def get_url_torrent(self: Descargas2020, bot=None, message: Text = None) -> Optional[Text]:
        """
        Funcion que obtiene la url torrent del la dirreccion que recibe,hay que tener en cuenta que la url que recibe es
        la del feed y que no es la pagina que contiene el torrent, pero como todas tienen la misma forma se modifica la
        url poniendole descarga-torrent

        :param obj bot: bot
        :param obj message: instancia del mensaje recibido

        :return str: Nos devuelve el string con la url del torrent
        """
        regex_recursion: Text = f"({DOMAIN})"

        if re.search(f"{DOMAIN}", self.url_web):
            if bot is not None and message is not None:
                bot.reply_to(message, f'Buscando torrent en {URL}')
            session: requests.session = requests.session()

            comp1: Optional[Text] = self.descarga_url_torrent_aux(session.get(self.url_web, verify=False).text)
            if comp1 is not None:
                return comp1

            # opcion 2
            # comp2: Optional[Text] = self.descarga_url_torrent_aux(
            #    session.get(self.url_web.replace(f'{self.url}/', f'{self.url}/descargar-seriehd/'),
            #                verify=False).text)
            # if comp2 is not None:
            #    return comp2
            return None

        elif re.search(regex_recursion, self.url_web):
            return self.get_url_torrent(re.sub(regex_recursion, DOMAIN, self.url_web), message)

    @staticmethod
    def descarga_url_torrent_aux(html_page: Text) -> Optional[Text]:
        """
        Metodo para obtener la url donde se encuentra el torrent dada una url.
        En caso de que este "camuflada" en una funcion javascript, se accedera a esa funcion y se buscara la url.
        :param html_page:
        :return:
        """
        try:
            sopa: BeautifulSoup = BeautifulSoup(html_page, 'html.parser')
            result: Text = sopa.find('a', {"class": "btn-torrent"})['href']
            # Si obtenemos una url es correcto sino buscamos en el codigo html
            if not re.search('javascript:', result):
                # return sopa.find('div', {"id": "tab1"}).a['href']
                return result
            else:
                """ si tiene puesto en href "javascript:" llamara a la funcion openTorrent() que tiene en la 
                variable window.location.href la url del torrent a descaegar, por lo que lo buscamos a pelo en el html 
                y eliminamos lo sobrante, feo pero funcional
                """
                javascript: List[Text] = re.findall(r'window\.location\.href = \".*\";', html_page)
                aux_url: Text = javascript[0].replace("window.location.href = \"", "").replace("\";", "")
                if not re.search('^https:', aux_url):
                    return f'https:{aux_url}'
                else:
                    return aux_url
        except Exception as e:
            logger.error(e)
            return None


if __name__ == '__main__':
    url1 = 'https://descargas2020.org/descargar/serie-en-hd/the-wall/temporada-1/capitulo-07/descargas2020-org'
    t = Descargas2020(title='test1', url_web=url1, path_download=PurePath('/home/procamora/Documents/Gestor-Series/'))
    print(t.get_url_torrent())
    # t.download_file_torrent()
    # print(t)

    f = FeedparserDescargas2020()
    # print(f.parse())
