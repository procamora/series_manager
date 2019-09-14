#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import inspect
from typing import NoReturn, Dict, List


class ModelPreference(object):
    def __init__(self) -> NoReturn:
        super().__init__()
        self._id = int()
        self._url_feed = str()
        self._url_feed_vose = str()
        self._path_download = str()

    def __str__(self) -> str:
        attributes = inspect.getmembers(self, lambda a: not (inspect.isroutine(a)))
        [a for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))]

        new_attributes = ModelPreference.delete_none_values(attributes[2][1])
        return str(new_attributes)

    @staticmethod
    def delete_none_values(attributes: List) -> Dict:
        new_attributes = dict()
        new_attributes['class'] = 'ModelPreference'
        for i in attributes:
            if isinstance(attributes[i], str) and len(attributes[i]) > 1:
                new_attributes[i] = attributes[i]
            elif isinstance(attributes[i], int) and attributes[i] != -1:
                new_attributes[i] = attributes[i]
        return new_attributes

    @staticmethod
    def load(dictionaty: Dict) -> ModelPreference:
        s = ModelPreference()
        for i in dictionaty:
            if i == 'ID':
                s._id = int(dictionaty[i])
            elif i == 'UrlFeedNewpct':
                s._url_feed = dictionaty[i]
            elif i == 'UrlFeedShowrss':
                s._url_feed_vose = dictionaty[i]
            elif i == 'RutaDescargas':
                s._path_download = dictionaty[i]
        return s
