#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys

import requests
from imdbpie import Imdb

try: #Ejecucion desde Series.py
    from .connect_sqlite import conectionSQLite, ejecutaScriptSqlite
    from .settings import modo_debug, ruta_db
except: #Ejecucion local
    from connect_sqlite import conectionSQLite, ejecutaScriptSqlite
    from settings import modo_debug, ruta_db

if '../' not in sys.path:
    sys.path.append('../')
from funciones import dbConfiguarion

class actualizaImdb():
    def __init__(self):
        self.imdb = Imdb()
        self.conf = dbConfiguarion()
        self.nombre_db = ruta_db
        #self.imdb = Imdb(cache=True, cache_dir='/tmp/imdbpie-cache-here', anonymize=False)


    def __compruebaDatos(self, Datos, series):
        if str(series['imdb_Temporada']) == Datos['Temp'] and str(series['imdb_Finaliza']) == Datos['year'] and str(series['imdb_Capitulos']) == Datos['Cap'] :
            return True
        else:
            return False


    def __compruebaDatosParcial(self, Datos, series):
        if str(series['imdb_Temporada']) == Datos['Temp'] and str(series['imdb_Finaliza']) == Datos['year']:
            return True
        else:
            return False


    def __buscaCapitulo(self, id_imdb):
        #Para buscar el capitulo en vez de coger el la primera temporada, coger la ultima
        # problema de que la ultima temporada no este completa
        url = 'http://www.imdb.com/title/{}/episodes?season=1'.format(id_imdb)
        session = requests.session()
        html = session.get(url, verify=True).text
        a = re.findall('S1, Ep[0-9]+', html)
        return re.findall('[0-9]+', a[-1])[-1]


    def __actualizaDatos(self, Datos):
        query = 'UPDATE series SET imdb_Temporada="{}", imdb_Finaliza="{}", imdb_Capitulos="{}" WHERE imdb_id Like "{}"'.format(Datos['Temp'], Datos['year'], Datos['Cap'], Datos['id_imdb'])
        conectionSQLite(self.nombre_db, query)
        print(query)


    def __actualizaDatosParcial(self, Datos):
        query = 'UPDATE series SET imdb_Temporada="{}", imdb_Finaliza="{}" WHERE imdb_id Like "{}"'.format(Datos['Temp'], Datos['year'], Datos['id_imdb'])
        conectionSQLite(self.nombre_db, query)
        print(query)


    def actualizaTemporadas(self): #tarda mucho
        query = 'SELECT * FROM Series WHERE imdb_Finaliza LIKE "????" AND imdb_seguir LIKE "Si" ORDER BY Nombre'		# para actualizar_insertar series con mod parcial
        series =  conectionSQLite(self.nombre_db, query, True)

        for i in series:
            try:
                print(i['Nombre'])
                title = self.imdb.get_title_by_id(i['imdb_id'])

                if title.data['seasons'][-1] == 'unknown':  #en algunas series la ultima temporada pone unknown
                    Temporada = title.data['seasons'][-2]
                else:
                    Temporada = title.data['seasons'][-1]

                DatosImdb = {'Titulo': title.data['title'], 'Temp': Temporada, 'year': title.data['year_end'], 'id_imdb': i['imdb_id']}
                Cap = self.__buscaCapitulo(i['imdb_id'])
                DatosImdb['Cap'] = Cap

                if not self.__compruebaDatosParcial(DatosImdb, i):
                    print(DatosImdb)
                    self.__actualizaDatosParcial(DatosImdb)

            except Exception as e:
                print('FALLO: {}'.format(i['Nombre']))
                print(e)


    def actulizaCompleto(self):
        query = 'SELECT * FROM Series WHERE imdb_seguir LIKE "Si" AND (imdb_id IS NULL OR imdb_Finaliza IS NULL) AND NOT imdb_id IS NULL'  # para nuevas series con mod completa
        series =  conectionSQLite(self.nombre_db, query, True)
        print(series)

        for i in series:
            try:
                if modo_debug:
                    print(i['Nombre'])
                title = self.imdb.get_title_by_id(i['imdb_id'])

                if title.data['seasons'][-1] == 'unknown':  #en algunas series la ultima temporada pone unknown
                    Temporada = title.data['seasons'][-2]
                else:
                    Temporada = title.data['seasons'][-1]

                DatosImdb = {'Titulo': title.data['title'], 'Temp': Temporada, 'year': title.data['year_end'], 'id_imdb': i['imdb_id']}
                Cap = self.__buscaCapitulo(i['imdb_id'])
                DatosImdb['Cap'] = Cap

                if not self.__compruebaDatos(DatosImdb, i):
                    #print 'completo'
                    self.__actualizaDatos(DatosImdb)

            except Exception as e:
                print('FALLO: {}'.format(i['Nombre']))
                print(e)


    def actualizaSerie(self, imdb_id):
        print(imdb_id)
        try:
            title = self.imdb.get_title_by_id(imdb_id)

            if title.data['seasons'][-1] == 'unknown':  #en algunas series la ultima temporada pone unknown
                Temporada = title.data['seasons'][-2]
            else:
                Temporada = title.data['seasons'][-1]

            DatosImdb = {'Titulo': title.data['title'], 'Temp': Temporada, 'year': title.data['year_end'], 'id_imdb': imdb_id}
            Cap = self.__buscaCapitulo(imdb_id)
            DatosImdb['Cap'] = Cap

            self.__actualizaDatos(DatosImdb)

        except Exception as e:
            print('FALLO: {}'.format(title.data['title']))
            print(e)


    def compruebaTitulo(self, imdb_id):
        '''
        Comprueba si el titulo pasado existe o no en la base de datos de imdb
        '''
        try:
            self.imdb.get_title_by_id(imdb_id)
        except:
            return False
        return True


    def series_finalizadas(self):
        '''
        busca las series finalizadas que tienen el imdb_seguir a si y lo actualiza a no para
        hacer mas rapidas las futuras actualizaciones
        '''
        query = 'SELECT * FROM Series Where Estado LIKE "Finalizada" AND imdb_seguir LIKE "Si"'
        series =  conectionSQLite(self.nombre_db, query, True)

        queryCompleta = str()

        for i in series:
            query = 'UPDATE series SET imdb_seguir="No" WHERE Nombre LIKE "{}";'.format(i["Nombre"])
            queryCompleta += '\n'+query

        #print(queryCompleta)
        ejecutaScriptSqlite(self.nombre_db, queryCompleta)


def main():
    a = actualizaImdb()
    #print((a.compruebaTitulo('tt1475582')))
    #'''
    print('actualizaTemporadas')
    #a.actualizaTemporadas()			# actualizar_insertar series con mod parcial(todas lases series siguiendo, tarda bastante)
    print('actulizaCompleto')
    #a.actulizaCompleto()
    print('actualizaSerie')
    #a.actualizaSerie('tt3551096')
    #'''				# actualizar_insertar series que no tienen datos de capitulo/temporada de imdb
    #a.series_finalizadas()


if __name__ == '__main__':
    main()
