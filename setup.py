#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import glob
import shutil

from cx_Freeze import setup, Executable

def CogeFich(ruta='./'):
    '''
    Con la lista que tengo de extensiones voy haciendo una lista de todos los ficheros de esa extension y despues la uno en una unica lista con todos los ficheros

    http:/www.genbetadev.com/python/python-mezclar-listas-sin-duplicados-o-aibalaostia
    '''
    extenciones = ['pyc', 'ui', 'db', 'conf', 'sql']
    inicial = list()
    for i in extenciones:
        lista = glob.glob('%s*.%s'%(ruta, i))
        #print len(lista)
        inicial = list(set(inicial + lista))
    return inicial


shutil.rmtree('build', ignore_errors=True)


# GUI applications require a different base on Windows (the default is for a
# console application).
if sys.platform == 'win32':
    base = 'Win32GUI'
else:
    base = None
#base = None

if len(sys.argv) == 1:
    sys.argv += ['build']




listaFicheros = list()
listaFicheros.append('SQL/')
#listaFicheros.append('Icons/')

import requests.certs
listaFicheros.append((requests.certs.where(), 'cacert.pem'))


print(listaFicheros)


if sys.platform == 'linux2':
    listaFicheros.append(('/usr/lib/qt4/plugins/sqldrivers', 'sqldrivers'))  # IMPORTANTE PARA QUE SE ABRA EL PROGRAMA
elif sys.platform == 'win32':
    listaFicheros.append(('C:/Python34/Lib/site-packages/PyQt4/plugins/sqldrivers', 'sqldrivers'))  # IMPORTANTE PARA QUE SE ABRA EL PROGRAMA
    #listaFicheros.append((r"../../../PyQt4/plugins/platforms/qwindows.dll", "platforms/qwindows.dll"))  # IMPORTANTE PARA QUE SE ABRA EL PROGRAMA



include_files= listaFicheros
includes = ['sip', 'PyQt4.QtCore', 'PyQt4.QtGui', 'atexit', 'sqlite3.dump']
excludes=['tcl', 'tables']
packages=['re', 'time', 'sys', 'os', 'platform', 'subprocess', 'requests', 'feedparser', 'sqlite3', 'unicodedata', 'datetime', 'json', 'glob',
'bs4', 'imdbpie', 'pushbullet', 'http', 'PyQt4', 'functools', 'shutil', 'tempfile', 'math', 'mailer', 'ntplib']


if sys.version[0] == '3':
    excludes.append('PyQt4.uic.port_v2')


exe = Executable(
    script='Series.py',
    base=base,
    icon='Icons/Principal.ico',
    #compress=True,
    copyDependentFiles=True,
    appendScriptToExe=True,
    appendScriptToLibrary=True
    )

build_exe_options = {'excludes':excludes,
    'includes':includes,
    'include_msvcr': True, 		#algunos sistemas no tienen la dll isntalada, por eso la incluimos
    'compressed': True,
    'copy_dependent_files': True,
    'create_shared_zip': True,
    'include_in_shared_zip': True,
    'optimize': 2,
    'include_files':include_files}
#'packages':packages}

setup(
    name = 'Gestor de Series',
    version = '1.0',
    description = 'Gestor de Series',
    author = 'Pablo Rocamora',
    author_email='pablojoserocamora@gmail.com',
    options = {'build_exe': build_exe_options},
    executables = [exe]
    )
