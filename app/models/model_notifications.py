#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from app.models import Model


@dataclass
class Notifications(Model):
    id: int = int()
    name: str = str()
    api: str = str()
    active: bool = bool()

    @staticmethod
    def load(dictionaty: Dict) -> Notifications:
        notifications = Notifications()
        for keys in dictionaty:
            if keys == 'ID':
                notifications.id = int(dictionaty[keys])
            elif keys == 'Nombre':
                notifications.name = dictionaty[keys]
            elif keys == 'API':
                notifications.api = dictionaty[keys]
            elif keys == 'Activo':
                notifications.active = Model.str_to_bool(dictionaty[keys])
        return notifications
