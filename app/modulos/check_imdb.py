#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from app.modulos.actualiza_imdb import actualizaImdb

from app import logger

a = actualizaImdb()
# logger.info((a.compruebaTitulo('tt1475582')))
# """
logger.info('actualizaTemporadas')
# actualizar_insertar series con mod parcial(todas lases series siguiendo,
# tarda bastante)
a.actualizaTemporadas()
logger.info('actulizaCompleto')
a.actulizaCompleto()
logger.info('actualizaSerie')
# a.actualizaSerie('tt3551096')
# """				# actualizar_insertar series que no tienen datos de capitulo/temporada de imdb
a.series_finalizadas()
