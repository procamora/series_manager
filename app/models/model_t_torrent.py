#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import PurePath, Path  # nueva forma de trabajar con rutas
from typing import NoReturn, Text

import requests

from app import logger
from app.utils.settings import REQ_HEADERS


@dataclass
class Torrent(ABC, object):
    title: Text
    url_web: Text
    path_download: Path
    path_file_torrent: Path = PurePath()
    url_torrent: Text = str()

    def __post_init__(self: Torrent) -> NoReturn:
        """
        https://docs.python.org/3/library/dataclasses.html#post-init-processing
        :return:
        """
        if not re.match(r"^(https?://).*", self.url_web):
            #logger.warning('add http to url')
            self.url_web = f'https://{self.url_web}'
        self.path_file_torrent: Path = Path(self.path_download, f'{self.title}.torrent')

    def _download_file(self: Torrent) -> NoReturn:
        # logger.debug(f'download url: {self.url_torrent}')
        if not isinstance(self.url_torrent, str):
            logger.critical("url is not valid")
            return
        r: requests.Response = requests.get(self.url_torrent, headers=REQ_HEADERS, verify=False)
        logger.info(f'download file: {self.path_file_torrent}')
        uniq_path = Path(self.path_file_torrent.parent, str(self.path_file_torrent))

        with uniq_path.open('wb') as code:
            code.write(r.content)

    @abstractmethod
    def download_file_torrent(self: Torrent) -> NoReturn:
        pass
