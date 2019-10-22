#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from app.models import Model
from pathlib import Path, PurePath  # nueva forma de trabajar con rutas


@dataclass
class Preferences(Model):
    id: int = int()
    url_feed: str = str()
    url_feed_vose: str = str()
    path_download: Path = Path()

    @staticmethod
    def load(dictionaty: Dict[str, str]) -> Preferences:
        preferences = Preferences()
        for i in dictionaty:
            if i == 'id':
                preferences.id = int(dictionaty[i])
            elif i == 'UrlFeedNewpct':
                preferences.url_feed = dictionaty[i]
            elif i == 'UrlFeedShowrss':
                preferences.url_feed_vose = dictionaty[i]
            elif i == 'RutaDescargas':
                preferences.path_download = Path(dictionaty[i])
        return preferences
