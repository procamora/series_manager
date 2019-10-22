#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import sys
from pathlib import Path, PurePosixPath  # nueva forma de trabajar con rutas
from typing import NoReturn

from PyQt5 import QtWidgets
from app.views.ui.asistente_inicial_ui import Ui_Dialog

from app import logger
from app.utils.settings import PATH_FILE_CONFIG, DIRECTORY_WORKING


class AsistenteInicial(QtWidgets.QDialog):
    def __init__(self, parent: object = None, ruta: Path = None) -> NoReturn:
        # super(MiFormulario, self).__init__()
        # uic.loadUi('ui/AcercaDe.ui', self)
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.config = configparser.ConfigParser()
        self.config.read(PATH_FILE_CONFIG)

        self.setWindowTitle('Asistente Inicial')

        # self.rutaSistemaDefecto = self.show_directory_temporary()
        # Si paso una ruta la pongo por defecto
        if ruta is None:
            self.ui.lineRuta.setText(str(DIRECTORY_WORKING))
        else:
            self.ui.lineRuta.setText(str(ruta))

        print(self.config["CONFIGURABLE"].getboolean('WORKDIR_DEFAULT'))
        if self.config["CONFIGURABLE"].getboolean('WORKDIR_DEFAULT'):
            self.ui.checkBoxSync.setChecked(False)
        else:
            self.ui.checkBoxSync.setChecked(True)

        self.ui.checkBoxValido.setChecked(True)
        self.show_message(self.ui.checkBoxValido, 'Valido', True)

        self.ui.checkBoxSync.clicked.connect(self.check_sync)
        self.ui.pushButtonRuta.clicked.connect(self.search_directory)

        self.ui.pushButtonAplicar.clicked.connect(self.apply_data)
        self.ui.pushButtonCerrar.clicked.connect(self.close)
        self.ui.pushButtonAceptar.clicked.connect(self.accept_data)

    ''''@staticmethod
    def show_directory_temporary() -> NoReturn:
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
            directorio_trabajo = f'{os.environ["HOME"]}/.{"Gestor-Series"}'
        return directorio_trabajo'''

    def search_directory(self) -> NoReturn:
        """
        Se encarga de coger la ruta en la que vamos a guardar el fichero,
        en este caso solo buscamos directorios,y establecemos que la ruta raiz sea
        el escrotorio, que se establece en el init
        """

        # filenames = QtGui.QFileDialog.getOpenFileName()
        filenames: Path = Path(
            QtWidgets.QFileDialog.getExistingDirectory(self, "Open Directory", str(self.ui.lineRuta.text()),
                                                       QtWidgets.QFileDialog.ShowDirsOnly |
                                                       QtWidgets.QFileDialog.DontResolveSymlinks))

        self.ui.lineRuta.setText(filenames)
        if filenames.exists():
            self.ui.checkBoxValido.setChecked(True)
            self.show_message(self.ui.checkBoxValido, 'Valido', True)
        else:
            self.show_message(self.ui.checkBoxValido, 'No Valido 1', False)
            self.ui.checkBoxValido.setChecked(False)

    def check_sync(self) -> NoReturn:
        if self.ui.checkBoxSync.isChecked():
            # self.__cambiaVisibilidad(True)
            self.ui.checkBoxValido.setChecked(False)
            self.show_message(self.ui.checkBoxValido, 'Ruta vacia', False)
            self.ui.lineRuta.setText("")
        else:
            # self.__cambiaVisibilidad(False)
            self.ui.checkBoxValido.setChecked(True)
            self.show_message(self.ui.checkBoxValido, 'Valido', True)
            self.ui.lineRuta.setText(str(DIRECTORY_WORKING))

    def apply_data(self) -> bool:
        if self.ui.checkBoxValido.isChecked():
            print(self.ui.checkBoxSync.isChecked())
            self.config["CONFIGURABLE"]['WORKDIR_DEFAULT'] = str(not self.ui.checkBoxSync.isChecked())
            if self.ui.checkBoxSync.isChecked():
                self.config["CONFIGURABLE"]['WORKDIR'] = PurePosixPath(self.ui.lineRuta.text())
            with open(str(PATH_FILE_CONFIG), 'w') as configfile:
                print("escribi datos")
                self.config.write(configfile)

            self.show_message(self.ui.label, 'Exito', True)
            return True
        else:
            self.show_message(self.ui.label, 'Error', False)
            return False

    def accept_data(self) -> NoReturn:
        """
        Boton Aceptar, primero aplicas los datos, si retorna True, cierra la ventana
        """
        if self.apply_data():
            self.accept()

    @staticmethod
    def show_message(label: QtWidgets.QLabel, texto: str = 'Texto plantilla', estado: bool = True) -> NoReturn:
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
    def check_integrity_sqlite(id_sqlite: str) -> bool:
        """
        Metodo para checkear que es correcto el fichero que contiene el id de la configuracion de la base de datos
        :return boolean: indicando si el valor es un integer o no 
        """
        try:
            int(id_sqlite)  # si falla la conversion no es un integer
            return True
        except ValueError:
            return False

    @staticmethod
    def check_integrity_gdrive(id_gdrive: str) -> bool:
        """
        Metodo para checkear que es correcto el fichero que contiene el la ruta del directorio de rtrabajo con la base 
        de datos
        :return boolean: indicando si es correcto o no
        """
        try:
            int(id_gdrive)  # si falla la conversion no es un integer
            return True
        except ValueError:
            return False

    @staticmethod
    def check_integrity_files() -> bool:
        """
        Comprobamos que existen los ficheros de cofiguracion necesarios y son correctos, en caso contrario llamamos a 
        asistente_inicial y terminamos
        tendra que ejecutarlo al inicio Series.py
        :return: 
        """
        # Si no existe uno de los ficheros necesarios asistente inicial
        logger.debug(f'Analized exists: {PATH_FILE_CONFIG}')
        if not PATH_FILE_CONFIG.exists():
            main()  # main de la funcion
            return False
        return True

    @staticmethod
    def get_data(parent: object = None, ruta: Path = None) -> NoReturn:
        dialog = AsistenteInicial(parent, ruta)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    AsistenteInicial.get_data()
    return app


if __name__ == '__main__':
    main()
