#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
from pathlib import PurePath, Path  # nueva forma de trabajar con rutas

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: str = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

from app import logger

path_views: Path = Path(new_path, 'app', 'views')
path_ui: Path = Path(new_path, 'app', 'views', 'ui')

for file in path_ui.glob('*.ui'):
    new_path_ui: Path = Path(file.parent, str(file.stem) + '_ui.py')
    command = f'pyuic5 -x {file} -o {new_path_ui}'
    logger.info(command)
    os.system(command)


print(path_views.joinpath('fatcow.qrc'))
print(path_ui)
# os.system('pyrcc5 fatcow.qrc -o fatcow_rc.py')
# os.system('pyrcc5 ui/fatcow.qrc -o ui/fatcow_rc.py')
