#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import inspect
from typing import NoReturn, Dict, List


class ModelStates(object):
    def __init__(self) -> NoReturn:
        super().__init__()
        self._state = str()

    def __str__(self) -> str:
        attributes = inspect.getmembers(self, lambda a: not (inspect.isroutine(a)))
        [a for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))]

        new_attributes = ModelStates.delete_none_values(attributes[2][1])
        return str(new_attributes)

    @staticmethod
    def delete_none_values(attributes: List) -> Dict:
        new_attributes = dict()
        new_attributes['class'] = 'ModelStates'
        for i in attributes:
            if isinstance(attributes[i], str) and len(attributes[i]) > 1:
                new_attributes[i] = attributes[i]
            elif isinstance(attributes[i], int) and attributes[i] != -1:
                new_attributes[i] = attributes[i]
        return new_attributes

    @staticmethod
    def load(dictionaty: Dict) -> ModelStates:
        s = ModelStates()
        for i in dictionaty:
            if i == 'Estados':
                s._state = dictionaty[i]
        return s
