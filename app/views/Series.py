#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SISTEMA
import functools
import os
import subprocess
import sys
from typing import List, NoReturn

# TERCEROS
from PyQt5 import QtGui, QtWidgets, QtCore
from app.views.ui.series_ui import Ui_MainWindow

# PROPIAS
import app.controller.Controller as Controller
from app import logger
from app.models.model_serie import Serie
from app.modulos import funciones
from app.modulos.settings import DIRECTORY_WORKING, SYSTEM, NAME_DATABASE, DIRECTORY_LOCAL
from app.views import acerca_de
from app.views import actualizar_insertar
from app.views import asistente_inicial
from app.views import buscar_series
from app.views import descarga_automatica
from app.views import estado_series
from app.views import lista_activa
from app.views import listar_todas
from app.views import msgbox
from app.views import newpct1_completa
from app.views import notificaciones
from app.views import preferencias
from app.models.model_query import Query

class Series(QtWidgets.QMainWindow):
    def __init__(self, parent: object = None) -> NoReturn:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.database: str = f'{DIRECTORY_WORKING}/{NAME_DATABASE}'

        self.other: str = 'otra'  # campo otra del formulario
        self.state_ok: str = 'Ok'  # estado inicial
        self.state_cancel: str = 'Cancelado'  # final
        self.state_current: str = self.state_ok  # actual
        # CUIADO REVISAR ESTO Y UNIFICADO TODOS LOS NOMBRE DE LA DB
        self.db: str = self.database
        self.queryCompleta: str = str()  # lista de consultas que se ejecutaran al final

        self.setWindowTitle('Gestor de Series by Pablo')

        self.init_active_list()  # Crea toda la vista del menu
        funciones.create_full_backup_db()
        self.menus()

    def init_active_list(self) -> NoReturn:

        self.ui.gridLayoutGobal = QtWidgets.QGridLayout(self.ui.scrollAreaWidgetContents)
        response_query = Controller.get_series_follow_active(self.db)

        # todo esto es para ordenar las series por fecha de proximidad de proximo capitulo
        fecha2 = funciones.calculate_day_week()
        fecha_orde = funciones.date_to_number(fecha2)
        listado_final = self.sort_series(fecha_orde, response_query.response)

        for texto, i in zip(listado_final, list(range(0, len(listado_final)))):  # el encabezado lo tengo encima
            self.create_list_serie(i, texto)
            logger.debug(f'{i}-> {texto}')

        self.ui.pushButtonAceptar.setVisible(False)
        self.ui.pushButtonAplicar.setText("Guardar")
        self.ui.pushButtonAplicar.clicked.connect(self.apply_data)
        self.ui.pushButtonCerrar.clicked.connect(self.cancel)
        self.ui.pushButtonAceptar.clicked.connect(self.accept_data)

    def create_list_serie(self, n: int = 0, serie: Serie = None) -> NoReturn:
        """
        Crea la linea de cada serie completa, generada por qtdesigner y pasado
        el codigo a python, despues visto como se crea y hecho algunas modificaciones

        param n int: se usa para dar formato estilo tabla, empieza en 0 y va hasta
        el numero de series que haya

        param datos dict: diccionario con todos los datos de la serie a la que se crea una linea
        """

        label_emision = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.gridLayoutGobal.addWidget(label_emision, n, 0, 1, 1, QtCore.Qt.AlignLeft)

        label_nombre = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.gridLayoutGobal.addWidget(label_nombre, n, 1, 1, 1, QtCore.Qt.AlignLeft)

        line_episodio = QtWidgets.QLineEdit(self.ui.scrollAreaWidgetContents)
        line_episodio.setEnabled(False)
        line_episodio.setMaximumSize(QtCore.QSize(50, 20))
        line_episodio.setReadOnly(True)
        self.ui.gridLayoutGobal.addWidget(line_episodio, n, 2, 1, 1, QtCore.Qt.AlignLeft)

        widget_botones = QtWidgets.QWidget(self.ui.scrollAreaWidgetContents)
        widget_botones.setMaximumSize(QtCore.QSize(90, 45))
        horizontal_layout_botones = QtWidgets.QHBoxLayout(widget_botones)
        button_restar = QtWidgets.QPushButton(widget_botones)
        horizontal_layout_botones.addWidget(button_restar)
        button_sumar = QtWidgets.QPushButton(widget_botones)
        horizontal_layout_botones.addWidget(button_sumar)
        self.ui.gridLayoutGobal.addWidget(widget_botones, n, 3, 1, 1, QtCore.Qt.AlignLeft)

        label_emision.setText(serie.day)
        label_nombre.setText(serie.title)
        # hago esto para que quede bonito los numeros de los capitulos
        line_episodio.setText(f'{serie.get_season_chapter()}')
        button_sumar.setText("+1")
        button_restar.setText("-1")

        # Conexion de los botones sumar y restar enviando la referencia del objeto para trabajar con ella posteriormente
        button_sumar.clicked.connect(functools.partial(self.add_serie, line_episodio, serie))
        button_restar.clicked.connect(functools.partial(self.sub_serie, line_episodio, serie))

        # Widget para meter el QLineEdit y QPushButton
        widget_teoricos = QtWidgets.QWidget(self.ui.scrollAreaWidgetContents)
        widget_teoricos.setMaximumSize(QtCore.QSize(90, 45))
        horizontal_layout_teoricos = QtWidgets.QHBoxLayout(widget_teoricos)

        # Temporada y capitulo teorico
        line_episodio_teorico = QtWidgets.QLineEdit(self.ui.scrollAreaWidgetContents)
        line_episodio_teorico.setEnabled(False)
        line_episodio_teorico.setReadOnly(True)
        line_episodio_teorico.setMaximumSize(QtCore.QSize(30, 20))

        # Boton para actualizar el estado conforme al descargado automaticamente
        button_teorico = QtWidgets.QPushButton(widget_teoricos)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        button_teorico.setIcon(icon)

        # Spacer para que se vea bonito cuando ocultamos el boton
        spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        # Incluimos todos al Widget
        horizontal_layout_teoricos.addWidget(line_episodio_teorico)
        horizontal_layout_teoricos.addWidget(button_teorico)
        horizontal_layout_teoricos.addItem(spacer_item)
        self.ui.gridLayoutGobal.addWidget(widget_teoricos, n, 4, 1, 1, QtCore.Qt.AlignLeft)

        # Si el capitulo es None o ya lo tengo actualizado no muestro el boton
        if serie.chapter_downloaded is not None and serie.chapter != serie.chapter_downloaded:
            line_episodio_teorico.setText(str(serie.chapter_downloaded))  # Asignamos el valor del capitulo
        else:
            line_episodio_teorico.setVisible(False)
            button_teorico.setVisible(False)

        button_teorico.clicked.connect(
            functools.partial(self.button_teoric, line_episodio_teorico, line_episodio, serie))

    def button_teoric(self, capitulo_t: QtWidgets.QLineEdit, capitulo: QtWidgets.QLineEdit, dat: Serie) -> NoReturn:
        """
        Calcula si el capitulo descargado es mayor o menor, despues el bucle se ejecuta la diferencia entre los
        capitulos ejecutando la funcion         de sumar o restar capitulos
        """

        cap = int(capitulo.text().split('x')[-1])
        cap_t = int(capitulo_t.text())

        if cap_t > cap:
            for i in range(0, cap_t - cap):
                logger.debug(f'Suma: {i}')
                self.add_serie(capitulo, dat)
        else:
            for i in range(0, cap_t - cap):
                logger.debug(f'Resta: {i}')
                self.sub_serie(capitulo, dat)

    def add_serie(self, qline_edit: QtWidgets.QLineEdit, serie: Serie) -> NoReturn:
        """
        Tiene 2 funcionalidades:
            - 1: sumar un capitulo a numero de capitulo que se ve por pantalla de la serie
            - 2: crear una query para actualizar_insertar la bd y la mete en una lista para su posterior ejecucion

        param n object: objeto que hace referencia al campo donde sale temporada y capitulo que se modificara
        param dat dict: diccionario con todos los datos de la serie que me modificara
        """

        serie.chapter += 1  # esto funciona porque hace referencia al objeto
        qline_edit.setText(serie.get_season_chapter())

        # fixme meter en controller
        query = f'''UPDATE series SET Capitulo=Capitulo+1 WHERE Nombre LIKE "{serie.title}";'''
        self.queryCompleta += '\n' + query
        logger.debug(query)

    def sub_serie(self, qline_edit: QtWidgets.QLineEdit, serie: Serie) -> NoReturn:
        """
        Tiene 2 funcionalidades,
            - 1: restar un capitulo a numero de capitulo que se ve por pantalla de la serie
            - 2: crear una query para actualizar_insertar la bd y la mete en una lista para su posterior ejecucion

        param n object: objeto que hace referencia al campo donde sale temporada y capitulo que se modificara
        param dat dict: diccionario con todos los datos de la serie que me modificara
        """

        serie.chapter = serie.chapter - 1  # esto funciona porque hace referencia al objeto
        qline_edit.setText(serie.get_season_chapter())

        # fixme meter en controller
        query = f'UPDATE series SET Capitulo=Capitulo-1 WHERE Nombre LIKE "{serie.title}";'
        self.queryCompleta += '\n' + query
        logger.debug(query)

    def cancel(self) -> NoReturn:
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.state_current = self.state_cancel
        self.close()

    def apply_data(self) -> bool:
        """
        Recorre toda la lista de updates alctualizando todas las series,
        cuando termina vacia la lista por si volvemos a darle a aplicar,
        asi evitamos que se ejecute dos veces la misma lista
        """

        logger.debug(self.queryCompleta)
        Controller.execute_query_script_sqlite(self.db, self.queryCompleta)

        self.queryCompleta = str()  # por si vuelvo a darle al boton aplicar
        return True

    @staticmethod
    def sort_series(semana: List, series: List) -> List[Serie]:
        """
        creo una lista ordenada por dia de la semana
        """

        lista = list()
        # none es el valor por defecto de la bd cuando no hay dia
        semana.extend(['None'])

        for i in semana:
            for j in series:
                if j.day == i:
                    lista.append(j)
        return lista

    def accept_data(self) -> NoReturn:
        """
        Boton Aceptar, primero aplicas los datos, si retorna True, cierra la ventana
        """

        if self.apply_data():
            self.accept()

    def menus(self) -> NoReturn:
        # Crear menu nuevo completo
        """
        self.tools = self.menubar.addMenu('&Tools')
        prevMenu = self.tools.addMenu('Preview')
        prevMenu.addAction('Software', lambda: self.test('Hola'))
        """

        # SERIES
        self.ui.actionSeries_Activas.triggered.connect(self.menu_series_actives)
        self.ui.actionSeries_Activas.setShortcut('Ctrl+A')
        self.ui.actionSeries_Activas.setStatusTip('Edicion rapida de series activas')
        self.ui.actionModificacion_masiva.triggered.connect(self.menu_list)
        self.ui.actionModificacion_individual.triggered.connect(self.menu_serie_update)
        self.ui.actionModificacion_individual.setShortcut('Ctrl+F')
        self.ui.actionInsertar_Serie.triggered.connect(self.menu_insert)
        self.ui.actionInsertar_Serie.setShortcut('Ctrl+I')
        self.ui.actionInsertar_Serie.setStatusTip('insertar una nueva serie')

        self.ui.actionRevisar_Estados.triggered.connect(self.check_series_states)
        self.ui.actionRevisar_Estados.setShortcut('Ctrl+E')
        self.ui.actionRevisar_Estados.setStatusTip('Revisar estados de series')

        self.ui.actionSalir.triggered.connect(self.close)
        self.ui.actionSalir.setShortcut('Ctrl+X')
        self.ui.actionSalir.setStatusTip('Cerrar el programa')

        # HERRAMIENTRAS
        self.ui.actionActualizar_bd_de_Imdb.triggered.connect(self.menu_imdb_update)
        self.ui.actionDescarga_Automatica.triggered.connect(self.menu_download_automatic)
        self.ui.actionDescarga_Automatica.setShortcut('Ctrl+N')
        self.ui.actionDescarga_Automatica.setStatusTip('Descargar series')
        self.ui.actionDescargar_Serie_Completa.triggered.connect(self.menu_download_automatic_complete)
        self.ui.actionDescargar_Serie_Completa.setShortcut('Ctrl+M')
        self.ui.actionDescargar_Serie_Completa.setStatusTip('Descargar series por temporada')
        self.ui.actionAbrir_carpeta_de_datos.triggered.connect(self.open_directory_data)
        self.ui.actionAbrir_carpeta_de_datos.setStatusTip('Abrir directorio de datos del programa')

        # OPCIONES
        self.ui.actionPreferencias.triggered.connect(self.menu_preferences)
        self.ui.actionPreferencias.setShortcut('Ctrl+P')
        self.ui.actionPreferencias.setStatusTip('Edicion de preferencias')

        self.ui.actionNotificaciones.triggered.connect(self.menu_notifications)
        self.ui.actionNotificaciones.setShortcut('Ctrl+K')
        self.ui.actionNotificaciones.setStatusTip('Edicion de notificaciones')

        self.ui.actionLogNewpct1.triggered.connect(lambda: self.menu_select_log('newpct1'))
        self.ui.actionLogNewpct1.setShortcut('Ctrl+1')
        self.ui.actionLogNewpct1.setStatusTip('Vaciar el log de newpct1')

        self.ui.actionLogShowrss.triggered.connect(lambda: self.menu_select_log('showrss'))
        self.ui.actionLogShowrss.setShortcut('Ctrl+2')
        self.ui.actionLogShowrss.setStatusTip('Vaciar el log de showrss')

        self.ui.actionLogDescargas.triggered.connect(lambda: self.menu_select_log('Descargas'))
        self.ui.actionLogDescargas.setShortcut('Ctrl+3')
        self.ui.actionLogDescargas.setStatusTip('Vaciar el log de Descargas')

        self.ui.actionLogTodos.triggered.connect(lambda: self.menu_select_log('Todos'))
        self.ui.actionLogTodos.setShortcut('Ctrl+4')
        self.ui.actionLogTodos.setStatusTip('Vaciar todos los log')

        self.ui.actionAsistente_inicial.triggered.connect(self.menu_initial_assistant)
        self.ui.actionAsistente_inicial.setStatusTip('Edicion de preferencias')

        ################################################################################################################
        # revisar esto, hacer un for
        # self.ui.actionId_de_Opcion = self.ui.menuOpciones.addMenu('Id de Opcion')
        # self.ui.actionId_de_Opcion.addAction('Desplegable 1')
        # self.ui.actionId_de_Opcion.addAction('Desplegable 2')

        # A CERCA DE
        self.ui.actionAcerca_de.triggered.connect(self.menu_about)
        self.ui.actionAcerca_de.setShortcut('Ctrl+H')
        self.ui.actionAcerca_de.setStatusTip('A cerca de')

    def menu_series_actives(self) -> NoReturn:
        """
        Muestra todas las series activas con un boton de sumar o restar capitulos
        """

        lista_activa.ListaActiva.get_data(database=self.database)

    def menu_list(self) -> NoReturn:
        """
        Muestra las series para hacer modificaciones en masa
        """

        listar_todas.ListarTodas.get_data(database=self.database)

    def menu_serie_update(self) -> NoReturn:
        """
        Busca una serie especifica en la bd y te abre la ventana de modificacion de la serie
        """

        buscar_series.BuscarSeries.get_data(database=self.database)

    def menu_insert(self) -> NoReturn:
        """
        Abre una ventana para meter una nueva serie en la bd
        """

        actualizar_insertar.ActualizarInsertar.get_data(database=self.database)

    def check_series_states(self):
        """
        Revisa los estados de las series, si empiezan temporada, acaban temporadao acaban serie
        """

        estado_series.EstadoSeries.get_data(database=self.database)

    @staticmethod
    def menu_imdb_update() -> NoReturn:
        import app.modulos.actualiza_imdb as actualiza_imdb
        a = actualiza_imdb.UpdateImdb()
        logger.info('actulizaCompleto')
        a.update_completed()

    def menu_download_automatic(self) -> NoReturn:
        conf: Query = Controller.get_database_configuration(self.db)
        ruta_desc = str(conf['RutaDescargas'])  # es unicode

        if not os.path.exists(ruta_desc):
            dat = {'title': 'No existe el directorio', 'text': f'El directorio {ruta_desc} no existe'}
            msgbox.MsgBox.get_data(datos=dat)
        else:
            descarga_automatica.DescargaAutomatica.get_data(database=self.database)

    def menu_download_automatic_complete(self) -> NoReturn:
        preferences: Query = Controller.get_database_configuration(self.database)
        #ruta_desc = str(preferences.response[0].path_download)  # es unicode

        if not os.path.exists(preferences.response[0].path_download):
            dat = {'title': 'No existe el directorio',
                   'text': f'El directorio {preferences.response[0].path_download} no existe'}
            msgbox.MsgBox.get_data(datos=dat)
        else:
            newpct1_completa.TorrentlocuraCompleta.get_data()

    @staticmethod
    def open_directory_data() -> NoReturn:
        if SYSTEM == 'Windows':
            comando = 'explorer "{}"'.format(DIRECTORY_WORKING.replace('/', '\\'))
        else:
            entorno_grafico = str()
            for command in ["dolphin", "caja", "nautilus"]:
                cmd = f"{command} -h"
                ejecucion = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                ejecucion.communicate()
                if ejecucion.returncode == 0:
                    entorno_grafico = command
                    break

            if entorno_grafico is not None:
                comando = f'{entorno_grafico} "{DIRECTORY_WORKING}"'  # no esta revisado
                logger.info(entorno_grafico)

        ejecucion = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ejecucion.communicate()  # no se lanza un hilo, hasta que no se cierre la ventana no sepuede seguir usando

    # PREFERENCIAS
    def menu_preferences(self) -> NoReturn:
        preferencias.Preferencias.get_data(database=self.database)

    def menu_notifications(self) -> NoReturn:
        notificaciones.Notificaciones.get_data(database=self.database)

    def menu_select_log(self, num: str) -> NoReturn:
        """
        creo una lista con los directorios/ficheros que quiero borrar
        """

        lista_log = list()

        with open(rf'{DIRECTORY_LOCAL}/id.conf', 'r') as f:
            id_fich = f.readline().replace('/n', '')

        consultas_log = Controller.get_credentials_fileconf(id_fich, self.db)

        if not consultas_log.is_empty():
            if num == 'newpct1':
                lista_log.append(f'{DIRECTORY_WORKING}/log/{consultas_log.response[0]["FicheroFeedNewpct"]}')
            elif num == 'showrss':
                lista_log.append(f'{DIRECTORY_WORKING}/log/{consultas_log.response[0]["FicheroFeedShowrss"]}')
            elif num == 'Descargas':
                lista_log.append(f'{DIRECTORY_WORKING}/log/{consultas_log.response[0]["FicheroDescargas"]}')
            elif num == 'Todos':
                lista_log.append(f'{DIRECTORY_WORKING}/log/{consultas_log.response[0]["FicheroFeedNewpct"]}')
                lista_log.append(f'{DIRECTORY_WORKING}/log/{consultas_log.response[0]["FicheroFeedShowrss"]}')
                lista_log.append(f'{DIRECTORY_WORKING}/log/{consultas_log.response[0]["FicheroDescargas"]}')

        # print self.listaLog
        self.menu_empty_log(lista_log)

    @staticmethod
    def menu_empty_log(list_log) -> NoReturn:
        """
        Borra los ficheros que estan la la lista (si existen)
        """

        for files in list_log:
            if os.path.exists(files):
                with open(files, 'w'):
                    pass

    @staticmethod
    def menu_initial_assistant() -> NoReturn:
        asistente_inicial.AsistenteInicial.get_data(ruta=DIRECTORY_WORKING)

    @staticmethod
    def menu_about() -> NoReturn:
        acerca_de.AcercaDe.get_data()


def main():
    # intentamos crear los ficheros de configuracion necesarios un maximo de 3 veces
    contador = 0
    while not asistente_inicial.AsistenteInicial.check_integrity_files():
        contador += 1
        logger.info(f"Intento {contador} de 3")
        if contador == 3:
            return

    funciones.create_directory_work()

    # global app  # sino lo pongo sale QObject::startTimer: QTimer can only be used with threads started with QThread
    app = QtWidgets.QApplication(sys.argv)

    myapp = Series()
    myapp.show()
    app.exec_()


if __name__ == "__main__":
    if len(sys.argv) != 1:
        descarga_automatica.main()
    else:
        main()
