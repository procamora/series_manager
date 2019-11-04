#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import sys
import time
from builtins import print
from dataclasses import dataclass, field
from pathlib import PurePath, Path  # nueva forma de trabajar con rutas
from typing import NoReturn, List

import libtorrent
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: str = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

from app import logger
from app.models.model_torrent import Torrent
from app.models.model_feed import Feed

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


@dataclass
class FeedparserPropio():
    entries: List[Feed] = field(default_factory=list)

    @staticmethod
    def parse(url: str = 'https://grantorrent.tv/series-2/') -> FeedparserPropio:
        f = FeedparserPropio()
        return f


@dataclass
class ShowRss(Torrent):
    """
    """

    def download_file_torrent(self) -> NoReturn:
        # Por herencia  se pone http:// pero los magnet no lo tienen y hay que borrarlo
        self.url_web = self.url_web[7:]
        self.magnet2torrent(self.url_web, str(self.path_download))
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
