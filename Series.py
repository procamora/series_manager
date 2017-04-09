#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SISTEMA
import sys
import os
import re
import platform
import functools
import subprocess
# TERCEROS
from PyQt5 import QtGui, QtWidgets, QtCore
# PROPIAS
from ui.series_ui import Ui_MainWindow
import asistente_inicial
import lista_activa
import listar_todas
import buscar_series
import actualizar_insertar
import preferencias
import notificaciones
import acerca_de
import estado_series
import msgbox
import descarga_automatica
import newpct1_completa
from modulos.connect_sqlite import conectionSQLite, ejecutaScriptSqlite
from modulos.settings import directorio_trabajo, sistema, nombre_db, directorio_local, modo_debug, ruta_db
import funciones


class Series(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.database = '{}/{}'.format(directorio_trabajo, nombre_db)

        self.otra = 'otra'  # campo otra del formulario
        self.estadoI = 'Ok'  # estado inicial
        self.estadoF = 'Cancelado'  # final
        self.estadoA = self.estadoI  # actual
        # CUIADO REVISAR ESTO Y UNIFICADO TODOS LOS NOMBRE DE LA DB
        self.db = self.database
        self.queryCompleta = str()  # lista de consultas que se ejecutaran al final

        self.setWindowTitle('Gestor de Series by Pablo')

        self.initListaActiva()  # Crea toda la vista del menu
        funciones.crearBackUpCompletoDB()
        self.menus()

    def initListaActiva(self):

        self.ui.gridLayoutGobal = QtWidgets.QGridLayout(self.ui.scrollAreaWidgetContents)

        query = """SELECT Nombre, Temporada, Capitulo, Dia, Capitulo_Descargado FROM Series 
                WHERE Siguiendo = "Si" AND Capitulo <> 0 AND Estado='Activa'"""
        series = conectionSQLite(self.db, query, True)

        # todo esto es para ordenar las series por fecha de proximidad de proximo capitulo
        fecha2 = funciones.calculaDiaSemana()
        fechaOrde = funciones.fechaToNumero(fecha2)

        listadoFinal = self.ordenaSeries(fechaOrde, series)

        for texto, i in zip(listadoFinal, list(range(0, len(listadoFinal)))):  # el encabezado lo tengo encima
            self.creaListaSerie(i, texto)
            if modo_debug:
                print(i, texto)

        self.ui.pushButtonAceptar.setVisible(False)
        self.ui.pushButtonAplicar.setText("Guardar")
        self.ui.pushButtonAplicar.clicked.connect(self.aplicaDatos)
        self.ui.pushButtonCerrar.clicked.connect(self.cancela)
        self.ui.pushButtonAceptar.clicked.connect(self.aceptaDatos)

    def creaListaSerie(self, n=0, datos=None):
        """
        Crea la linea de cada serie completa, generada por qtdesigner y pasado
        el codigo a python, despues visto como se crea y hecho algunas modificaciones

        param n int: se usa para dar formato estilo tabla, empieza en 0 y va hasta
        el numero de series que haya

        param datos dict: diccionario con todos los datos de la serie a la que se crea una linea
        """

        labelEmision = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.gridLayoutGobal.addWidget(labelEmision, n, 0, 1, 1, QtCore.Qt.AlignLeft)

        labelNombre = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.gridLayoutGobal.addWidget(labelNombre, n, 1, 1, 1, QtCore.Qt.AlignLeft)

        lineEpisodio = QtWidgets.QLineEdit(self.ui.scrollAreaWidgetContents)
        lineEpisodio.setEnabled(False)
        lineEpisodio.setMaximumSize(QtCore.QSize(50, 20))
        lineEpisodio.setReadOnly(True)
        self.ui.gridLayoutGobal.addWidget(lineEpisodio, n, 2, 1, 1, QtCore.Qt.AlignLeft)

        widgetBotones = QtWidgets.QWidget(self.ui.scrollAreaWidgetContents)
        widgetBotones.setMaximumSize(QtCore.QSize(90, 45))
        horizontalLayoutBotones = QtWidgets.QHBoxLayout(widgetBotones)
        buttonRestar = QtWidgets.QPushButton(widgetBotones)
        horizontalLayoutBotones.addWidget(buttonRestar)
        buttonSumar = QtWidgets.QPushButton(widgetBotones)
        horizontalLayoutBotones.addWidget(buttonSumar)
        self.ui.gridLayoutGobal.addWidget(widgetBotones, n, 3, 1, 1, QtCore.Qt.AlignLeft)

        labelEmision.setText(datos["Dia"])
        labelNombre.setText(datos["Nombre"])
        # hago esto para que quede bonito los numeros de los capitulos
        if len(str(datos["Capitulo"])) == 1:
            lineEpisodio.setText('{}x0{}'.format(datos["Temporada"], datos["Capitulo"]))
        else:
            lineEpisodio.setText('{}x{}'.format(datos["Temporada"], datos["Capitulo"]))
        buttonSumar.setText("+1")
        buttonRestar.setText("-1")

        # Conexion de los botones sumar y restar enviando la referencia del objeto para trabajar con ella posteriormente
        buttonSumar.clicked.connect(functools.partial(self.sumarSerie, lineEpisodio, datos))
        buttonRestar.clicked.connect(functools.partial(self.restarSerie, lineEpisodio, datos))

        # Widget para meter el QLineEdit y QPushButton
        widgetTeoricos = QtWidgets.QWidget(self.ui.scrollAreaWidgetContents)
        widgetTeoricos.setMaximumSize(QtCore.QSize(90, 45))
        horizontalLayoutTeoricos = QtWidgets.QHBoxLayout(widgetTeoricos)

        # Temporada y capitulo teorico
        lineEpisodioTeorico = QtWidgets.QLineEdit(self.ui.scrollAreaWidgetContents)
        lineEpisodioTeorico.setEnabled(False)
        lineEpisodioTeorico.setReadOnly(True)
        lineEpisodioTeorico.setMaximumSize(QtCore.QSize(30, 20))

        # Boton para actualizar el estado conforme al descargado automaticamente
        buttonTeorico = QtWidgets.QPushButton(widgetTeoricos)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        buttonTeorico.setIcon(icon)

        # Spacer para que se vea bonito cuando ocultamos el boton
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        # Incluimos todos al Widget
        horizontalLayoutTeoricos.addWidget(lineEpisodioTeorico)
        horizontalLayoutTeoricos.addWidget(buttonTeorico)
        horizontalLayoutTeoricos.addItem(spacerItem)
        self.ui.gridLayoutGobal.addWidget(widgetTeoricos, n, 4, 1, 1, QtCore.Qt.AlignLeft)

        # Si el capitulo es None o ya lo tengo actualizado no muestro el boton
        if datos["Capitulo_Descargado"] is not None and datos["Capitulo"] != datos["Capitulo_Descargado"]:
            lineEpisodioTeorico.setText(str(datos["Capitulo_Descargado"]))  # Asignamos el valor del capitulo
        else:
            lineEpisodioTeorico.setVisible(False)
            buttonTeorico.setVisible(False)

        buttonTeorico.clicked.connect(functools.partial(self.botonTeorico, lineEpisodioTeorico, lineEpisodio, datos))

    def botonTeorico(self, capituloT, capitulo, dat):
        """
        Calcula si el capitulo descargado es mayor o menor, despues el bucle se ejecuta la diferencia entre los capitulos ejecutando la funcion
        de sumar o restar capitulos
        """

        cap = int(capitulo.text().split('x')[-1])
        capT = int(capituloT.text())

        if capT > cap:
            for i in range(0, capT - cap):
                if modo_debug:
                    print('Suma: {}'.format(str(i)))
                self.sumarSerie(capitulo, dat)
        else:
            for i in range(0, capT - cap):
                if modo_debug:
                    print('Resta: {}'.format(str(i)))
                self.restarSerie(capitulo, dat)

    def sumarSerie(self, n, dat):
        """
        Tiene 2 funcionalidades:
            - 1: sumar un capitulo a numero de capitulo que se ve por pantalla de la serie
            - 2: crear una query para actualizar_insertar la bd y la mete en una lista para su posterior ejecucion

        param n object: objeto que hace referencia al campo donde sale temporada y capitulo que se modificara
        param dat dict: diccionario con todos los datos de la serie que me modificara
        """

        dat["Capitulo"] = dat["Capitulo"] + 1  # esto funciona porque hace referencia al objeto
        if len(str(dat["Capitulo"])) == 1:
            n.setText('{}x0{}'.format(dat["Temporada"], dat["Capitulo"]))
        else:
            n.setText('{}x{}'.format(dat["Temporada"], dat["Capitulo"]))

        query = """UPDATE series SET Capitulo=Capitulo+1 WHERE Nombre LIKE "{}";""".format(dat["Nombre"])
        self.queryCompleta += '\n' + query
        if modo_debug:
            print(query)

    def restarSerie(self, n, dat):
        """
        Tiene 2 funcionalidades,
            - 1: restar un capitulo a numero de capitulo que se ve por pantalla de la serie
            - 2: crear una query para actualizar_insertar la bd y la mete en una lista para su posterior ejecucion

        param n object: objeto que hace referencia al campo donde sale temporada y capitulo que se modificara
        param dat dict: diccionario con todos los datos de la serie que me modificara
        """

        dat["Capitulo"] = dat["Capitulo"] - 1  # esto funciona porque hace referencia al objeto
        if len(str(dat["Capitulo"])) == 1:
            n.setText('{}x0{}'.format(dat["Temporada"], dat["Capitulo"]))
        else:
            n.setText('{}x{}'.format(dat["Temporada"], dat["Capitulo"]))

        query = 'UPDATE series SET Capitulo=Capitulo-1 WHERE Nombre LIKE "{}";'.format(dat["Nombre"])
        self.queryCompleta += '\n' + query
        if modo_debug:
            print(query)

    def cancela(self):
        """
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        """

        self.estadoA = self.estadoF
        self.close()

    def aplicaDatos(self):
        """
        Recorre toda la lista de updates alctualizando todas las series,
        cuando termina vacia la lista por si volvemos a darle a aplicar,
        asi evitamos que se ejecute dos veces la misma lista
        """

        if modo_debug:
            print(self.queryCompleta)

        ejecutaScriptSqlite(self.db, self.queryCompleta)

        self.queryCompleta = str()  # por si vuelvo a darle al boton aplicar
        return True

    @staticmethod
    def ordenaSeries(semana, series):
        """
        creo una lista ordenada por dia de la semana
        """

        lista = list()
        # none es el valor por defecto de la bd cuando no hay dia
        semana.extend(['None'])

        for i in semana:
            for j in series:
                if j['Dia'] == i:
                    lista.append(j)
        if modo_debug:
            print(lista)
        return lista

    def aceptaDatos(self):
        """
        Boton Aceptar, primero aplicas los datos, si retorna True, cierra la ventana
        """

        if self.aplicaDatos():
            self.accept()

    def menus(self):
        # Crear menu nuevo completo
        """
        self.tools = self.menubar.addMenu('&Tools')
        prevMenu = self.tools.addMenu('Preview')
        prevMenu.addAction('Software', lambda: self.test('Hola'))
        """

        # SERIES
        self.ui.actionSeries_Activas.triggered.connect(self.menSeriesActivas)
        self.ui.actionSeries_Activas.setShortcut('Ctrl+A')
        self.ui.actionSeries_Activas.setStatusTip('Edicion rapida de series activas')
        self.ui.actionModificacion_masiva.triggered.connect(self.menListar)
        self.ui.actionModificacion_individual.triggered.connect(self.menActualizaSerie)
        self.ui.actionModificacion_individual.setShortcut('Ctrl+F')
        self.ui.actionInsertar_Serie.triggered.connect(self.menInsertar)
        self.ui.actionInsertar_Serie.setShortcut('Ctrl+I')
        self.ui.actionInsertar_Serie.setStatusTip('insertar una nueva serie')

        self.ui.actionRevisar_Estados.triggered.connect(self.RevisaEstadoSeries)
        self.ui.actionRevisar_Estados.setShortcut('Ctrl+E')
        self.ui.actionRevisar_Estados.setStatusTip('Revisar estados de series')

        self.ui.actionSalir.triggered.connect(self.close)
        self.ui.actionSalir.setShortcut('Ctrl+X')
        self.ui.actionSalir.setStatusTip('Cerrar el programa')

        # HERRAMIENTRAS
        self.ui.actionActualizar_bd_de_Imdb.triggered.connect(self.menActualizarImdb)
        self.ui.actionDescarga_Automatica.triggered.connect(self.menNewpct1)
        self.ui.actionDescarga_Automatica.setShortcut('Ctrl+N')
        self.ui.actionDescarga_Automatica.setStatusTip('Descargar series')
        self.ui.actionDescargar_Serie_Completa.triggered.connect(self.menCompletoNewpct1)
        self.ui.actionDescargar_Serie_Completa.setShortcut('Ctrl+M')
        self.ui.actionDescargar_Serie_Completa.setStatusTip('Descargar series por temporada')
        self.ui.actionAbrir_carpeta_de_datos.triggered.connect(self.abrirDirectorioDatos)
        self.ui.actionAbrir_carpeta_de_datos.setStatusTip('Abrir directorio de datos del programa')

        # OPCIONES
        self.ui.actionPreferencias.triggered.connect(self.menPreferencias)
        self.ui.actionPreferencias.setShortcut('Ctrl+P')
        self.ui.actionPreferencias.setStatusTip('Edicion de preferencias')

        self.ui.actionNotificaciones.triggered.connect(self.menNotificaciones)
        self.ui.actionNotificaciones.setShortcut('Ctrl+K')
        self.ui.actionNotificaciones.setStatusTip('Edicion de notificaciones')

        self.ui.actionLogNewpct1.triggered.connect(lambda: self.menSeleccionaLog('newpct1'))
        self.ui.actionLogNewpct1.setShortcut('Ctrl+1')
        self.ui.actionLogNewpct1.setStatusTip('Vaciar el log de newpct1')

        self.ui.actionLogShowrss.triggered.connect(lambda: self.menSeleccionaLog('showrss'))
        self.ui.actionLogShowrss.setShortcut('Ctrl+2')
        self.ui.actionLogShowrss.setStatusTip('Vaciar el log de showrss')

        self.ui.actionLogDescargas.triggered.connect(lambda: self.menSeleccionaLog('Descargas'))
        self.ui.actionLogDescargas.setShortcut('Ctrl+3')
        self.ui.actionLogDescargas.setStatusTip('Vaciar el log de Descargas')

        self.ui.actionLogTodos.triggered.connect(lambda: self.menSeleccionaLog('Todos'))
        self.ui.actionLogTodos.setShortcut('Ctrl+4')
        self.ui.actionLogTodos.setStatusTip('Vaciar todos los log')

        self.ui.actionAsistente_inicial.triggered.connect(self.menAsistenteInicial)
        self.ui.actionAsistente_inicial.setStatusTip('Edicion de preferencias')

        ################################################################################################################
        # revisar esto, hacer un for
        # self.ui.actionId_de_Opcion = self.ui.menuOpciones.addMenu('Id de Opcion')
        # self.ui.actionId_de_Opcion.addAction('Desplegable 1')
        # self.ui.actionId_de_Opcion.addAction('Desplegable 2')

        # A CERCA DE
        self.ui.actionAcerca_de.triggered.connect(self.menAcercaDe)
        self.ui.actionAcerca_de.setShortcut('Ctrl+H')
        self.ui.actionAcerca_de.setStatusTip('A cerca de')

    def menSeriesActivas(self):
        """
        Muestra todas las series activas con un boton de sumar o restar capitulos
        """

        lista_activa.ListaActiva.getDatos(dbSeries=self.database)

    def menListar(self):
        """
        Muestra las series para hacer modificaciones en masa
        """

        listar_todas.ListarTodas.getDatos(dbSeries=self.database)

    def menActualizaSerie(self):
        """
        Busca una serie especifica en la bd y te abre la ventana de modificacion de la serie
        """

        buscar_series.BuscarSeries.getDatos(dbSeries=self.database)

    def menInsertar(self):
        """
        Abre una ventana para meter una nueva serie en la bd
        """

        actualizar_insertar.ActualizarInsertar.getDatos(dbSeries=self.database)

    def RevisaEstadoSeries(self):
        """
        Revisa los estados de las series, si empiezan temporada, acaban temporadao acaban serie
        """

        estado_series.EstadoSeries.getDatos(dbSeries=self.database)

    @staticmethod
    def menActualizarImdb():
        import modulos.actualiza_imdb
        a = modulos.actualiza_imdb.actualizaImdb()
        print('actulizaCompleto')
        a.actulizaCompleto()

    def menNewpct1(self):
        Conf = funciones.dbConfiguarion()
        rutaDesc = str(Conf['RutaDescargas'])  # es unicode

        if not os.path.exists(rutaDesc):
            dat = {'title': 'No existe el directorio', 'text': 'El directorio {} no existe'.format(rutaDesc)}
            msgbox.MsgBox.getData(datos=dat)
        else:
            descarga_automatica.DescargaAutomatica.getDatos(dbSeries=self.database)

    @staticmethod
    def menCompletoNewpct1():
        Conf = funciones.dbConfiguarion()
        rutaDesc = str(Conf['RutaDescargas'])  # es unicode

        if not os.path.exists(rutaDesc):
            dat = {'title': 'No existe el directorio', 'text': 'El directorio {} no existe'.format(rutaDesc)}
            msgbox.MsgBox.getData(datos=dat)
        else:
            newpct1_completa.Newpct1Completa.getDatos()

    @staticmethod
    def abrirDirectorioDatos():
        if sistema == 'Windows':
            comando = 'explorer "{}"'.format(directorio_trabajo.replace('/', '\\'))
        else:
            entornoGrafico = str()
            for i in ["dolphin", "caja", "nautilus"]:
                cmd = "{} -h".format(i)
                ejecucion = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                ejecucion.communicate()
                if ejecucion.returncode == 0:
                    entornoGrafico = i
                    break

            if entornoGrafico is not None:
                comando = '{} "{}"'.format(entornoGrafico, directorio_trabajo)  # no esta revisado
                print(entornoGrafico)

        ejecucion = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ejecucion.communicate()  # no se lanza un hilo, hasta que no se cierre la ventana no sepuede seguir usando

    # PREFERENCIAS
    def menPreferencias(self):
        preferencias.Preferencias.getDatos(dbSeries=self.database)

    def menNotificaciones(self):
        notificaciones.Notificaciones.getDatos(dbSeries=self.database)

    def menSeleccionaLog(self, num):
        """
        creo una lista con los directorios/ficheros que quiero borrar
        """

        listaLog = list()

        with open(r'{}/id.conf'.format(directorio_local), 'r') as f:
            id_fich = f.readline().replace('/n', '')

        query = 'SELECT * FROM Configuraciones, Credenciales WHERE ID LIKE {} LIMIT 1'.format(id_fich)
        consultasLog = conectionSQLite(self.database, query, True)

        if len(consultasLog) > 0:
            if num == 'newpct1':
                listaLog.append('{}/log/{}'.format(directorio_trabajo, consultasLog[0]['FicheroFeedNewpct']))
            elif num == 'showrss':
                listaLog.append('{}/log/{}'.format(directorio_trabajo, consultasLog[0]['FicheroFeedShowrss']))
            elif num == 'Descargas':
                listaLog.append('{}/log/{}'.format(directorio_trabajo, consultasLog[0]['FicheroDescargas']))
            elif num == 'Todos':
                listaLog.append('{}/log/{}'.format(directorio_trabajo, consultasLog[0]['FicheroFeedNewpct']))
                listaLog.append('{}/log/{}'.format(directorio_trabajo, consultasLog[0]['FicheroFeedShowrss']))
                listaLog.append('{}/log/{}'.format(directorio_trabajo, consultasLog[0]['FicheroDescargas']))

        # print self.listaLog
        self.menVaciaLog(listaLog)

    @staticmethod
    def menVaciaLog(listaLog):
        """
        Borra los ficheros que estan la la lista (si existen)
        """

        for files in listaLog:
            if os.path.exists(files):
                with open(files, 'w'):
                    pass

    @staticmethod
    def menAsistenteInicial():
        asistente_inicial.AsistenteInicial.getDatos(ruta=directorio_trabajo)

    @staticmethod
    def menAcercaDe():
        acerca_de.AcercaDe.getDatos()


def main():
    # intentamos crear los ficheros de configuracion necesarios un maximo de 3 veces
    contador = 0
    while not asistente_inicial.AsistenteInicial.checkIntegridadFicheros():
        contador += 1
        print("Intento {} de 3".format(contador))
        if contador == 3:
            return

    funciones.creaDirectorioTrabajo()

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
