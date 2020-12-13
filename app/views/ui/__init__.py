#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path, PurePath  # nueva forma de trabajar con rutas

# Metodo para encontrarar todos los ficheros e importarlos
absolut_path = PurePath(__file__)  # Ruta absoluta de este fichero
# Path(absolut_path.parent)     # Obtenemos el directorio donde esta el fichero
# glob("*.py")                  # Buscamos todos los ficheros con extension py
# PurePath(str(f)).stem         # Para cada fichero solo obtenemos su nombre (sin extension y ruta)
__all__ = [PurePath(str(f)).stem for f in Path(absolut_path.parent).glob("*.py")]
