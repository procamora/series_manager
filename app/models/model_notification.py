#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Dict


class ModelNotification(object):
    name: str = str()
    api: str = str()
    active: bool = bool()

    @staticmethod
    def load(dictionaty: Dict) -> ModelNotification:
        s = ModelNotification()
        for i in dictionaty:
            if i == 'Nombre':
                s.name = dictionaty[i]
            elif i == 'API':
                s.api = dictionaty[i]
            elif i == 'Activo':
                s.active = bool(dictionaty[i])
        return s
