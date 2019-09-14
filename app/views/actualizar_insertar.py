#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from typing import Dict, NoReturn

from PyQt5 import QtWidgets
from app.views.ui.actualizar_insertar_ui import Ui_Dialog

from app import logger
from app.modulos import funciones
from app.modulos.actualiza_imdb import actualizaImdb
from app.modulos.connect_sqlite import conectionSQLite
from app.modulos.settings import ruta_db
from app.views.msgbox import MsgBox


class ActualizarInsertar(QtWidgets.QDialog):
    def __init__(self, parent=None, database: str = None, datSerie: Dict = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.other = 'otra'  # campo otra del formulario
        self.state_ok = 'Ok'  # estado inicial
        self.state_cancel = 'Cancelado'  # final
        self.state_current = self.state_ok  # actual
        self.db = database
        self.datSerie = datSerie

        # para todos establezco esto que el estado es Activa, si actualizo lo
        # modifico en la funcion creaConf
        self.list_states()

        all_items = [self.ui.BoxEstado.itemText(i) for i in range(self.ui.BoxEstado.count())]
        if len(all_items) > 0:
            self.ui.BoxEstado.setCurrentIndex(all_items.index('Activa'))

        if self.datSerie is not None:  # Actualizar
            self.setWindowTitle('Actualizar serie: {}'.format(self.datSerie['Nombre']))

            # para poder modifical el nombre en el update
            self.name_original = str(self.datSerie['Nombre'])

            self.ui.pushButtonAplicar.setText('Actualizar')
            self.creaConf()
        else:  # Insertar
            self.setWindowTitle('Insertar Serie')
            self.ui.pushButtonAplicar.setText('Insertar')

            # Generar checkbox
            self.listaTemporadas(1, 5)
            self.listaCapitulos(1, 13)

            # pongo la fecha de hoy para insertar por defecto
            # recogo todos los dias de la caja y le paso el indice del dia en
            # el que sale
            all_items = [self.ui.BoxEmision.itemText(i) for i in range(self.ui.BoxEmision.count())]
            if len(all_items) > 0:
                self.ui.BoxEmision.setCurrentIndex(all_items.index(funciones.calculaDiaSemana()))

        # Ocultar textos
        self.ui.lineTemp.hide()
        self.ui.lineCapitulo.hide()

        self.ui.lineTemp.setText(str(self.ui.BoxTemporada.currentText()))
        self.ui.lineCapitulo.setText(str(self.ui.BoxCapitulo.currentText()))

        # conectores
        self.ui.BoxTemporada.activated.connect(self.campoTemp)
        self.ui.BoxCapitulo.activated.connect(self.campoCap)

        self.ui.pushButtonAplicar.clicked.connect(self.apply_data)
        self.ui.pushButtonCerrar.clicked.connect(self.cancel)
        self.ui.pushButtonAceptar.clicked.connect(self.accept_data)

    def campoTemp(self) -> NoReturn:
        """
        Si en la lista de temporadas seleccionamos otra se abre un line edit
        para poner el numero de temporada que no esta, si lo cambiamos se oculta
        """

        if self.ui.BoxTemporada.currentText() == self.other:
            self.ui.lineTemp.setEnabled(True)
            self.ui.lineTemp.setVisible(True)
            self.ui.lineTemp.setText('')
        else:
            self.ui.lineTemp.setEnabled(False)
            self.ui.lineTemp.setVisible(False)
            self.ui.lineTemp.setText(str(self.ui.BoxTemporada.currentText()))

    def campoCap(self) -> NoReturn:
        """
        Si en la lista de capitulos seleccionamos otra se abre un line edit
        para poner el numero de capitulo que no esta, si lo cambiamos se oculta
        """

        if str(self.ui.BoxCapitulo.currentText()) == self.other:
            self.ui.lineCapitulo.setEnabled(True)
            self.ui.lineCapitulo.setVisible(True)
            self.ui.lineCapitulo.setText('')
        else:
            self.ui.lineCapitulo.setEnabled(False)
            self.ui.lineCapitulo.setVisible(False)
            self.ui.lineCapitulo.setText(
                str(self.ui.BoxCapitulo.currentText()))

    def listaTemporadas(self, x: int, y: int) -> NoReturn:
        """
        Crea el comboBox de las temporadas, primero lo vacia y
        luego lo crea con los rangos que le indico
        """

        listTemp = list()
        for i in range(x, y):
            listTemp.append(str(i))

        self.ui.BoxTemporada.clear()
        self.ui.BoxTemporada.addItems(listTemp)
        self.ui.BoxTemporada.addItem(self.other)

    def listaCapitulos(self, x: int, y: int) -> NoReturn:
        """
        Crea el comboBox de los capitulos, primero lo vacia y
        luego lo crea con los rangos que le indico
        """

        listCap = list()
        for i in range(x, y):
            listCap.append(str(i))

        self.ui.BoxCapitulo.clear()
        self.ui.BoxCapitulo.addItems(listCap)
        self.ui.BoxCapitulo.addItem(self.other)

    def list_states(self) -> NoReturn:
        """
        Crea el comboBox de los estados, primero lo vacia y
        luego lo crea con los rangos que le indico
        """
        estados = 'SELECT * FROM ID_Estados'
        query_estados = conectionSQLite(self.db, estados, True)
        listEst = list()
        for i in query_estados:
            listEst.append(i['Estados'])

        self.ui.BoxEstado.clear()
        self.ui.BoxEstado.addItems(listEst)

    def creaConf(self) -> NoReturn:
        """
        Establece los valores por defecto que se le indican en caso de que se indiquen
        """
        logger.debug(self.datSerie)

        self.ui.lineTitulo.setText(self.datSerie['Nombre'])

        # Generar checkbox
        self.listaTemporadas(self.datSerie['Temporada'], self.datSerie['Temporada'] + 2)
        self.listaCapitulos(self.datSerie['Capitulo'], self.datSerie['Capitulo'] + 8)

        if self.datSerie['Siguiendo'] == 'Si':
            self.ui.radioSeguirSi.click()
        else:
            self.ui.radioSeguirNo.click()

        # recogo todos los dias de la caja y le paso el indice del dia en el que sale
        all_items = [self.ui.BoxEmision.itemText(i) for i in range(self.ui.BoxEmision.count())]
        if len(all_items) > 0:
            self.ui.BoxEmision.setCurrentIndex(all_items.index(self.datSerie['Dia']))

        if self.datSerie['VOSE'] == 'Si':
            self.ui.radioVOSE_Si.click()
        else:
            self.ui.radioVOSE_No.click()

        if self.datSerie['Acabada'] == 'Si':
            self.ui.radioAcabadaSi.click()
        else:
            self.ui.radioAcabadaNo.click()

        all_items = [self.ui.BoxEstado.itemText(i) for i in range(self.ui.BoxEstado.count())]
        if len(all_items) > 0:
            self.ui.BoxEstado.setCurrentIndex(all_items.index(self.datSerie['Estado']))

        if self.datSerie['imdb_id'] is not None:
            self.ui.lineImdb.setText(self.datSerie['imdb_id'])

        self.ui.radioImdbNo.click()

    def apply_data(self) -> bool:
        """
        Recoge todos los valores que necesita, crea el update y lo ejecuta
        """

        self.ui.label_Info.setText('')
        if self.ui.radioVOSE_Si.isChecked():
            vose = 'Si'
        else:
            vose = 'No'

        if self.ui.radioAcabadaSi.isChecked():
            acabada = 'Si'
        else:
            acabada = 'No'

        if self.ui.radioImdbSi.isChecked():
            imdb = 'Si'
        else:
            imdb = 'No'

        if self.ui.radioSeguirSi.isChecked():
            seguir = 'Si'
        else:
            seguir = 'No'

        if len(str(self.ui.lineImdb.text())) == 0:  # añadido de insertar
            str_imdb = 'NULL'
        else:
            str_imdb = str(self.ui.lineImdb.text())

        datos = {
            'Titulo': str(self.ui.lineTitulo.text()).lstrip().rstrip(),
            'Temporada': str(self.ui.lineTemp.text()),
            'Capitulo': str(self.ui.lineCapitulo.text()),
            'Seguir': seguir,
            'Emision': str(self.ui.BoxEmision.currentText()),
            'VOSE': vose,
            'Acabada': acabada,
            'Estado': str(self.ui.BoxEstado.currentText()),
            'idImdb': str_imdb,
            'ImdbLanzar': imdb
        }

        # Nombre vacia produce errores al descargar series
        if len(str(self.ui.lineTitulo.text())) != 0:
            # HAGO ESTO PARA QUE EL UPDATE SE HAGA CON NONE EN CASO DE QUE NO LO PONGA
            if len(str(self.ui.lineImdb.text())) == 0:
                if self.datSerie is not None:
                    query = '''UPDATE series SET Nombre="{}", Temporada={}, Capitulo={}, Siguiendo="{}", Dia="{}", 
                    VOSE="{}", Acabada="{}", Estado="{}",imdb_id={} WHERE Nombre="{}"'''.format(
                        datos['Titulo'], datos['Temporada'], datos['Capitulo'], datos['Seguir'], datos['Emision'],
                        datos['VOSE'], datos['Acabada'], datos['Estado'], datos['idImdb'], self.name_original)
                else:
                    query = '''INSERT INTO series(Nombre, Temporada, Capitulo, Siguiendo, Dia, VOSE, Acabada, Estado, 
                    imdb_id) VALUES ("{}", {}, {}, "{}", "{}", "{}", "{}", "{}", {})'''.format(
                        datos['Titulo'], datos['Temporada'], datos['Capitulo'], datos['Seguir'], datos['Emision'],
                        datos['VOSE'], datos['Acabada'], datos['Estado'], datos['idImdb'])
            else:
                if self.datSerie is not None:
                    query = '''UPDATE series SET Nombre="{}", Temporada={}, Capitulo={}, Siguiendo="{}", Dia="{}", 
                    VOSE="{}", Acabada="{}", Estado="{}",imdb_id="{}" WHERE Nombre="{}"'''.format(
                        datos['Titulo'], datos['Temporada'], datos['Capitulo'], datos['Seguir'], datos['Emision'],
                        datos['VOSE'], datos['Acabada'], datos['Estado'], datos['idImdb'], self.name_original)
                else:
                    query = '''INSERT INTO series(Nombre, Temporada, Capitulo, Siguiendo, Dia, VOSE, Acabada, Estado, 
                  imdb_id) VALUES ("{}", {}, {}, "{}", "{}", "{}", "{}", "{}", "{}")'''.format(
                        datos['Titulo'], datos['Temporada'], datos['Capitulo'], datos['Seguir'], datos['Emision'],
                        datos['VOSE'], datos['Acabada'], datos['Estado'], datos['idImdb'])
            try:
                logger.debug(query)
                if datos['ImdbLanzar'] == 'Si':
                    imbd_test = actualizaImdb()

                    if imbd_test.compruebaTitulo(datos['idImdb']):
                        self.execute_imdb()
                        conectionSQLite(self.db, query)
                        # Si es una inserccion despues de insertar vacio el
                        # titulo para poder hacer mas
                        if self.datSerie is None:
                            funciones.muestraMensaje(self.ui.label_Info, 'Insertado con imdb', True)
                            self.ui.lineTitulo.setText('')
                        else:
                            funciones.muestraMensaje(self.ui.label_Info, 'Actualizado con imdb', True)
                    else:  # Si da error no quiero que borre el nombre
                        funciones.muestraMensaje(self.ui.label_Info, 'fallo en imdb', False)
                else:
                    conectionSQLite(self.db, query)
                    # Si es una inserccion despues de insertar vacio el titulo
                    # para poder hacer mas
                    if self.datSerie is None:
                        funciones.muestraMensaje(self.ui.label_Info, 'Insertado', True)
                        self.ui.lineTitulo.setText('')
                    else:
                        funciones.muestraMensaje(self.ui.label_Info, 'Actualizado', True)
                return True

            except Exception as e:
                logger.error(e)
                dat = {'title': 'Error en bd', 'text': str(e)}
                MsgBox.getData(datos=dat)
                return False
        else:
            funciones.muestraMensaje(self.ui.label_Info, 'Titulo vacio', False)
            return False

    def execute_imdb(self) -> NoReturn:
        """
        Actualiza los datos de la serie de imdb siempre que el id no este vacio
        """

        a = actualizaImdb()
        id_imdb = str(self.ui.lineImdb.text())
        if len(id_imdb) > 0:
            logger.debug('actualiza imdb')
            a.actualizaSerie(id_imdb)

    def accept_data(self) -> NoReturn:
        """
        Boton Aceptar, primero aplicas los datos, si retorna True, cierra la ventana
        """

        if self.apply_data():
            self.accept()

    def cancel(self) -> NoReturn:
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.state_current = self.state_cancel
        self.reject()

    @staticmethod
    def get_data(parent: object = None, data_serie: Dict = None, database: str = None) -> NoReturn:
        dialog = ActualizarInsertar(parent, database, data_serie)
        dialog.exec_()


def main():
    # query = 'SELECT * FROM Series WHERE Nombre LIKE "Silicon Valley"'
    # configuracion = conectionSQLite('{}/{}'.format(directorio_trabajo, nombre_db), query, True)[0]
    ser = None
    app = QtWidgets.QApplication(sys.argv)
    # hay que poner la base de datos como parametro
    ActualizarInsertar.get_data(database=ruta_db, data_serie=ser)
    return app


if __name__ == '__main__':
    main()
