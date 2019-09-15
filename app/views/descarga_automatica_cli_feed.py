#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

"""
import os
import re
import time

import feedparser

from app import logger
from app.modulos import funciones
from app.modulos.connect_sqlite import conection_sqlite, execute_script_sqlite
from app.modulos.mail2 import ML2
from app.modulos.pushbullet2 import PB2
from app.modulos.settings import directorio_trabajo, ruta_db
from app.modulos.telegram2 import TG2

# https://gist.github.com/kaotika/e8ca5c340ec94f599fb2

SERIE_DEBUG = "NoAtlantis"


class DescargaAutomaticaCli:
    def __init__(self, database=None):
        if funciones.internet_on():
            if database is None:  # en herencia no mando ruta
                self.db = ruta_db
            else:
                self.db = database

            self.notificaciones = self.muestraNotificaciones()  # variable publica

            self.query = """SELECT Nombre, Temporada, Capitulo, VOSE FROM Series WHERE Siguiendo = "Si"
                          ORDER BY Nombre ASC"""
            self.series = conection_sqlite(self.db, self.query, True)

            self.listaNotificaciones = str()
            self.actualizaDia = str()
            self.conf = funciones.db_configuarion()

            url_new = self.conf['UrlFeedNewpct']
            url_show = self.conf['UrlFeedShowrss']

            # Diccionario con las series y capitulos para actualizar la bd el capitulo descargado
            self.capDescargado = dict()
            self.consultaUpdate = str()
            self.rutlog = str()

            try:
                self.feedNew = feedparser.parse(url_new)
            except TypeError:  # Para el fallo en fedora
                self.feedNew = funciones.feed_parser(url_new)

            try:
                self.feedShow = feedparser.parse(url_show)
            except TypeError:  # Para el fallo en fedora
                self.feedShow = funciones.feed_parser(url_show)

            self.consultaSeries = conection_sqlite(self.db, self.query, True)

    def run(self):
        serie_actual_new = str()
        serie_actual_show = str()
        # SerieActualTemp = str()

        fich_newpct = self.conf['FicheroFeedNewpct']
        fich_showrss = self.conf['FicheroFeedShowrss']
        self.rutlog = r'{}/log'.format(directorio_trabajo)

        if not os.path.exists(self.rutlog):
            os.mkdir(self.rutlog)

        if not os.path.exists('{}/{}'.format(self.rutlog, fich_newpct)):
            funciones.create_file('{}/{}'.format(self.rutlog, fich_newpct))

        if not os.path.exists('{}/{}'.format(self.rutlog, fich_showrss)):
            funciones.create_file('{}/{}'.format(self.rutlog, fich_showrss))

        with open('{}/{}'.format(self.rutlog, fich_newpct), 'r') as f:
            self.ultimaSerieNew = f.readline()

        with open('{}/{}'.format(self.rutlog, fich_showrss), 'r') as f:
            self.ultimaSerieShow = f.readline()

        for i in self.consultaSeries:
            try:
                logger.info(('Revisa: {}'.format(funciones.remove_tildes(i['Nombre']))))
                serie_actual_temp = self.parseaFeed(
                    i['Nombre'], i['Temporada'], i['Capitulo'], i['VOSE'])
                if i['VOSE'] == 'Si':
                    serie_actual_show = serie_actual_temp
                else:
                    serie_actual_new = serie_actual_temp
            except Exception as e:
                logger.error('################', i['Nombre'], ' FALLO: ', e)

        if len(self.ultimaSerieNew) != 0:  # or len(self.ultimaSerieShow) != 0:
            logger.info(self.actualizaDia)
            # actualiza los dias en los que sale el capitulo
            execute_script_sqlite(self.db, self.actualizaDia)

            for notif in self.notificaciones:
                if notif['Activo'] == 'True':
                    if notif['Nombre'] == 'Telegram':
                        tg3.send_tg(self.listaNotificaciones)
                    elif notif['Nombre'] == 'Pushbullet':
                        pb3.send_text_pb('Gestor series', self.listaNotificaciones)

        # capitulos que descargo
        for i in self.capDescargado.items():
            # logger.info(i)
            query = 'UPDATE Series SET Capitulo_Descargado={} WHERE Nombre LIKE "{}";\n'.format(str(i[1]), i[0])
            self.consultaUpdate += query

        logger.info(self.consultaUpdate)
        # actualiza el ultimo capitulo que he descargado
        execute_script_sqlite(self.db, self.consultaUpdate)

        # Guardar ultima serie del feed
        if serie_actual_show is not None and serie_actual_new is not None:
            with open('{}/{}'.format(self.rutlog, fich_newpct), 'w') as f:
                f.write(funciones.remove_tildes(serie_actual_new))
            with open('{}/{}'.format(self.rutlog, fich_showrss), 'w') as f:
                f.write(funciones.remove_tildes(serie_actual_show))
        else:
            logger.warning('PROBLEMA CON if SerieActualShow is not None and SerieActualNew is not None:')

    def parseaFeed(self, serie, tem, cap, vose):
        """Solo funciona con series de 2 digitos por la expresion regular"""
        cap = str(cap)
        ruta = str(self.conf['RutaDescargas'])  # es unicode
        if vose == 'Si':
            ultima_serie = self.ultimaSerieShow
            d = self.feedShow
        else:
            ultima_serie = self.ultimaSerieNew
            d = self.feedNew

        if not os.path.exists(ruta):
            os.mkdir(ruta)

        if len(str(cap)) == 1:
            cap = '0' + str(cap)

        for i in d.entries:
            self.titleSerie = funciones.remove_tildes(i.title)
            # cuando llegamos al ultimo capitulo pasamos a la siguiente serie
            # logger.info(self.titleSerie, ".........", ultimaSerie, ".FIN")
            if self.titleSerie == ultima_serie:
                # retornamos el valor que luego usaremos en ultima serie para guardarlo en el fichero
                return funciones.remove_tildes(d.entries[0].title)

            regex_vose = r'(?i){} ({}|{}|{}).*'.format(funciones.scapes_parenthesis(serie.lower()), tem, tem + 1, tem + 2)
            regex_cast = r'(?i){}( \(Proper\))?( )*- Temporada( )?\d+ \[HDTV 720p?\]\[Cap\.({}|{}|{})\d+(_\d+)?\]\[A.*' \
                .format(funciones.scapes_parenthesis(serie.lower()), tem, tem + 1, tem + 2)

            if serie.lower() == SERIE_DEBUG.lower():
                logger.info('{}->{}'.format(regex_cast, self.titleSerie))
                logger.info(i.link)

            estado = False
            if vose == 'Si':
                if re.search(regex_vose, self.titleSerie):
                    estado = True
            else:
                if re.search(regex_cast, self.titleSerie):
                    estado = True

            if estado:
                title_serie = self.titleSerie  # conversion necesaria para usar como str
                if vose == 'Si':
                    torrent = i.link
                else:
                    torrent = funciones.descargaUrlTorrent(i.link)

                try:  # arreglar problema codificacion de algunas series
                    logger.info(title_serie)
                except Exception:
                    title_serie = title_serie.replace(u"\uFFFD", "?")

                if not os.path.exists(u'{}{}.torrent'.format(ruta, title_serie)):
                    fichero_descargas = self.conf['FicheroDescargas']
                    with open('{}/{}'.format(self.rutlog, fichero_descargas), 'a') as f:
                        f.write('{} {}\n'.format(time.strftime('%Y%m%d'), title_serie))

                    if vose == 'Si':
                        self.accionExtra(title_serie)
                        # creo un string para solo mandar una notificacion
                        self.listaNotificaciones += '{}\n'.format(title_serie)
                    else:
                        # En pelis que son VOSE no se si da fallo, esto solo es para no VOSE
                        var_nom = self.titleSerie.split('-')[0]
                        var_epi = self.titleSerie.split('][')[1]
                        self.accionExtra('{} {}'.format(var_nom, var_epi))
                        # creo un string para solo mandar una notificacion
                        self.listaNotificaciones += '{} {}\n'.format(var_nom, var_epi)
                    funciones.download_file(torrent, r'{}/{}.torrent'.format(ruta, str(title_serie)))
                    # Diccionario con todos los capitulos descargados, para actualizar la bd con los capitulos por
                    # donde voy regex para coger el capitulo unicamente
                    self.actualizaDia += """\nUPDATE series SET Dia="{}" WHERE Nombre LIKE "{}";""".format(
                        funciones.calculate_day_week(), serie)

                    capitulo_actual = var_epi[-2:]  # mas eficiente, el otro metodo falla con multiples series: 206_209
                    # capituloActual = int(re.sub('Cap\.{}'.format(tem), '', varEpi))
                    if serie not in self.capDescargado:
                        self.capDescargado[serie] = capitulo_actual
                    else:
                        # REVISAR, CREO QUE ESTA MAL NO ES 4X05 ES 405
                        if self.capDescargado[serie] < capitulo_actual:
                            self.capDescargado[serie] = capitulo_actual

                logger.info(('DESCARGANDO: {}'.format(serie)))

        return funciones.remove_tildes(d.entries[0].title)

    def accionExtra(self, serie):
        """
        Metodo que no hace nada en esta clase pero que en herencia es
        usado para usar el entorno ggrafico que QT
        :return:
        """
        pass

    def getSeries(self):
        return self.consultaSeries

    def getSerieActual(self):
        return self.titleSerie

    @staticmethod
    def muestraNotificaciones():
        """
        poner las api de la base de datos
        """
        query_n = 'SELECT * FROM notificaciones'
        datos = conection_sqlite(ruta_db, query_n, True)

        global tg3, pb3, ml3, api_ml3
        logger.info(datos)
        for i in datos:
            if i['Activo'] == 'True':
                if i['Nombre'] == 'Telegram':
                    tg3 = TG2(i['API'])

                elif i['Nombre'] == 'Pushbullet':
                    pb3 = PB2(i['API'])

                elif i['Nombre'] == 'Email':
                    ml3 = ML2('test1notificaciones@gmail.com', 'i(!f!Boz_A&YLY]q')
                    api_ml3 = api_ml3

        return datos


def main():
    DescargaAutomaticaCli(database=ruta_db).run()


if __name__ == '__main__':
    main()
