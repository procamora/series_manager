#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import platform

modo_debug = True
gdrive = 0
sistema = platform.system()
nombre_db = 'Series.db'

#api_telegram = '143504303:AAF5JHesA5WGnc9VWrG9EotCqtMtaZfdEVE'

#user_tviso  = 'NotSer'
#pass_tviso  = 'i(!f!Boz_A&YLY]q'

if os.path.exists('sync.cnf'):
    with open('sync.cnf', 'r') as f:
        lineas_fich = f.readlines()
        gdrive = int(lineas_fich[0].replace('\n', ''))
elif os.path.exists('../sync.cnf'):
    with open('../sync.cnf', 'r') as f:
        lineas_fich = f.readlines()
        gdrive = int(lineas_fich[0].replace('\n', ''))

if gdrive:
    dir_drive = lineas_fich[1].replace('\n', '')

    if sistema == "Windows":
        directorio_trabajo = '{}/{}'.format(dir_drive, 'Gestor-Series')
        directorio_local = os.path.dirname(os.path.realpath(__file__)).replace(
            '\\', '/').replace('/modulos', '')  # tengo que eliminar /modulos para que coga ../ y no este directorio
        # para cuando lo ejecuto con el exe
        if directorio_local.split('/')[-1] == 'library.zip':
            directorio_local += '/..'
    elif sistema == "Linux":
        directorio_trabajo = '{}/{}'.format(dir_drive, 'Gestor-Series')
        directorio_local = os.path.dirname(
            os.path.realpath(__file__)).replace('/modulos', '')
else:
    if sistema == "Windows":
        directorio_trabajo = '{}/{}'.format(
            (os.environ['LOCALAPPDATA']).replace('\\', '/'), 'Gestor-Series')
        directorio_local = os.path.dirname(os.path.realpath(__file__)).replace(
            '\\', '/').replace('/modulos', '')
        # para cuando lo ejecuto con el exe
        if directorio_local.split('/')[-1] == 'library.zip':
            directorio_local += '/.2.'
    elif sistema == "Linux":
        directorio_trabajo = '{}/.{}'.format(
            os.environ['HOME'], 'Gestor-Series')
        directorio_local = os.path.dirname(
            os.path.realpath(__file__)).replace('/modulos', '')

ruta_db = '{}/{}'.format(directorio_trabajo, nombre_db)

if modo_debug:
    print('Dir local: {}'.format(directorio_local))
    print('Dir traba: {}'.format(directorio_trabajo))
    print('Ruta db: {}'.format(ruta_db))
