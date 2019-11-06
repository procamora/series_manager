#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import PurePath  # nueva forma de trabajar con rutas
from typing import NoReturn

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: str = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)


@dataclass
class Feed:
    title: str
    season: int  # Temporada
    chapter: int  # Capitulo
    link: str
    epi: str = str()  # formato de temporada y sesion TxS

    def __post_init__(self) -> NoReturn:

        if (len(str(self.chapter))) > 1:
            self.epi = f"{self.season}x{self.chapter}"
        else:
            self.epi = f"{self.season}x0{self.chapter}"

    # def __str__(self) -> NoReturn:
    #    return f'{self.title} - {self.chapter} - {self.link}'