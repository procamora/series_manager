#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtWidgets

from modulos import funciones
from modulos.connect_sqlite import conectionSQLite
from modulos.settings import modo_debug, directorio_local, ruta_db
from ui.preferencias_ui import Ui_Dialog


class Preferencias(QtWidgets.QDialog):
    def __init__(self, parent=None, dbSeries=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.otra = 'otra'  # campo otra del formulario
        self.estadoI = 'Ok'  # estado inicial
        self.estadoF = 'Cancelado'  # final
        self.estadoA = self.estadoI  # actual
        self.db = dbSeries
        self.ruta = directorio_local

        self.setWindowTitle('Preferencias de configuracion')
        self.ui.tabWidget.setCurrentIndex(0)

        self.configuraciones = list(dict())
        self.datodDb = dict()
        self.operacionesIniciales()

        # recogo todos los dias de la caja y le paso el indice del dia en el
        # que sale
        allItems = [self.ui.BoxId.itemText(i) for i in range(self.ui.BoxId.count())]

        print(allItems)
        with open(r'{}/id.conf'.format(self.ruta), 'r') as f:
            id_fich = f.readline().replace('/n', '')

        try:
            self.ui.BoxId.setCurrentIndex(allItems.index(id_fich))
        except ValueError:
            if len(allItems) == 1:  # si solo hay 1 es 'otra'
                self.ui.BoxId.setCurrentIndex(allItems.index(self.otra))
            else:
                # si da error por algun motivo pongo el primero
                self.ui.BoxId.setCurrentIndex(allItems.index('1'))

        self.procesosComunes()

        self.ui.pushButton.clicked.connect(self.buscarDirectorio)
        self.ui.BoxId.activated.connect(self.procesosComunes)

        self.ui.pushButtonAplicar.clicked.connect(self.aplicaDatos)
        self.ui.pushButtonCerrar.clicked.connect(self.cancela)
        self.ui.pushButtonAceptar.clicked.connect(self.aceptaDatos)

    def operacionesIniciales(self):
        self.sacaDatos()
        self.listaId()

    def buscarDirectorio(self):
        """
        Se encarga de coger la ruta en la que vamos a guardar el fichero, en este caso solo buscamos directorios,
        y establecemos que la ruta raiz sea el escrotorio, que se establece en el init
        """

        # filenames = QtGui.QFileDialog.getOpenFileName()
        filenames = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Directory", str(self.ui.lineRuta.text()),
                                                               QtWidgets.QFileDialog.ShowDirsOnly |
                                                               QtWidgets.QFileDialog.DontResolveSymlinks)

        if filenames is not None:
            # if not (filenames.isNull()): en python 3 filenames ya no es un
            # QString sino str
            self.ui.lineRuta.setText(filenames)

    def sacaDatos(self):
        """

        """

        query = 'SELECT * FROM Configuraciones'
        self.configuraciones = conectionSQLite(self.db, query, True)
        if len(self.configuraciones) > 0:
            self.datodDb = self.configuraciones[0]

    def listaId(self):
        """

        """

        lista = list()
        for i in self.configuraciones:
            lista.append(str(i['id']))

        self.ui.BoxId.clear()
        self.ui.BoxId.addItems(lista)
        self.ui.BoxId.addItem(self.otra)

    def averiguaConf(self):
        """

        """

        for i in self.configuraciones:
            if str(self.ui.BoxId.currentText()) == str(i['id']):
                if modo_debug:
                    print((self.ui.BoxId.currentText()))
                    print(i)
                self.datodDb = i
        if self.ui.BoxId.currentText() == self.otra:
            self.datodDb = {'UrlFeedShowrss': '',
                            'RutaDescargas': '',
                            'UrlFeedNewpct': '',
                            'id': ''}

    def procesosComunes(self):
        """

        """

        self.averiguaConf()
        self.insertarSerie()

    def aplicaDatos(self):
        datos = {
            'ID': str(self.ui.BoxId.currentText()),
            'Newpct': str(self.ui.lineNewpct.text()),
            'showrss': str(self.ui.lineShowrss.text()),
            'Ruta': funciones.cambiaBarras(str(self.ui.lineRuta.text()))
        }

        if datos['ID'] == self.otra:
            print('insert')
            query = """INSERT INTO Configuraciones(UrlFeedNewpct, UrlFeedShowrss, RutaDescargas) VALUES ("{}", "{}", 
            "{}")""".format(datos['Newpct'], datos['showrss'], datos['Ruta'])

            if modo_debug:
                print('update')
                print(query)

            conectionSQLite(self.db, query)
            self.operacionesIniciales()
        else:
            query = """UPDATE Configuraciones SET UrlFeedNewpct="{}", UrlFeedShowrss="{}", RutaDescargas="{}"
            WHERE ID LIKE {}""".format(datos['Newpct'], datos['showrss'], datos['Ruta'], datos['ID'])

            if modo_debug:
                print('update')
                print(query)

            conectionSQLite(self.db, query)

        with open(r'{}/id.conf'.format(self.ruta), 'w') as f:
            f.write(datos['ID'])

        return True

    def insertarSerie(self):
        """

        """

        self.ui.lineNewpct.setText(self.datodDb['UrlFeedNewpct'])
        self.ui.lineShowrss.setText(self.datodDb['UrlFeedShowrss'])
        self.ui.lineRuta.setText(str(self.datodDb['RutaDescargas']))

    def cancela(self):
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.estadoA = self.estadoF
        self.reject()

    def aceptaDatos(self):
        """
        Boton Aceptar, primero aplicas los datos, si retorna True, cierra la ventana
        """

        if self.aplicaDatos():
            self.accept()

    @staticmethod
    def getDatos(parent=None, dbSeries=None):
        dialog = Preferencias(parent, dbSeries)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    Preferencias.getDatos(dbSeries=ruta_db)
    return app


# revisar cuando pongo otra, poner insetar en vez de otra
if __name__ == '__main__':
    main()
