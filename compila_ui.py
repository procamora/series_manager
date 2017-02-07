#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import os

fich = glob.glob("ui/*.ui")

for i in fich:
    comando = "pyuic5 -x {} -o {}.py".format(i, i.replace(".", "_"))
    print(comando)
    os.system(comando)

os.system('pyrcc5 fatcow.qrc -o fatcow_rc.py')
os.system('pyrcc5 ui/fatcow.qrc -o ui/fatcow_rc.py')
