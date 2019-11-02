#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import NoReturn

import requests
from bs4 import BeautifulSoup


@dataclass
class TorrentLocura:
    """
    """
    url: str

    def __post_init__(self) -> NoReturn:
        """
        https://docs.python.org/3/library/dataclasses.html#post-init-processing
        :return:
        """
        if not re.match(r"^(http://).*", self.url):
            self.url = f'http://{self.url}'

    def download_file_torrent(self):
        pass

    def get_url_torrent(self, bot=None, message=None):
        """
        Funcion que obtiene la url torrent del la dirreccion que recibe,hay que tener en cuenta que la url que recibe es
        la del feed y que no es la pagina que contiene el torrent, pero como todas tienen la misma forma se modifica la
        url poniendole descarga-torrent

        :param str direcc: Dirreccion de la pagina web que contiene el torrent
        :param obj bot: bot
        :param obj message: instancia del mensaje recibido

        :return str: Nos devuelve el string con la url del torrent
        """
        print(self.url)
        regex_recursion = "(tumejortorrent|newpct1|newpct)"

        if re.search("torrentlocura", self.url):
            if bot is not None and message is not None:
                bot.reply_to(message, 'Buscando torrent en torrentlocura.com')
            session = requests.session()

            comp1 = self.descarga_url_torrent_aux(
                session.get(self.url.replace('torrentlocura.com/', 'torrentlocura.com/descarga-torrent/'),
                            verify=False).text)
            if comp1 is not None:
                return comp1

            # opcion 2
            comp2 = self.descarga_url_torrent_aux(
                session.get(self.url.replace('torrentlocura.com/', 'torrentlocura.com/descargar-seriehd/'),
                            verify=False).text)
            if comp2 is not None:
                return comp2

            return None

        elif re.search(regex_recursion, self.url):
            return self.get_url_torrent(re.sub(regex_recursion, "torrentlocura", self.url), message)

    def descarga_url_torrent_aux(self, page):
        try:
            sopa = BeautifulSoup(page, 'html.parser')
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
                javascript = re.findall(r'window\.location\.href = \".*\";', page)
                return javascript[0].replace("window.location.href = \"", "").replace("\";", "")
                # return sopa.find('div', {"id": "tab1"}).a['href']
        except Exception as e:
            print(e)
            return None


if __name__ == '__main__':
    url1 = 'torrentlocura.com/descargar/cine-alta-definicion-hd/tolkien/'
    t = TorrentLocura(url1)
    print(t)
    print(t.get_url_torrent())
