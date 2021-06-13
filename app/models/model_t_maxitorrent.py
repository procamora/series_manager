#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path  # nueva forma de trabajar con rutas
from typing import Optional, List, Text
from datetime import datetime

import requests
import urllib3
from bs4 import BeautifulSoup

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: Path = Path(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: Text = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

from app.models.model_t_feedparser import FeedParser
from app.models.model_t_torrent import Torrent
from app.models.model_t_feed import Feed
from app.utils.settings import REQ_HEADERS
from app import logger

urllib3.disable_warnings()

DOMAIN: Text = "maxitorrent"
URL: Text = f'{DOMAIN}.com'


@dataclass
class FeedparserMaxitorrent(FeedParser):
    entries: List[Feed] = field(default_factory=list)
    # FIXME ahora mismo no lo uso porque no veo series que salgan con la temporada completa
    # cuando salgan detectarlo y mofificar el number
    NUMBER: int = 99  # INDICA QUE ES UNA TEMPORADA COMPLETA

    @staticmethod
    def parse(url: Text = f'https://{URL}/ultimas-descargas/') -> FeedparserMaxitorrent:
        session: requests.session = requests.session()
        all_html: session.post = session.get(url, headers=REQ_HEADERS, verify=False)

        sopa: BeautifulSoup = BeautifulSoup(all_html.text, 'html.parser')
        result: BeautifulSoup.element.ResultSet = sopa.findAll('ul')

        feed: FeedparserMaxitorrent = FeedparserMaxitorrent()
        ul: BeautifulSoup.element.Tag
        for ul in result:
            if not ul.findAll('img'):
                continue  # skip ul other actions
            # foreach all (movies, tv shows, etc)
            li: BeautifulSoup.element.Tag
            for li in ul.findAll('li'):
                # filter quality 720p
                if re.search(r'720p', li.div.span.text, re.IGNORECASE):
                    link: Text = f"{URL}{li.a['href']}"
                    original_name: Text = li.div.find('a').text.strip()
                    # check if 1 chapter or more
                    if re.search(r'Capitulos ', original_name, re.IGNORECASE):
                        chapter: int = int(re.findall(r'\d+', original_name)[-1])
                        title: Text = re.sub(r'- Temp.*', '', original_name).strip()
                    elif re.search(r'Capitulo ', original_name, re.IGNORECASE):
                        chapter: int = int(re.search(r'Capitulo (\d+)', original_name, re.IGNORECASE).group(1))
                        title: Text = re.sub(r'Temp\. \d+ Capitulo \d+', '', original_name).strip()
                    else:
                        continue  # skip if not detect capitulo

                    season: int = int(re.search(r'Temp. (\d+)', original_name, re.IGNORECASE).group(1))
                    feed.add(title, season, chapter, link, original_name)

            return feed

    def __str__(self) -> Text:
        response: Text = str()
        for i in self.entries:
            response += f'{i.title} -> {i.epi}\n'
        return response


@dataclass
class Maxitorrent(Torrent):

    def __post_init__(self):
        if not re.search(r'/torrent/', self.url_web, re.IGNORECASE):
            self.url_web = re.sub(r'descargar/', 'descargar/torrent/', self.url_web)
        logger.debug(self.url_web)

    def download_file_torrent(self: Maxitorrent, random_name: bool = False) -> Optional[bool]:
        self.url_torrent = self.get_url_torrent()
        if self.url_torrent is None:
            return False

        if random_name:
            now = datetime.now()  # current date and time
            uniq: Text = now.strftime("%Y%d%m_%H%M%S_%f")
            self.path_file_torrent = Path(self.path_file_torrent.parent, f'{uniq}_{str(self.path_file_torrent.name)}')

        # fixme pendiente hde hacer algo estigo grantorrent para obtener una lista de torrents
        self._download_file()
        return True

    def get_url_torrent(self: Maxitorrent, bot=None, message: Text = None) -> Optional[Text]:
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
        else:
            logger.warning(f"not found {self.url_web}")

    @staticmethod
    def descarga_url_torrent_aux(html_page: Text) -> Optional[Text]:
        """
        Metodo para obtener la url donde se encuentra el torrent dada una url.
        En caso de que este "camuflada" en una funcion javascript, se accedera a esa funcion y se buscara la url.
        :param html_page:
        :return:
        """
        # logger.info(html_page)
        # https://maxitorrent.com/descargar/cine-alta-definicion-hd/possessor/bluray-microhd/
        # https://maxitorrent.com/descargar/torrent/cine-alta-definicion-hd/possessor/bluray-microhd/

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
    url1 = 'https://maxitorrent.com/descargar/cine-alta-definicion-hd/possessor/bluray-microhd/'
    t = Maxitorrent(title='test1', url_web=url1, path_download=Path('./'))
    print(t.get_url_torrent())
    # t.download_file_torrent()
    # print(t)

    f1 = FeedparserMaxitorrent()
    # f1.parse()
    print(f1.parse())
