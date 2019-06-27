#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import inspect


class Serie(object):
    def __init__(self) -> None:
        super().__init__()
        self._name = str()
        self._season = -1
        self._chapter = -1
        self._following = bool()
        self._vose = bool()
        self._finished = bool()
        self._day = str()
        self._state = str()
        self._imdb_id = str()
        self._imdb_season = -1
        self._imdb_chapter = -1
        self._imdb_finished = -1
        self._imdn_following = bool()
        self._chapter_downloaded = -1

    def __str__(self) -> str:
        attributes = inspect.getmembers(self, lambda a: not (inspect.isroutine(a)))
        [a for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))]

        new_attributes = Serie.delete_none_values(attributes[2][1])
        return str(new_attributes)

    @staticmethod
    def delete_none_values(attributes) -> dict:
        new_attributes = dict()
        new_attributes['class'] = 'Serie'
        for i in attributes:
            if isinstance(attributes[i], str) and len(attributes[i]) > 1:
                new_attributes[i] = attributes[i]
            elif isinstance(attributes[i], int) and attributes[i] != -1:
                new_attributes[i] = attributes[i]
        return new_attributes

    @staticmethod
    def load(dictionaty) -> object:
        s = Serie()
        for i in dictionaty:
            if i == 'Nombre':
                s._name = dictionaty[i]
            elif i == 'Temporada':
                s._season = int(dictionaty[i])
            elif i == 'Capitulo':
                s._chapter = int(dictionaty[i])
            elif i == 'Siguiendo':
                s._following = bool(dictionaty[i])
            elif i == 'VOSE':
                s._vose = dictionaty[i]
            elif i == 'Acabada':
                s._finished = bool(dictionaty[i])
            elif i == 'Dia':
                s._day = dictionaty[i]
            elif i == 'Estado':
                s._state = dictionaty[i]
            elif i == 'imdb_id':
                s._imdb_id = dictionaty[i]
            elif i == 'imdb_Temporada':
                s._imdb_season = dictionaty[i]
            elif i == 'imdb_Capitulos':
                s._imdb_chapter = dictionaty[i]
            elif i == 'imdb_Finaliza':
                s._imdb_finished = dictionaty[i]
            elif i == 'imdb_seguir':
                s._imdn_following = bool(dictionaty[i])
            elif i == 'Capitulo_Descargado':
                s._chapter_downloaded = dictionaty[i]
        return s
