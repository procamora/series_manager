#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#SISTEMA
import sys
import os
import re
import platform
import functools
#TERCEROS
from PyQt5 import QtGui, QtWidgets,  QtCore
#PROPIAS
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


class MiFormulario(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        try:
            self.database = '{}/{}'.format(funciones.creaDirectorioTrabajo(), nombre_db)
        except:
            self.database = ruta_db

        self.setWindowTitle('Gestor de Series by Pablo')

        self.__init_listaActiva()		# Crea toda la vista del menu
        funciones.crearBackUpCompletoDB()
        self.Menus()


    def __init_listaActiva(self):
        self.Otra = 'Otra'  # campo otra del formulario
        self.EstadoI = 'Ok' # estado inicial
        self.EstadoF = 'Cancelado' #final
        self.EstadoA = self.EstadoI  # actual
        # CUIADO REVISAR ESTO Y UNIFICADO TODOS LOS NOMBRE DE LA DB
        self.db = self.database

        self.QueryCompleta = str()   # lista de consultas que se ejecutaran al final

        self.ui.gridLayoutGobal = QtWidgets.QGridLayout(self.ui.scrollAreaWidgetContents)

        query = '''SELECT Nombre, Temporada, Capitulo, Dia, Capitulo_Descargado FROM Series WHERE Siguiendo = "Si" AND Capitulo <> 0 AND Estado="Activa"'''
        series =  conectionSQLite(self.db, query, True)

        # todo esto es para ordenar las series por fecha de proximidad de proximo capitulo
        self.fecha2 = funciones.calculaDiaSemana()
        self.fechaOrde = funciones.fechaToNumero(self.fecha2)

        self.listadoFinal = self.__ordenaSeries(self.fechaOrde, series)
        text = self.listadoFinal

        for texto, i in zip(text, list(range(0, len(text)))):# el encabezado lo tengo encima
            self.__creaListaSerie(i, texto)
            if modo_debug:
                print((i, texto))

        self.ui.pushButtonAceptar.setVisible(False)
        self.ui.pushButtonAplicar.setText("Guardar")
        self.ui.pushButtonAplicar.clicked.connect(self.__aplicaDatos)
        self.ui.pushButtonCerrar.clicked.connect(self.__cancela)
        self.ui.pushButtonAceptar.clicked.connect(self.__aceptaDatos)


    def __creaListaSerie(self, n=0, datos=None):
        '''
        Crea la linea de cada serie completa, generada por qtdesigner y pasado
        el codigo a python, despues visto como se crea y hecho algunas modificaciones

        param n int: se usa para dar formato estilo tabla, empieza en 0 y va hasta
        el numero de series que haya

        param datos dict: diccionario con todos los datos de la serie a la que se crea una linea
        '''

        self.datos = datos
        self.labelEmision = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.gridLayoutGobal.addWidget(self.labelEmision, n, 0, 1, 1, QtCore.Qt.AlignLeft)

        self.labelNombre = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.gridLayoutGobal.addWidget(self.labelNombre, n, 1, 1, 1, QtCore.Qt.AlignLeft)

        self.lineEpisodio = QtWidgets.QLineEdit(self.ui.scrollAreaWidgetContents)
        self.lineEpisodio.setEnabled(False)
        self.lineEpisodio.setMaximumSize(QtCore.QSize(50, 20))
        self.lineEpisodio.setReadOnly(True)
        self.ui.gridLayoutGobal.addWidget(self.lineEpisodio, n, 2, 1, 1, QtCore.Qt.AlignLeft)

        self.widgetBotones = QtWidgets.QWidget(self.ui.scrollAreaWidgetContents)
        self.widgetBotones.setMaximumSize(QtCore.QSize(90, 45))
        self.horizontalLayoutBotones = QtWidgets.QHBoxLayout(self.widgetBotones)
        self.ButtonRestar = QtWidgets.QPushButton(self.widgetBotones)
        self.horizontalLayoutBotones.addWidget(self.ButtonRestar)
        self.ButtonSumar = QtWidgets.QPushButton(self.widgetBotones)
        self.horizontalLayoutBotones.addWidget(self.ButtonSumar)
        self.ui.gridLayoutGobal.addWidget(self.widgetBotones, n, 3, 1, 1, QtCore.Qt.AlignLeft)

        self.labelEmision.setText(self.datos["Dia"])
        self.labelNombre.setText(self.datos["Nombre"])
        # hago esto para que quede bonito los numeros de los capitulos
        if len(str(self.datos["Capitulo"])) == 1:
            self.lineEpisodio.setText('{}x0{}'.format(self.datos["Temporada"], self.datos["Capitulo"]))
        else:
            self.lineEpisodio.setText('{}x{}'.format(self.datos["Temporada"], self.datos["Capitulo"]))
        self.ButtonSumar.setText("+1")
        self.ButtonRestar.setText("-1")

        #Conexion de los botones sumar y restar enviando la referencia del objeto para trabajar con ella posteriormente
        self.ButtonSumar.clicked.connect(functools.partial(self.__sumarSerie, self.lineEpisodio, self.datos))
        self.ButtonRestar.clicked.connect(functools.partial(self.__restarSerie, self.lineEpisodio, self.datos))

        #Widget para meter el QLineEdit y QPushButton
        self.widgetTeoricos = QtWidgets.QWidget(self.ui.scrollAreaWidgetContents)
        self.widgetTeoricos.setMaximumSize(QtCore.QSize(90, 45))
        self.horizontalLayoutTeoricos = QtWidgets.QHBoxLayout(self.widgetTeoricos)

        #Temporada y capitulo teorico
        self.lineEpisodioTeorico = QtWidgets.QLineEdit(self.ui.scrollAreaWidgetContents)
        self.lineEpisodioTeorico.setEnabled(False)
        self.lineEpisodioTeorico.setReadOnly(True)
        self.lineEpisodioTeorico.setMaximumSize(QtCore.QSize(30, 20))

        #Boton para actualizar el estado conforme al descargado automaticamente
        self.ButtonTeorico = QtWidgets.QPushButton(self.widgetTeoricos)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap((":/Iconos/Icons/fatcow/add.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ButtonTeorico.setIcon(icon)

        #Spacer para que se vea bonito cuando ocultamos el boton
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        #Incluimos todos al Widget
        self.horizontalLayoutTeoricos.addWidget(self.lineEpisodioTeorico)
        self.horizontalLayoutTeoricos.addWidget(self.ButtonTeorico)
        self.horizontalLayoutTeoricos.addItem(spacerItem)
        self.ui.gridLayoutGobal.addWidget(self.widgetTeoricos, n, 4, 1, 1, QtCore.Qt.AlignLeft)

        #Si el capitulo es None o ya lo tengo actualizado no muestro el boton
        if self.datos["Capitulo_Descargado"] is not None and self.datos["Capitulo"] != self.datos["Capitulo_Descargado"]:
            self.lineEpisodioTeorico.setText(str(self.datos["Capitulo_Descargado"]))		#Asignamos el valor del capitulo
        else:
            self.lineEpisodioTeorico.setVisible(False)
            self.ButtonTeorico.setVisible(False)

        self.ButtonTeorico.clicked.connect(functools.partial(self.__botonTeorico, self.lineEpisodioTeorico, self.lineEpisodio, self.datos))


    def __botonTeorico(self, capituloT, capitulo, dat):
        '''
        Calcula si el capitulo descargado es mayor o menor, despues el bucle se ejecuta la diferencia entre los capitulos ejecutando la funcion
        de sumar o restar capitulos
        '''

        cap = int(capitulo.text().split('x')[-1])
        capT = int(capituloT.text())

        if capT > cap:
            for i in range(0, capT-cap):
                if modo_debug:
                    print('Suma: {}'.format(str(i)))
                self.__sumarSerie(capitulo, dat)
        else:
            for i in range(0, capT-cap):
                if modo_debug:
                    print('Resta: {}'.format(str(i)))
                self.__restarSerie(capitulo, dat)


    def __sumarSerie(self, n, dat):
        '''
        Tiene 2 funcionalidades:
            - 1: sumar un capitulo a numero de capitulo que se ve por pantalla de la serie
            - 2: crear una query para actualizar_insertar la bd y la mete en una lista para su posterior ejecucion

        param n object: objeto que hace referencia al campo donde sale temporada y capitulo que se modificara
        param dat dict: diccionario con todos los datos de la serie que me modificara
        '''

        dat["Capitulo"] = dat["Capitulo"]+1  # esto funciona porque hace referencia al objeto
        if len(str(dat["Capitulo"])) == 1:
            n.setText('{}x0{}'.format(dat["Temporada"], dat["Capitulo"]))
        else:
            n.setText('{}x{}'.format(dat["Temporada"], dat["Capitulo"]))

        query = '''UPDATE series SET Capitulo=Capitulo+1 WHERE Nombre LIKE "{}";'''.format(dat["Nombre"])
        self.QueryCompleta += '\n'+query
        if modo_debug:
            print(query)


    def __restarSerie(self, n, dat):
        '''
        Tiene 2 funcionalidades,
            - 1: restar un capitulo a numero de capitulo que se ve por pantalla de la serie
            - 2: crear una query para actualizar_insertar la bd y la mete en una lista para su posterior ejecucion

        param n object: objeto que hace referencia al campo donde sale temporada y capitulo que se modificara
        param dat dict: diccionario con todos los datos de la serie que me modificara
        '''

        dat["Capitulo"] = dat["Capitulo"]-1  # esto funciona porque hace referencia al objeto
        if len(str(dat["Capitulo"])) == 1:
            n.setText('{}x0{}'.format(dat["Temporada"], dat["Capitulo"]))
        else:
            n.setText('{}x{}'.format(dat["Temporada"], dat["Capitulo"]))

        query = 'UPDATE series SET Capitulo=Capitulo-1 WHERE Nombre LIKE "{}";'.format(dat["Nombre"])
        self.QueryCompleta += '\n'+query
        if modo_debug:
            print(query)


    def __cancela(self):
        '''
        Establece el estado actual en cancelado para retornar None y ejecuta reject
        '''

        self.EstadoA = self.EstadoF
        self.close()


    def __aplicaDatos(self):
        '''
        Recorre toda la lista de updates alctualizando todas las series,
        cuando termina vacia la lista por si volvemos a darle a aplicar,
        asi evitamos que se ejecute dos veces la misma lista
        '''

        if modo_debug:
            print((self.QueryCompleta))

        ejecutaScriptSqlite(self.db, self.QueryCompleta)

        self.QueryCompleta = str()  # por si vuelvo a darle al boton aplicar
        return True


    def __ordenaSeries(self, semana, series):
        '''
        creo una lista ordenada por dia de la semana
        '''

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


    def __aceptaDatos(self):
        """
        Boton Aceptar, primero aplicas los datos, si retorna True, cierra la ventana
        """

        if self.__aplicaDatos():
            self.accept()


    def Menus(self):
        #Crear menu nuevo completo
        '''
        self.tools = self.menubar.addMenu('&Tools')
        prevMenu = self.tools.addMenu('Preview')
        prevMenu.addAction('Software', lambda: self.test('Hola'))
        '''

        #SERIES
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

        #HERRAMIENTRAS
        self.ui.actionActualizar_bd_de_Imdb.triggered.connect(self.menActualizarImdb)
        self.ui.actionDescarga_Automatica.triggered.connect(self.menNewpct1)
        self.ui.actionDescarga_Automatica.setShortcut('Ctrl+N')
        self.ui.actionDescarga_Automatica.setStatusTip('Descargar series')
        self.ui.actionDescargar_Serie_Completa.triggered.connect(self.menCompletoNewpct1)
        self.ui.actionDescargar_Serie_Completa.setShortcut('Ctrl+M')
        self.ui.actionDescargar_Serie_Completa.setStatusTip('Descargar series por temporada')
        self.ui.actionAbrir_carpeta_de_datos.triggered.connect(self.abrirDirectorioDatos)
        self.ui.actionAbrir_carpeta_de_datos.setStatusTip('Abrir directorio de datos del programa')

        #OPCIONES
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

        ################################################################################################################################
        # revisar esto, hacer un for
        #self.ui.actionId_de_Opcion = self.ui.menuOpciones.addMenu('Id de Opcion')
        #self.ui.actionId_de_Opcion.addAction('Desplegable 1')
        #self.ui.actionId_de_Opcion.addAction('Desplegable 2')

        #A CERCA DE
        self.ui.actionAcerca_de.triggered.connect(self.menAcercaDe)
        self.ui.actionAcerca_de.setShortcut('Ctrl+H')
        self.ui.actionAcerca_de.setStatusTip('A cerca de')


    def menSeriesActivas(self):
        '''
        Muestra todas las series activas con un boton de sumar o restar capitulos
        '''

        lista_activa.MiFormulario.getDatos(dbSeries=self.database)


    def menListar(self):
        '''
        Muestra las series para hacer modificaciones en masa
        '''

        listar_todas.MiFormulario.getDatos(dbSeries=self.database)


    def menActualizaSerie(self):
        '''
        Busca una serie especifica en la bd y te abre la ventana de modificacion de la serie
        '''

        buscar_series.MiFormulario.getDatos(dbSeries=self.database)


    def menInsertar(self):
        '''
        Abre una ventana para meter una nueva serie en la bd
        '''

        actualizar_insertar.MiFormulario.getDatos(dbSeries=self.database)


    def RevisaEstadoSeries(self):
        '''
        Revisa los estados de las series, si empiezan temporada, acaban temporadao acaban serie
        '''

        estado_series.MiFormulario.getDatos(dbSeries=self.database)


    def menActualizarImdb(self):
        import modulos.actualiza_imdb
        a = modulos.actualiza_imdb.actualizaImdb()
        print('actulizaCompleto')
        a.actulizaCompleto()


    def menNewpct1(self):
        Conf = funciones.dbConfiguarion()
        rutaDesc = str(Conf['RutaDescargas'])   # es unicode

        if not os.path.exists(rutaDesc):
            dat = {'title':'No existe el directorio', 'text':'El directorio {} no existe'.format(rutaDesc)}
            msgbox.MiFormulario.getData(datos=dat)
        else:
            descarga_automatica.MiFormulario.getDatos(dbSeries=self.database)

    def menCompletoNewpct1(self):
        Conf = funciones.dbConfiguarion()
        rutaDesc = str(Conf['RutaDescargas'])   # es unicode

        if not os.path.exists(rutaDesc):
            dat = {'title':'No existe el directorio', 'text':'El directorio {} no existe'.format(rutaDesc)}
            msgbox.MiFormulario.getData(datos=dat)
        else:
            newpct1_completa.MiFormulario.getDatos()

    def abrirDirectorioDatos(self):
        if sistema == 'win32':
            comando = 'explorer "{}"'.format(funciones.creaDirectorioTrabajo().replace('/', '\\'))
        else:
            if re.search('fedora', platform.platform()):
                comando = 'dolphin "{}"'.format(funciones.creaDirectorioTrabajo()) # no esta revisado
            else:
                comando = 'nautilus "{}"'.format(funciones.creaDirectorioTrabajo()) # no esta revisado

        os.system(comando)


    # PREFERENCIAS
    def menPreferencias(self):
        preferencias.MiFormulario.getDatos(dbSeries=self.database)


    def menNotificaciones(self):
        notificaciones.MiFormulario.getDatos(dbSeries=self.database)


    def menSeleccionaLog(self, num):
        '''
        creo una lista con los directorios/ficheros que quiero borrar
        '''

        self.listaLog = list()

        with open(r'{}/id.conf'.format(directorio_local), 'r') as f:
            id_fich = f.readline().replace('/n', '')

        query = 'SELECT * FROM Configuraciones, Credenciales WHERE ID LIKE {} LIMIT 1'.format(id_fich)
        ser = conectionSQLite(self.database, query, True)[0]

        if num == 'newpct1':
            self.listaLog.append('{}/log/{}'.format(directorio_trabajo, ser['FicheroFeedNewpct']))
        elif num == 'showrss':
            self.listaLog.append('{}/log/{}'.format(directorio_trabajo, ser['FicheroFeedShowrss']))
        elif num == 'Descargas':
            self.listaLog.append('{}/log/{}'.format(directorio_trabajo, ser['FicheroDescargas']))
        elif num == 'Todos':
            self.listaLog.append('{}/log/{}'.format(directorio_trabajo, ser['FicheroFeedNewpct']))
            self.listaLog.append('{}/log/{}'.format(directorio_trabajo, ser['FicheroFeedShowrss']))
            self.listaLog.append('{}/log/{}'.format(directorio_trabajo, ser['FicheroDescargas']))

        #print self.listaLog
        self.menVaciaLog()


    def menVaciaLog(self):
        '''
        Borra los ficheros que estan la la lista
        '''

        for i in self.listaLog:
            with open(i, 'w'):
                pass


    def menAsistenteInicial(self):
        asistente_inicial.MiFormulario.getDatos(ruta=directorio_trabajo)


    def menAcercaDe(self):
        acerca_de.MiFormulario.getDatos()


def main():
    global app   # sino lo pongo sale    QObject::startTimer: QTimer can only be used with threads started with QThread
    app = QtWidgets.QApplication(sys.argv)

    myapp = MiFormulario()
    myapp.show()
    app.exec_()


if __name__ == "__main__":
    if len(sys.argv) != 1:
        descarga_automatica.main()
    else:
        main()
        #funciones.creaDirectorioTrabajo()
        #print('fin')
