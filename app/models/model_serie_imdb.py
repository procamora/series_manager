#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SerieImdb:
    """
    Clase auxiliar que contiene los datos obtenidos de imdb
    """
    title: str
    season: int
    chapter: int
    year: int
    id: str
