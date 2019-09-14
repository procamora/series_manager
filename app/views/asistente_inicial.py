#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import platform
import sys
from typing import NoReturn

from PyQt5 import QtWidgets

from app import logger
from app.modulos.settings import sync_sqlite, sync_gdrive
from app.views.ui.asistente_inicial_ui import Ui_Dialog


class AsistenteInicial(QtWidgets.QDialog):
    def __init__(self, parent: object = None, ruta: str = None) -> NoReturn:
        # super(MiFormulario, self).__init__()
        # uic.loadUi('ui/AcercaDe.ui', self)
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowTitle('Asistente Inicial')

        self.rutaSistemaDefecto = self.muestraDirectorioTemporal()
        # Si paso una ruta la pongo por defecto
        if ruta is None:
            self.ui.checkBoxSync.setChecked(False)
            self.ui.lineRuta.setText(self.rutaSistemaDefecto)
        else:
            self.ui.lineRuta.setText(ruta)
            self.ui.checkBoxSync.setChecked(True)

        self.ui.checkBoxValido.setChecked(True)
        self.muestraMensaje(self.ui.checkBoxValido, 'Valido', True)

        self.ui.checkBoxSync.clicked.connect(self.checkSync)
        self.ui.pushButtonRuta.clicked.connect(self.buscarDirectorio)

        self.ui.pushButtonAplicar.clicked.connect(self.aplicaDatos)
        self.ui.pushButtonCerrar.clicked.connect(self.close)
        self.ui.pushButtonAceptar.clicked.connect(self.aceptaDatos)

    @staticmethod
    def muestraDirectorioTemporal() -> NoReturn:
        """
        IMPORTANTE
        Esta funcion es la misma que la de settings, solo la hago por visibilidad,
        pero esta repetida, no la copio porque no se si da problemas de dependencias
        el importar el otro fichero
        """
        directorio_trabajo = str()
        if platform.system() == "Windows":
            directorio_trabajo = '{}/{}'.format((os.environ['LOCALAPPDATA']).replace('\\', '/'), 'Gestor-Series')
        elif platform.system() == "Linux":
            directorio_trabajo = '{}/.{}'.format(os.environ['HOME'], 'Gestor-Series')
        return directorio_trabajo

    def buscarDirectorio(self) -> NoReturn:
        """
        Se encarga de coger la ruta en la que vamos a guardar el fichero,
        en este caso solo buscamos directorios,y establecemos que la ruta raiz sea
        el escrotorio, que se establece en el init
        """

        # filenames = QtGui.QFileDialog.getOpenFileName()
        filenames = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Directory", str(self.ui.lineRuta.text()),
                                                               QtWidgets.QFileDialog.ShowDirsOnly |
                                                               QtWidgets.QFileDialog.DontResolveSymlinks)

        self.ui.lineRuta.setText(filenames)
        if os.path.exists(filenames):
            self.ui.checkBoxValido.setChecked(True)
            self.muestraMensaje(self.ui.checkBoxValido, 'Valido', True)
        else:
            self.muestraMensaje(self.ui.checkBoxValido, 'No Valido 1', False)
            self.ui.checkBoxValido.setChecked(False)

    def checkSync(self) -> NoReturn:
        if self.ui.checkBoxSync.isChecked():
            # self.__cambiaVisibilidad(True)
            self.ui.checkBoxValido.setChecked(False)
            self.muestraMensaje(self.ui.checkBoxValido, 'Ruta vacia', False)
            self.ui.lineRuta.setText("")
        else:
            # self.__cambiaVisibilidad(False)
            self.ui.checkBoxValido.setChecked(True)
            self.muestraMensaje(self.ui.checkBoxValido, 'Valido', True)
            self.ui.lineRuta.setText(self.rutaSistemaDefecto)

    def aplicaDatos(self) -> bool:
        if self.ui.checkBoxValido.isChecked():
            if self.ui.checkBoxSync.isChecked():
                with open(sync_gdrive, 'w') as f:
                    f.write('1\n')
                    f.write(self.cambiaBarras(self.ui.lineRuta.text()))
            else:
                with open(sync_gdrive, 'w') as f:
                    f.write('0')
            with open(sync_sqlite, 'w') as f:
                f.write('1\n')
            self.muestraMensaje(self.ui.label, 'Exito', True)
            return True
        else:
            self.muestraMensaje(self.ui.label, 'Error', False)
            return False

    def aceptaDatos(self) -> NoReturn:
        """
        Boton Aceptar, primero aplicas los datos, si retorna True, cierra la ventana
        """

        if self.aplicaDatos():
            self.accept()

    @staticmethod
    def muestraMensaje(label: QtWidgets.QLabel, texto: str = 'Texto plantilla', estado: bool = True) -> NoReturn:
        """
        Muestra una determinada label con rojo o verde (depende del estado) y
        con el texto indicado
        """

        label.setText(texto)
        if estado:
            label.setStyleSheet('color: green')
        else:
            label.setStyleSheet('color: red')

    @staticmethod
    def cambiaBarras(texto: str) -> str:
        """
        Funcion para sustituir las barra de windows por las de linux, esta implementada
        en funciones.py, pero este fichero no puede importar nada de otros, ya que
        es el primero en ejecutarse la primera vez
        """
        return texto.replace('\\', '/')

    @staticmethod
    def checkIntegridadSqlite(idSqlite: str) -> bool:
        """
        Metodo para checkear que es correcto el fichero que contiene el id de la configuracion de la base de datos
        :return boolean: indicando si el valor es un integer o no 
        """

        try:
            int(idSqlite)  # si falla la conversion no es un integer
            return True
        except ValueError:
            return False

    @staticmethod
    def checkIntegridadGdrive(idGdrive: str) -> bool:
        """
        Metodo para checkear que es correcto el fichero que contiene el la ruta del directorio de rtrabajo con la base 
        de datos

        :return boolean: indicando si es correcto o no
        """

        try:
            int(idGdrive)  # si falla la conversion no es un integer
            return True
        except ValueError:
            return False

    @staticmethod
    def checkIntegridadFicheros() -> bool:
        """
        Comprobamos que existen los ficheros de cofiguracion necesarios y son correctos, en caso contrario llamamos a 
        asistente_inicial y terminamos

        tendra que ejecutarlo al inicio Series.py
        :return: 
        """

        # Si no existe uno de los ficheros necesarios asistente inicial
        logger.debug('Analized exists: {}'.format(sync_sqlite))
        logger.debug('Analized exists: {}'.format(sync_gdrive))
        if not os.path.exists(sync_sqlite) or not os.path.exists(sync_gdrive):
            main()  # main de la funcion
            return False
        else:
            # comprobamos que es correcto el fichero sync_sqlite
            with open(sync_sqlite, 'r') as f:
                retornoSqlite = AsistenteInicial.checkIntegridadSqlite(f.readline())

            # comprobamos que es correcto el fichero sync_gdrive
            with open(sync_gdrive, 'r') as f:
                retornoGdrive = AsistenteInicial.checkIntegridadGdrive(f.readlines()[0])  # linea 1 es un 1 o un 0

            if not retornoGdrive or not retornoSqlite:
                main()  # main de la funcion
                return False

            return True

    @staticmethod
    def getDatos(parent: object = None, ruta: str = None) -> NoReturn:
        dialog = AsistenteInicial(parent, ruta)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    AsistenteInicial.getDatos()
    return app


if __name__ == '__main__':
    main()
