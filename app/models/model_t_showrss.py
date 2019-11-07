#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from builtins import print
from dataclasses import dataclass
from pathlib import PurePath, Path  # nueva forma de trabajar con rutas
from typing import NoReturn

import feedparser
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: str = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

from app import logger
from app.models.model_t_torrent import Torrent
from app.models.model_t_feedparser import FeedParser

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


@dataclass
class FeedparserShowRss(FeedParser):
    regex: str = 'S(\d+).*E(\d+).*'

    @staticmethod
    def parse(url: str) -> FeedParser:
        feed_show: feedparser.FeedParserDict = FeedparserShowRss.feed_parser(url)

        f = FeedparserShowRss()
        for entrie in feed_show.entries:
            new_regex = f'{FeedparserShowRss.regex}'
            # Para obtener el titulo parto por el S00E00  (Mr Robot S04E05 1080p WEB x264 XLF)
            title: str = str(re.sub(new_regex, '', entrie.title, re.IGNORECASE))
            season = int(re.search(FeedparserShowRss.regex, entrie.title, re.IGNORECASE).group(1))
            chapter = int(re.search(FeedparserShowRss.regex, entrie.title, re.IGNORECASE).group(2))
            f.add(title, season, chapter, entrie.link)

        [logger.debug(f'-> {i}') for i in f.entries]
        return f

    @staticmethod
    def feed_parser(url) -> feedparser.FeedParserDict:
        """
        Da un fallo en fedora 23, por eso hace falta esta funcion
        https://github.com/kurtmckee/feedparser/issues/30
        """

        try:
            return feedparser.parse(url)
        except TypeError:
            if 'drv_libxml2' in feedparser.PREFERRED_XML_PARSERS:
                feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2')
                return feedparser.parse(url)
            else:
                raise


@dataclass
class ShowRss(Torrent):
    """
    """

    client_torrent: str = None

    @staticmethod
    def execute_command(binary: str, magnet: str) -> NoReturn:
        if binary is None:
            logger.critical("No se ha proporcionado un cliente torrent")
            sys.exit(1)

        command: str = f'{binary} {magnet}'
        logger.debug(f'execute_command: {command}')
        execute = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = execute.communicate()
        if len(stderr) != 0:
            logger.error(f"{binary} ha fallado añadiendo el magnet: {magnet}")

    def download_file_torrent(self) -> NoReturn:
        # Por herencia  se pone http:// pero los magnet no lo tienen y hay que borrarlo
        self.url_web = self.url_web[7:]
        try:
            self.magnet2torrent(self.url_web, str(self.path_download))
        except ModuleNotFoundError:
            self.execute_command(self.client_torrent, self.url_web)

        logger.info("FIN")
        # time.sleep(10)

    @staticmethod
    def magnet2torrent(magnet: str, path_download: str):
        """
        https://github.com/xrgtn/mag2tor
        :param magnet:
        :param path_download:
        :return:
        """
        import libtorrent
        logger.info(magnet)
        logger.info(path_download)
        sess = libtorrent.session()
        prms = {
            'save_path': path_download,
            # 'storage_mode':libtorrent.storage_mode_t(2),
            'paused': False,
            'auto_managed': False,
            'upload_mode': True,
        }
        torr = libtorrent.add_magnet_uri(sess, magnet, prms)
        while not torr.has_metadata():
            logger.debug('.')
            time.sleep(0.1)
        sess.pause()
        tinf = torr.get_torrent_info()

        path_file_torrent: Path = Path(path_download, f'{tinf.name()}.torrent')
        logger.info('write: ' + str(path_file_torrent))
        path_file_torrent.write_bytes(libtorrent.bencode(libtorrent.create_torrent(tinf).generate()))

        sess.remove_torrent(torr)


if __name__ == '__main__':
    # url1 = 'https://grantorrent.tv/series-2/jack-ryan-temporada-2/'
    # url1 = 'https://grantorrent.tv/series-2/gotham-temporada-5/'
    url1 = "magnet:?xt=urn:btih:834DAC50F4F3C8F167C72EDF913FA9E36CF79AF5&dn=Mr+Robot+S04E05+1080p+WEB+x264+XLF&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce"
    t = ShowRss('mia1', url1, PurePath('/home/procamora/Documents/Gestor-Series/'))
    t.download_file_torrent()
    print(t)
    print("##############")
