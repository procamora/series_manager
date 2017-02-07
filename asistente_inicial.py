#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import platform

from PyQt5 import QtWidgets

from ui.asistente_inicial_ui import Ui_Dialog


class MiFormulario(QtWidgets.QDialog):
    def __init__(self, parent=None, ruta=None):
        #super(MiFormulario, self).__init__()
        #uic.loadUi('ui/AcercaDe.ui', self)
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowTitle('Asistente Inicial')

        self.RutaSistemaDefecto = self.__muestraDirectorioTemporal()
        #Si paso una ruta la pongo por defecto
        if ruta is None:
            self.ui.checkBoxSync.setChecked(False)
            self.ui.lineRuta.setText(self.RutaSistemaDefecto)
        else:
            self.ui.lineRuta.setText(ruta)
            self.ui.checkBoxSync.setChecked(True)


        self.ui.checkBoxValido.setChecked(True)
        self.__muestraMensaje(self.ui.checkBoxValido, 'Valido', True)

        self.ui.checkBoxSync.clicked.connect(self.__checkSync)
        self.ui.pushButtonRuta.clicked.connect(self.__buscarDirectorio)

        self.ui.pushButtonAplicar.clicked.connect(self.__aplicaDatos)
        self.ui.pushButtonCerrar.clicked.connect(self.close)
        self.ui.pushButtonAceptar.clicked.connect(self.__aceptaDatos)


    def __muestraDirectorioTemporal(self):
        """
        IMPORTANTE
        Esta funcion es la misma que la de settings, solo la hago por visibilidad,
        pero esta repetida, no la copio porque no se si da problemas de dependencias
        el importar el otro fichero
        """
        if platform.system() == "Windows":
            directorio_trabajo = '{}/{}'.format((os.environ['LOCALAPPDATA']).replace('\\', '/'), 'Gestor-Series')
        elif platform.system() == "Linux":
            directorio_trabajo = '{}/.{}'.format(os.environ['HOME'], 'Gestor-Series')
        return directorio_trabajo


    def __buscarDirectorio(self):
        """
        Se encarga de coger la ruta en la que vamos a guardar el fichero,
        en este caso solo buscamos directorios,y establecemos que la ruta raiz sea
        el escrotorio, que se establece en el init
        """

        #filenames = QtGui.QFileDialog.getOpenFileName()
        filenames = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Directory",
            str(self.ui.lineRuta.text()),
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks)

        self.ui.lineRuta.setText(filenames)
        if os.path.exists(filenames):
            self.ui.checkBoxValido.setChecked(True)
            self.__muestraMensaje(self.ui.checkBoxValido, 'Valido', True)
        else:
            self.__muestraMensaje(self.ui.checkBoxValido, 'No Valido 1', False)
            self.ui.checkBoxValido.setChecked(False)


    def __cambiaVisibilidad(self, estado=False):
        """
        Actualmente no se usa, oculta la seguda fila
        """
        self.ui.lineRuta.setVisible(estado)
        self.ui.pushButtonRuta.setVisible(estado)


    def __checkSync(self):
        if self.ui.checkBoxSync.isChecked():
            #self.__cambiaVisibilidad(True)
            self.ui.checkBoxValido.setChecked(False)
            self.__muestraMensaje(self.ui.checkBoxValido, 'Ruta vacia', False)
            self.ui.lineRuta.setText("")
        else:
            #self.__cambiaVisibilidad(False)
            self.ui.checkBoxValido.setChecked(True)
            self.__muestraMensaje(self.ui.checkBoxValido, 'Valido', True)
            self.ui.lineRuta.setText(self.RutaSistemaDefecto)


    def __aplicaDatos(self):
        if self.ui.checkBoxValido.isChecked():
            if self.ui.checkBoxSync.isChecked():
                with open('sync.cnf', 'w') as f:
                    f.write('1\n')
                    f.write(self.__cambiaBarras(self.ui.lineRuta.text()))
            else:
                with open('sync.cnf', 'w') as f:
                    f.write('0')
            self.__muestraMensaje(self.ui.label, 'Exito', True)
            return True
        else:
            self.__muestraMensaje(self.ui.label, 'Error', False)
            return False


    def __aceptaDatos(self):
        """
        Boton Aceptar, primero aplicas los datos, si retorna True, cierra la ventana
        """

        if self.__aplicaDatos():
            self.accept()


    def __muestraMensaje(self, label, texto='Texto plantilla', estado=True):
        """
        Muestra una determinada label con rojo o verde (depende del estado) y
        con el texto indicado
        """

        label.setText(texto)
        if estado:
            label.setStyleSheet('color: green')
        else:
            label.setStyleSheet('color: red')


    def __cambiaBarras(self, texto):
        """
        Funcion para sustituir las barra de windows por las de linux, esta implementada
        en funciones.py, pero este fichero no puede importar nada de otros, ya que
        es el primero en ejecutarse la primera vez
        """
        return texto.replace('\\', '/')


    @staticmethod
    def getDatos(parent=None, ruta=None):
        dialog = MiFormulario(parent, ruta)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    MiFormulario.getDatos()
    return app


if __name__ == '__main__':
    main()
