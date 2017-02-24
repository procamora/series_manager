#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from modulos.actualiza_imdb import actualizaImdb


a = actualizaImdb()
# print((a.compruebaTitulo('tt1475582')))
#'''
print('actualizaTemporadas')
# actualizar_insertar series con mod parcial(todas lases series siguiendo,
# tarda bastante)
a.actualizaTemporadas()
print('actulizaCompleto')
a.actulizaCompleto()
print('actualizaSerie')
# a.actualizaSerie('tt3551096')
#'''				# actualizar_insertar series que no tienen datos de capitulo/temporada de imdb
a.series_finalizadas()
