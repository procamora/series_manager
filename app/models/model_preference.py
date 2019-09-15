#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Dict


class ModelPreference(object):
    id: int = int()
    url_feed: str = str()
    url_feed_vose: str = str()
    path_download: str = str()

    @staticmethod
    def load(dictionaty: Dict) -> ModelPreference:
        s = ModelPreference()
        for i in dictionaty:
            if i == 'ID':
                s.id = int(dictionaty[i])
            elif i == 'UrlFeedNewpct':
                s.url_feed = dictionaty[i]
            elif i == 'UrlFeedShowrss':
                s.url_feed_vose = dictionaty[i]
            elif i == 'RutaDescargas':
                s.path_download = dictionaty[i]
        return s
