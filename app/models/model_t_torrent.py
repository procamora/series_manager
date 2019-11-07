#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import PurePath, Path  # nueva forma de trabajar con rutas
from typing import NoReturn

import requests

from app import logger
from app.utils.settings import REQ_HEADERS


@dataclass
class Torrent(ABC, object):
    title: str
    url_web: str
    path_download: PurePath
    path_file_torrent: PurePath = PurePath()
    url_torrent: str = str()

    def __post_init__(self) -> NoReturn:
        """
        https://docs.python.org/3/library/dataclasses.html#post-init-processing
        :return:
        """
        if not re.match(r"^(https?://).*", self.url_web):
            #print('add http to url')
            self.url_web = f'http://{self.url_web}'
        self.path_file_torrent: Path = Path(self.path_download, f'{self.title}.torrent')

    def _download_file(self) -> NoReturn:
        # logger.debug(f'download url: {self.url_torrent}')
        r = requests.get(self.url_torrent, headers=REQ_HEADERS, verify=False)
        logger.info(f'download file: {self.path_file_torrent}')
        with open(str(self.path_file_torrent), "wb") as code:
            code.write(r.content)

    @abstractmethod
    def download_file_torrent(self) -> NoReturn:
        pass
