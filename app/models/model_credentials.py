#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from app.models import Model


@dataclass
class Credentials(Model):
    # id: int = int()
    user_tviso: str = str()
    pass_tviso: str = str()
    api_telegram: str = str()

    @staticmethod
    def load(dictionaty: Dict[str, str]) -> Credentials:
        credentials = Credentials()
        for i in dictionaty:
            if i == 'id':
                credentials.id = int(dictionaty[i])
            elif i == 'user_tviso':
                credentials.user_tviso = dictionaty[i]
            elif i == 'pass_tviso':
                credentials.pass_tviso = dictionaty[i]
            elif i == 'api_telegram':
                credentials.api_telegram = dictionaty[i]
        return credentials
