#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

# FIXME CAMBIAR NOMBRE POR model_serie??? o eliminar el model del resto
from dataclasses import dataclass
from typing import Dict

from app.models import Model


@dataclass
class Serie(Model):
    title: str = str()
    season: int = -1
    chapter: int = -1
    following: bool = bool()
    vose: bool = bool()
    finished: bool = bool()
    day: str = str()
    state: str = str()
    imdb_id: str = str()
    imdb_season: int = -1
    imdb_chapter: int = -1
    imdb_finished: int = -1
    imdb_following: bool = bool()
    chapter_downloaded: int = -1

    def get_season_chapter(self) -> str:
        if len(str(self.chapter)) == 1:
            return f'{self.season}x0{self.chapter}'
        else:
            return f'{self.season}x{self.chapter}'

    # def __str__(self) -> str:
    #    return (f'{self.__class__.__name__}('
    #            f'{self.name!r}, {self.season!r}x{self.chapter!r}, follow={self.following!r})')

    @staticmethod
    def load(dictionaty: Dict[str, str]) -> Serie:
        s = Serie()
        for i in dictionaty:
            if i == 'Nombre':
                s.title = dictionaty[i]
            elif i == 'Temporada':
                s.season = int(dictionaty[i])
            elif i == 'Capitulo':
                s.chapter = int(dictionaty[i])
            elif i == 'Siguiendo':
                s.following = Model.str_to_bool(dictionaty[i])
            elif i == 'VOSE':
                s.vose = Model.str_to_bool(dictionaty[i])
            elif i == 'Acabada':
                s.finished = Model.str_to_bool(dictionaty[i])
            elif i == 'Dia':
                s.day = dictionaty[i]
            elif i == 'Estado':
                s.state = dictionaty[i]
            elif i == 'imdb_id':
                s.imdb_id = dictionaty[i]
            elif i == 'imdb_Temporada':
                s.imdb_season = dictionaty[i]
            elif i == 'imdb_Capitulos':
                s.imdb_chapter = dictionaty[i]
            elif i == 'imdb_Finaliza':
                s.imdb_finished = dictionaty[i]
            elif i == 'imdb_seguir':
                s.imdb_following = Model.str_to_bool(dictionaty[i])
            elif i == 'Capitulo_Descargado':
                s._chapter_downloaded = dictionaty[i]
        return s

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Serie):
            return self.title == other.title
        return False
