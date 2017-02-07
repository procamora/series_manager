#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtWidgets

from ui.estado_series_ui import Ui_Dialog
from modulos.tviso import conectTviso
from modulos.connect_sqlite import conectionSQLite, ejecutaScriptSqlite
from modulos.settings import modo_debug, ruta_db


class MiFormulario(QtWidgets.QDialog):
    def __init__(self, parent=None, dbSeries=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.EstadoI = 'Ok' # estado inicial
        self.EstadoF = 'Cancelado' #final
        self.EstadoA = self.EstadoI #actual
        self.db = dbSeries

        self.QueryCompleta = str()   # str de consultas que se ejecutaran al final

        self.setWindowTitle('Estado de series Activas')

        # esto permite selecionar multiples
        self.ui.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.__sacaSeries()

        self.ui.radioButtonEmpieza.clicked.connect(self.__seriesEmpiezanTemporada)
        self.ui.radioButtonAcabaT.clicked.connect(self.__temporadaAcabada)
        self.ui.radioButtonFinalizada.clicked.connect(self.__serieFinalizada)

        self.ui.pushButtonRefresh.clicked.connect(self.__sacaSeries)

        self.ui.pushButtonAnadir.clicked.connect(self.__printCurrentItems)

        self.ui.pushButtonAplicar.clicked.connect(self.__aplicaDatos)
        self.ui.pushButtonCerrar.clicked.connect(self.__cancela)
        self.ui.pushButtonAceptar.clicked.connect(self.__aceptaDatos)



    def __sacaSeries(self):
        '''
        Saca todas las series de la bd y las mete en una lista de diccionarios
        accesible en todo el objeto
        '''
        query = '''SELECT Nombre FROM Series WHERE Estado LIKE "En Espera" AND Capitulo LIKE 0'''
        self.DatSeriesEmpiezanTemporada =  conectionSQLite(self.db, query, True)

        query = '''SELECT ID, Nombre, Estado, imdb_Finaliza FROM Series WHERE imdb_Finaliza <> "????" AND
            Capitulo LIKE imdb_Capitulos AND Estado <> "Finalizada"'''
        self.DatSerieFinalizada =  conectionSQLite(self.db, query, True)

        query = '''SELECT ID, Nombre, Estado, imdb_Finaliza FROM Series WHERE imdb_Finaliza LIKE "????" AND
            Capitulo LIKE imdb_Capitulos'''
        self.DatTemporadaAcabada =  conectionSQLite(self.db, query, True)

        query = '''SELECT ID, Nombre, Temporada, Capitulo, imdb_Temporada, imdb_Capitulos FROM Series
            WHERE Estado LIKE "Finalizada" AND Acabada LIKE "Si" AND (Capitulo <> imdb_Capitulos OR
            Temporada <> imdb_Temporada)'''
        self.DatSeriesFinalizadas =  conectionSQLite(self.db, query, True)

        self.ui.radioButtonFinalizada.setChecked(True)
        self.__serieFinalizada() # lo ejecuto al principio ya que es el activado por defecto

        #self.actuales = conectTviso()


    def __botonSiguiendo(self, seriesTest):
        '''
        Creo una lista con todas las series que estoy siguiendo
        '''

        self.ui.listWidget.clear()
        if len(seriesTest) != 0:
            for i in seriesTest:
                item=QtWidgets.QListWidgetItem()
                item.setText(i['Nombre'])
                self.ui.listWidget.addItem(item)
            self.ui.pushButtonAnadir.setVisible(True)

        else:
            item=QtWidgets.QListWidgetItem()
            item.setText('No hay ninguna serie')
            self.ui.listWidget.addItem(item)
            self.ui.pushButtonAnadir.setVisible(False)

        try:   # si no hay ninguno, da fallo
            # establezco por defecto el ultimo, que es el que tiene el valor del item
            self.ui.listWidget.setCurrentItem(item)
        except:
            pass


    def __aplicaDatos(self):
        '''
        Ejecuta todas las consultas que hay en la lista
        '''

        if modo_debug:
            print((self.QueryCompleta))

        ejecutaScriptSqlite(self.db, self.QueryCompleta)

        self.QueryCompleta = str()
        return True


    def __cancela(self):
        '''
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        '''

        self.EstadoA = self.EstadoF
        self.reject()


    def __serieFinalizada(self):
        #coge las series de imdb y actualiza la table de estado
        #query = 'SELECT ID, Nombre, Estado, imdb_Finaliza FROM Series'
        #revisar porque puedo ESTAR VIENDO UNA SERIE FINALIZADA Y NO QUIERO QUE CAMBIE ESTADO
        self.__botonSiguiendo(self.DatSerieFinalizada)


    def __temporadaAcabada(self):
        self.__botonSiguiendo(self.DatTemporadaAcabada)


    def __seriesFinalizadas(self):
        #busca las series finalizadas y las actualiza con el ultimo episodio si la he acabado de ver,
        #NO HAY IMPLEMENTADO BOTON PARA ELLO, solo lo ejecuto a pelo cuando lo necesito

        self.__botonSiguiendo(self.DatSeriesFinalizadas)

        for DatSer in self.DatSeriesFinalizadas:
            query = '''UPDATE series SET Temporada=imdb_Temporada, Capitulo=imdb_Capitulos
                WHERE Nombre LIKE "{}"'''.format(DatSer['Nombre'])
            print(query)
            conectionSQLite(self.db, query)


    def __seriesEmpiezanTemporada(self):
        #cuidado, si lo ejecutas la misma semana que acabas la temporada se pondra en activa,
        #hay que ejecurtarlo 1 vez a la semana
        #buscar forma de hacer que haga una comprobacion con las series que den positivo

        Calendario = list(dict())
        for i in self.actuales:   # lista de series de tviso
            # lista de series que estan a la espera de una nueva temporada
            for j in self.DatSeriesEmpiezanTemporada:
                #http:/stackoverflow.com/questions/8214932/how-to-check-if-a-value-exists-in-a-dictionary-python
                if i in list(j.values()):
                    # hago una lista de diccionarios, porque asi la tengo deficina de __botonSiguiendo
                    Calendario.append({'Nombre': str(i)})

        self.__botonSiguiendo(Calendario)


    def __printCurrentItems(self):
        '''
        Coge todas las series seleccionadas y las mete en una lista con su
        respectiva consulta para despues ejecutarlas
        '''

        for i in self.ui.listWidget.selectedItems():

            if self.ui.radioButtonAcabaT.isChecked():
                query = '''UPDATE series SET Temporada=Temporada+1, Capitulo="00", Estado="En Espera"
                    WHERE Nombre Like "{}";'''.format(i.text())
                self.QueryCompleta += '\n'+query

            elif self.ui.radioButtonEmpieza.isChecked():
                query = '''UPDATE series SET Capitulo="01", Estado="Activa" WHERE Nombre Like "{}";'''.format(i.text())
                self.QueryCompleta += '\n'+query

            elif self.ui.radioButtonFinalizada.isChecked():
                query = '''UPDATE series SET Estado="Finalizada", Acabada="Si", Siguiendo="No"
                    WHERE Nombre Like "{}";'''.format(i.text())
                self.QueryCompleta += '\n'+query

        if modo_debug:
            print((self.QueryCompleta))


    def __aceptaDatos(self):
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


if __name__ == '__main__':
    main()


#HACER FUNCION QUE COJA

#actualizar_insertar series en espera
#UPDATE series  SET Estado='En Espera' WHERE Capitulo LIKE '0'

#SERIE ACABADA
#UPDATE series SET Siguiendo='No', Acabada='Si', Estado='Finalizada' WHERE ID LIKE 33

#SELECT Nombre FROM Series WHERE Estado NOT LIKE "Activa" AND Estado NOT LIKE "En Espera" AND Estado NOT LIKE "Finalizada"
