#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys


class algo():
    def __init__(self):
        self.a = "A"
        self._b = "B"
        self.__c = "C"

    def otro(self):
        return ("asd")

    def _privado(self):
        return ("aasdasdsd")


a = algo()
print(a.a)
print(a.otro())
print(a._privado())
