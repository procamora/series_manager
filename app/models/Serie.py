#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Serie(object):
    def __init__(self) -> None:
        super().__init__()
        self.__name = str()
        self.__season = int()
        self.__chapter = int()
        self.__following = bool()
        self.__vose = bool()
        self.__finished = bool()
        self.__day = str()
        self.__imdb_id = str()
        self.__imdb_season = int()
        self.__imdb_chapter = int()
        self.__imdb_finished = int()
        self.__imdn_following = bool()
        self.__chapter_downloaded = int()
