#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sqlite3
import time
import datetime
import unicodedata
import requests
import glob

from modulos.connect_sqlite import conectionSQLite, ejecutaScriptSqlite
from modulos.settings import directorio_trabajo, directorio_local, nombre_db, ruta_db
import asistente_inicial


def creaDirectorioTrabajo(directorio='Gestor-series'):
    if not os.path.exists(directorio_trabajo):
        print("NO EXISTE DIRECTORIO TRABAJO")
        asistente_inicial.main()
        os.mkdir(directorio_trabajo)
        plantillaDatabase(nombre_db, directorio_trabajo)
        plantillaFicheroConf('id.conf', directorio_local)
    else:
        ruta_id = '{}/{}'.format(directorio_local, 'id.conf')
        if not os.path.exists(ruta_db) or os.stat(ruta_db).st_size == 0:
            print(1)
            plantillaDatabase(nombre_db, directorio_trabajo)
        if not os.path.exists(ruta_id) or os.stat(ruta_id).st_size == 0:
            print(2)
            plantillaFicheroConf('id.conf', directorio_local)
    return directorio_trabajo


def configuarion(fichero):
    with open(fichero, 'r') as f:
        a = f.read()
    # print a
    b = a.replace('/n', '->')
    b = b.replace(' ', '')
    # print b

    pri = b.split('->')
    # print pri
    par = list()
    impar = list()

    for i in pri:
        if (pri.index(i) % 2 == 0):
            par.append(i)
        else:
            impar.append(i)
    dictionary = dict(list(zip(par, impar)))
    return dictionary


def crearFichero(fichero):
    with open(fichero, 'w') as f:
        f.write("")


def dbConfiguarion(name_db=nombre_db, idFile='id.conf'):
    """
    Funcion que obtiene los valores de la configuracion de un programa,
    recibe el nombre de la base de datos y el del fichero con el id de la
    configuracion y devuelve el diciconario con los datos

    :param str name_db: Nombre de la base de datos sqlite
    :param str idFile:  Nombre del fichero con el id de la configuracion de la base de datos

    :return dict: Nos devuelve un diccionario con los datos
    """
    ruta = creaDirectorioTrabajo()
    try:
        with open(r'{}/{}'.format(directorio_local, idFile), 'r') as f:
            id_db = f.readline()
    except:
        print('fallo en dbConfiguarion')
        id_db = 1

    query = 'SELECT * FROM Configuraciones WHERE id IS {}'.format(id_db)
    # print u'{}/{}'.format(creaDirectorioTrabajo(),name_db)
    consulta = conectionSQLite('{}/{}'.format(ruta, name_db), query, True)[0]
    return consulta


def plantillaFicheroConf(fich='id.conf', ruta=directorio_local):
    """
    Si hay una configuracion en la la carpeta del programa la mueve a la carpeta
    de configuracion, sino la hay comprueba si existe el fichero, si existe y esta
    vacio o no existe lo pone a 1
    """

    fichero_conf = '{}/{}'.format(ruta, fich)
    if os.path.exists(fich):
        print((fich, fichero_conf))
        os.rename(fich, fichero_conf)
    else:
        if os.path.exists(fichero_conf):
            if os.stat(fichero_conf).st_size == 0:
                with open(fichero_conf, 'w') as f:
                    f.write("1")
        else:
            with open(fichero_conf, 'w') as f:
                f.write("1")


# MODIFICAR ESTO PORQUE HE AÑADIDO ESTA FUNCION EN CONECTIONSQLITE
def plantillaDatabase(db=nombre_db, ruta=directorio_trabajo):
    ficheros_sql = glob.glob('{}/SQL/*.sql'.format(directorio_local))

    fichero_db = '{}/{}'.format(ruta, db)
    if os.path.exists(db):
        print((db, fichero_db))
        os.rename(db, fichero_db)
    else:
        # con = sqlite3.connect(fichero_db) #Creo que ya no lo uso
        if os.path.exists(fichero_db):
            if os.stat(fichero_db).st_size == 0:
                if os.path.exists(ficheros_sql[-1]):
                    with open(cambiaBarras(ficheros_sql[-1]), 'r') as f:
                        plantilla = f.read()
                    ejecutaScriptSqlite(fichero_db, plantilla)
                elif os.path.exists(
                        '{}/SQL/20160724_completo.sql'.format(directorio_local)):  # da fallo porque el array esta vacio
                    with open(cambiaBarras('{}/SQL/20160724_completo.sql'.format(directorio_local)), 'r') as f:
                        plantilla = f.read()
                    ejecutaScriptSqlite(fichero_db, plantilla)
                else:
                    print('fallo al hacer backup')
        else:
            with open(cambiaBarras(ficheros_sql[-1]), 'r') as f:
                plantilla = f.read()
            ejecutaScriptSqlite(fichero_db, plantilla)


def crearBackUpCompletoDB():
    db = ruta_db

    con = sqlite3.connect(db)
    data = '\n'.join(con.iterdump())
    try:
        with open('{}/SQL/{}.sql'.format(directorio_local, time.strftime("%Y%m%d")), 'w') as f:
            f.write(data)
    except IOError:
        with open('SQL/{}.sql'.format(time.strftime("%Y%m%d")), 'w') as f:
            f.write(data)
    except:
        print('error final')


def cambiaBarras(texto):
    return texto.replace('\\', '/')


def calculaDiaSemana():
    """
    Te dice el dia de la semana en el que estamos, lo uso para ordenar serie de mas cerca a mas lejos
    """

    x = datetime.datetime.now()
    dicdias = {'MONDAY': 'Lunes',
               'TUESDAY': 'Martes',
               'WEDNESDAY': 'Miercoles',
               'THURSDAY': 'Jueves',
               'FRIDAY': 'Viernes',
               'SATURDAY': 'Sabado',
               'SUNDAY': 'Domingo'}

    anho = x.year
    mes = x.month
    dia = x.day

    fecha = datetime.date(anho, mes, dia)

    try:
        a = dicdias[fecha.strftime('%A').upper()]
        return eliminaTildes(a)
    # en linux sale el dia en castellano, por eso lo paso directamente
    # poniendo la primera letra en mayusculas
    except KeyError:
        a = fecha.strftime('%A').capitalize()
        return eliminaTildes(a)


def fechaToNumero(dia):
    """
    Convierte el dia de la semana a un numero, y luego te crea una lista ordenada
    de los dias de la semana de mas cerca a menos cerca
    """

    DiaNombre = ["Lunes", "Martes", "Miercoles",
                 "Jueves", "Viernes", "Sabado", "Domingo"]
    lista = list()
    num = DiaNombre.index(dia)  # localizo en indice del dia en el que estoy
    # guardo la parte de la derecha de la semana y luego la izq
    lista.extend(DiaNombre[num:])
    lista.extend(DiaNombre[:num])
    return lista


def eliminaTildes(cadena):
    """	http:/guimi.net/blogs/hiparco/funcion-para-eliminar-acentos-en-python/5"""
    # s = ''.join((c for c in unicodedata.normalize('NFD',unicode(cadena)) if unicodedata.category(c) != 'Mn'))
    # return s.decode()
    return ''.join((c for c in unicodedata.normalize('NFD', str(cadena)) if unicodedata.category(c) != 'Mn'))


def descargaFichero(url, destino, libreria='requests'):
    if libreria == 'urllib':
        import urllib
        # print "downloading with urllib"
        urllib.urlretrieve(url, destino)

    if libreria == 'urllib2':
        import urllib2
        # print "downloading with urllib2"
        f = urllib2.urlopen(url)
        data = f.read()
        with open(destino, "wb") as code:
            code.write(data)

    if libreria == 'requests':
        # print "downloading with requests"
        r = requests.get(url)
        with open(destino, "wb") as code:
            code.write(r.content)

    if libreria == 'wget':
        import wget
        # print "downloading with wget"
        wget.download(url, destino)


def muestraMensaje(label, texto='Texto plantilla', estado=True):
    """
    Muestra una determinada label con rojo o verde (depende del estado) y con el texto indicado
    """

    label.setText(texto)
    if estado:
        label.setStyleSheet('color: green')
    else:
        label.setStyleSheet('color: red')


def internetOn():
    try:
        session = requests.session()
        session.get('http://www.google.com', verify=False)
        return True
    except requests.exceptions.ConnectionError:
        return False
