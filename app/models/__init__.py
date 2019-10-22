#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path, PurePath  # nueva forma de trabajar con rutas
from typing import Dict

# Metodo para encontrarar todos los ficheros e importarlos
absolut_path = PurePath(__file__)  # Ruta absoluta de este fichero
# Path(absolut_path.parent)     # Obtenemos el directorio donde esta el fichero
# glob("*.py")                  # Buscamos todos los ficheros con extension py
# PurePath(str(f)).stem         # Para cada fichero solo obtenemos su nombre (sin extension y ruta)
__all__ = [PurePath(str(f)).stem for f in Path(absolut_path.parent).glob("*.py")]


class Model(ABC, object):

    @staticmethod
    @abstractmethod
    def load(dictionaty: Dict[str, str]) -> Model:
        """
        Metodo para crear un objeto a partir de un diccionario
        :param dictionaty:
        :return Model:
        """

    @staticmethod
    def str_to_bool(v):
        return v.lower() in ("yes", "true", "t", "1", "si")
