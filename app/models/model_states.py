#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from app.models import Model


@dataclass
class States(Model):
    id: int = int()
    state: str = str()

    # def __str__(self) -> str:
    #    attributes = inspect.getmembers(self, lambda a: not (inspect.isroutine(a)))
    #    [a for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))]
    #   new_attributes = ModelStates.delete_none_values(attributes[2][1])
    #    return str(new_attributes)

    # @staticmethod
    # def delete_none_values(attributes: List) -> Dict:
    #    new_attributes = dict()
    #    new_attributes['class'] = 'ModelStates'
    #    for i in attributes:
    #        if isinstance(attributes[i], str) and len(attributes[i]) > 1:
    #            new_attributes[i] = attributes[i]
    #        elif isinstance(attributes[i], int) and attributes[i] != -1:
    #            new_attributes[i] = attributes[i]
    #    return new_attributes

    @staticmethod
    def load(dictionaty: Dict[str, str]) -> States:
        states: States = States()
        for i in dictionaty:
            if i == 'Estados':
                states.state = dictionaty[i]
            elif i == 'ID':
                states.id = dictionaty[i]
        return states
