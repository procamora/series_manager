#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtWidgets

from ui.preferencias_ui import Ui_Dialog
from modulos.connect_sqlite import conectionSQLite
from modulos.settings import modo_debug, directorio_local, ruta_db
import funciones


class MiFormulario(QtWidgets.QDialog):
    def __init__(self, parent=None, dbSeries=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.Otra = 'Otra'  # campo otra del formulario
        self.EstadoI = 'Ok' # estado inicial
        self.EstadoF = 'Cancelado' #final
        self.EstadoA = self.EstadoI #actual
        self.db = dbSeries
        self.ruta = directorio_local
        funciones.creaDirectorioTrabajo()
        self.setWindowTitle('Preferencias de configuracion')
        self.ui.tabWidget.setCurrentIndex(0)

        self.__operacionesIniciales()

        AllItems = [self.ui.BoxId.itemText(i) for i in range(self.ui.BoxId.count())]   # recogo todos los dias de la caja y le paso el indice del dia en el que sale
        with open(r'{}/id.conf'.format(self.ruta), 'r') as f:
            id_fich = f.readline().replace('/n','')

        try:
            self.ui.BoxId.setCurrentIndex(AllItems.index(id_fich))
        except:
            self.ui.BoxId.setCurrentIndex(AllItems.index('1')) # si da error por algun motivo pongo el primero

        self.__procesosComunes()

        self.ui.pushButton.clicked.connect(self.__buscarDirectorio)
        self.ui.BoxId.activated.connect(self.__procesosComunes)

        self.ui.pushButtonAplicar.clicked.connect(self.__aplicaDatos)
        self.ui.pushButtonCerrar.clicked.connect(self.__cancela)
        self.ui.pushButtonAceptar.clicked.connect(self.__aceptaDatos)


    def __operacionesIniciales(self):
        self.__sacaDatos()
        self.__listaId()


    def __buscarDirectorio(self):
        """
        Se encarga de coger la ruta en la que vamos a guardar el fichero, en este caso solo buscamos directorios,
        y establecemos que la ruta raiz sea el escrotorio, que se establece en el init
        """

        #filenames = QtGui.QFileDialog.getOpenFileName()
        filenames = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Directory",
            str(self.ui.lineRuta.text()),
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks)

        if filenames is not None:
        #if not (filenames.isNull()): en python 3 filenames ya no es un QString sino str
            self.ui.lineRuta.setText(filenames)


    def __sacaDatos(self):
        '''

        '''

        query = 'SELECT * FROM Configuraciones'
        self.ser = conectionSQLite(self.db, query, True)
        self.DatodDb = self.ser[0]


    def __listaId(self):
        '''

        '''

        lista = list()
        for i in self.ser:
            lista.append(str(i['id']))

        self.ui.BoxId.clear()
        self.ui.BoxId.addItems(lista)
        self.ui.BoxId.addItem(self.Otra)


    def __averiguaConf(self):
        '''

        '''

        for i in self.ser:
            if str(self.ui.BoxId.currentText()) == str(i['id']):
                if modo_debug:
                    print((self.ui.BoxId.currentText()))
                    print(i)
                self.DatodDb = i
        if  self.ui.BoxId.currentText() == self.Otra:
            self.DatodDb = {'UrlFeedShowrss': '',
                'RutaDescargas': '',
                'UrlFeedNewpct': '',
                'id': ''}


    def __procesosComunes(self):
        '''

        '''

        self.__averiguaConf()
        self.__insertarSerie()


    def __aplicaDatos(self):
        datos = {
            'ID': str(self.ui.BoxId.currentText()),
            'Newpct': str(self.ui.lineNewpct.text()),
            'showrss': str(self.ui.lineShowrss.text()),
            'Ruta': funciones.cambiaBarras(str(self.ui.lineRuta.text()))
        }

        if datos['ID'] == self.Otra:
            print('insert')
            query = '''INSERT INTO Configuraciones(UrlFeedNewpct, UrlFeedShowrss, RutaDescargas)
VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}")'''.format(datos['Newpct'], datos['showrss'], datos['Ruta'])

            if modo_debug:
                print('update')
                print(query)

            conectionSQLite(self.db, query)
            self.__operacionesIniciales()
        else:
            query = '''UPDATE Configuraciones SET UrlFeedNewpct="{}", UrlFeedShowrss="{}", RutaDescargas="{}"
            WHERE ID LIKE {}'''.format(datos['Newpct'], datos['showrss'], datos['Ruta'], datos['ID'])

            if modo_debug:
                print('update')
                print(query)

            conectionSQLite(self.db, query)

        with open(r'{}/id.conf'.format(self.ruta), 'w') as f:
            f.write(datos['ID'])

        return True


    def __insertarSerie(self):
        '''

        '''

        self.ui.lineNewpct.setText(self.DatodDb['UrlFeedNewpct'])
        self.ui.lineShowrss.setText(self.DatodDb['UrlFeedShowrss'])
        self.ui.lineRuta.setText(str(self.DatodDb['RutaDescargas']))


    def __cancela(self):
        '''
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        '''

        self.EstadoA = self.EstadoF
        self.reject()


    def __aceptaDatos(self):
        """
        Boton Aceptar, primero aplicas los datos, si retorna True, cierra la ventana
        """

        if self.__aplicaDatos():
            self.accept()


    @staticmethod
    def getDatos(parent=None, dbSeries=None):
        dialog = MiFormulario(parent, dbSeries)
        dialog.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    MiFormulario.getDatos(dbSeries=ruta_db)
    return app

# revisar cuando pongo Otra, poner insetar en vez de otra
if __name__ == '__main__':
    main()
