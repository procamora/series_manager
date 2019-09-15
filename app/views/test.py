#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class algo:
    def __init__(self):
        self.a = "A"
        self._b = "B"
        self.__c = "C"
        self.d = [1, 2, 3, 4]

    def otro(self):
        return "asd"

    def _privado(self):
        return "aasdasdsd"

    @property
    def b(self):
        return self._b


a = algo()
print(a.a)
print(a.b)
print(a.d)
