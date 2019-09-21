#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import glob
import os
from abc import ABC, abstractmethod
from typing import Dict

__all__ = [os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__) + "/*.py")]


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
