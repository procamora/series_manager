# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/series.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(645, 533)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/Principal.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.label_4 = QtWidgets.QLabel(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setMaximumSize(QtCore.QSize(50, 50))
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.splitter)
        self.label_5.setMaximumSize(QtCore.QSize(50, 50))
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.splitter, 0, 6, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(50, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 2, 1, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setWordWrap(False)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 4, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(50, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 0, 3, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(25, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem2, 0, 5, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem3, 0, 7, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 0, 8, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem4, 0, 9, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 629, 402))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 1, 0, 1, 1)
        self.WidgetBotones = QtWidgets.QWidget(self.centralwidget)
        self.WidgetBotones.setObjectName("WidgetBotones")
        self.LayoutBotones = QtWidgets.QHBoxLayout(self.WidgetBotones)
        self.LayoutBotones.setContentsMargins(0, 0, 0, 0)
        self.LayoutBotones.setObjectName("LayoutBotones")
        self.label_Info = QtWidgets.QLabel(self.WidgetBotones)
        self.label_Info.setText("")
        self.label_Info.setObjectName("label_Info")
        self.LayoutBotones.addWidget(self.label_Info)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.LayoutBotones.addItem(spacerItem5)
        self.pushButtonAplicar = QtWidgets.QPushButton(self.WidgetBotones)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/accept_button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonAplicar.setIcon(icon1)
        self.pushButtonAplicar.setObjectName("pushButtonAplicar")
        self.LayoutBotones.addWidget(self.pushButtonAplicar)
        self.pushButtonCerrar = QtWidgets.QPushButton(self.WidgetBotones)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonCerrar.setIcon(icon2)
        self.pushButtonCerrar.setObjectName("pushButtonCerrar")
        self.LayoutBotones.addWidget(self.pushButtonCerrar)
        self.pushButtonAceptar = QtWidgets.QPushButton(self.WidgetBotones)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/Iconos/Icons/fatcow/file_save_as.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonAceptar.setIcon(icon3)
        self.pushButtonAceptar.setObjectName("pushButtonAceptar")
        self.LayoutBotones.addWidget(self.pushButtonAceptar)
        self.gridLayout.addWidget(self.WidgetBotones, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 645, 27))
        self.menubar.setObjectName("menubar")
        self.menuOpciones = QtWidgets.QMenu(self.menubar)
        self.menuOpciones.setObjectName("menuOpciones")
        self.menuVaciar_log = QtWidgets.QMenu(self.menuOpciones)
        self.menuVaciar_log.setObjectName("menuVaciar_log")
        self.menuAyuda = QtWidgets.QMenu(self.menubar)
        self.menuAyuda.setObjectName("menuAyuda")
        self.menuSeries = QtWidgets.QMenu(self.menubar)
        self.menuSeries.setObjectName("menuSeries")
        self.menuModificar_Series = QtWidgets.QMenu(self.menuSeries)
        self.menuModificar_Series.setObjectName("menuModificar_Series")
        self.menuHerramientas = QtWidgets.QMenu(self.menubar)
        self.menuHerramientas.setObjectName("menuHerramientas")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionInsertar = QtWidgets.QAction(MainWindow)
        self.actionInsertar.setObjectName("actionInsertar")
        self.actionTodasA = QtWidgets.QAction(MainWindow)
        self.actionTodasA.setObjectName("actionTodasA")
        self.actionSiguiendoA = QtWidgets.QAction(MainWindow)
        self.actionSiguiendoA.setObjectName("actionSiguiendoA")
        self.actionEn_EsperaA = QtWidgets.QAction(MainWindow)
        self.actionEn_EsperaA.setObjectName("actionEn_EsperaA")
        self.actionAcerca_de = QtWidgets.QAction(MainWindow)
        self.actionAcerca_de.setObjectName("actionAcerca_de")
        self.actionSeries_Activas = QtWidgets.QAction(MainWindow)
        self.actionSeries_Activas.setObjectName("actionSeries_Activas")
        self.actionTodasL = QtWidgets.QAction(MainWindow)
        self.actionTodasL.setObjectName("actionTodasL")
        self.actionSiguiendoL = QtWidgets.QAction(MainWindow)
        self.actionSiguiendoL.setObjectName("actionSiguiendoL")
        self.actionActivasL = QtWidgets.QAction(MainWindow)
        self.actionActivasL.setObjectName("actionActivasL")
        self.actionPreferencias = QtWidgets.QAction(MainWindow)
        self.actionPreferencias.setObjectName("actionPreferencias")
        self.actionInsertar_Serie = QtWidgets.QAction(MainWindow)
        self.actionInsertar_Serie.setObjectName("actionInsertar_Serie")
        self.actionModificacion_masiva = QtWidgets.QAction(MainWindow)
        self.actionModificacion_masiva.setObjectName("actionModificacion_masiva")
        self.actionModificacion_individual = QtWidgets.QAction(MainWindow)
        self.actionModificacion_individual.setObjectName("actionModificacion_individual")
        self.actionEn_Proceos = QtWidgets.QAction(MainWindow)
        self.actionEn_Proceos.setObjectName("actionEn_Proceos")
        self.actionActualizar_bd_de_Imdb = QtWidgets.QAction(MainWindow)
        self.actionActualizar_bd_de_Imdb.setObjectName("actionActualizar_bd_de_Imdb")
        self.actionNewpct1 = QtWidgets.QAction(MainWindow)
        self.actionNewpct1.setObjectName("actionNewpct1")
        self.actionShowRss = QtWidgets.QAction(MainWindow)
        self.actionShowRss.setObjectName("actionShowRss")
        self.actionActualizar_Serie = QtWidgets.QAction(MainWindow)
        self.actionActualizar_Serie.setObjectName("actionActualizar_Serie")
        self.actionId_de_Opcion = QtWidgets.QAction(MainWindow)
        self.actionId_de_Opcion.setObjectName("actionId_de_Opcion")
        self.actionRevisar_Estados = QtWidgets.QAction(MainWindow)
        self.actionRevisar_Estados.setObjectName("actionRevisar_Estados")
        self.actionSalir = QtWidgets.QAction(MainWindow)
        self.actionSalir.setObjectName("actionSalir")
        self.actionNotificaciones = QtWidgets.QAction(MainWindow)
        self.actionNotificaciones.setObjectName("actionNotificaciones")
        self.actionLogNewpct1 = QtWidgets.QAction(MainWindow)
        self.actionLogNewpct1.setObjectName("actionLogNewpct1")
        self.actionLogShowrss = QtWidgets.QAction(MainWindow)
        self.actionLogShowrss.setObjectName("actionLogShowrss")
        self.actionLogDescargas = QtWidgets.QAction(MainWindow)
        self.actionLogDescargas.setObjectName("actionLogDescargas")
        self.actionLogTodos = QtWidgets.QAction(MainWindow)
        self.actionLogTodos.setObjectName("actionLogTodos")
        self.actionDescargar_Serie_Completa = QtWidgets.QAction(MainWindow)
        self.actionDescargar_Serie_Completa.setObjectName("actionDescargar_Serie_Completa")
        self.actionExportar_backup_de_la_bd = QtWidgets.QAction(MainWindow)
        self.actionExportar_backup_de_la_bd.setObjectName("actionExportar_backup_de_la_bd")
        self.actionImportar_backup_de_la_bd = QtWidgets.QAction(MainWindow)
        self.actionImportar_backup_de_la_bd.setObjectName("actionImportar_backup_de_la_bd")
        self.actionAbrir_carpeta_de_datos = QtWidgets.QAction(MainWindow)
        self.actionAbrir_carpeta_de_datos.setObjectName("actionAbrir_carpeta_de_datos")
        self.actionDescarga_Automatica = QtWidgets.QAction(MainWindow)
        self.actionDescarga_Automatica.setObjectName("actionDescarga_Automatica")
        self.actionAsistente_inicial = QtWidgets.QAction(MainWindow)
        self.actionAsistente_inicial.setObjectName("actionAsistente_inicial")
        self.menuVaciar_log.addAction(self.actionLogNewpct1)
        self.menuVaciar_log.addAction(self.actionLogShowrss)
        self.menuVaciar_log.addAction(self.actionLogDescargas)
        self.menuVaciar_log.addSeparator()
        self.menuVaciar_log.addAction(self.actionLogTodos)
        self.menuOpciones.addAction(self.actionPreferencias)
        self.menuOpciones.addAction(self.actionNotificaciones)
        self.menuOpciones.addAction(self.menuVaciar_log.menuAction())
        self.menuOpciones.addAction(self.actionAsistente_inicial)
        self.menuAyuda.addAction(self.actionAcerca_de)
        self.menuModificar_Series.addAction(self.actionModificacion_masiva)
        self.menuModificar_Series.addAction(self.actionModificacion_individual)
        self.menuSeries.addAction(self.actionSeries_Activas)
        self.menuSeries.addAction(self.menuModificar_Series.menuAction())
        self.menuSeries.addAction(self.actionInsertar_Serie)
        self.menuSeries.addAction(self.actionRevisar_Estados)
        self.menuSeries.addSeparator()
        self.menuSeries.addAction(self.actionSalir)
        self.menuHerramientas.addAction(self.actionActualizar_bd_de_Imdb)
        self.menuHerramientas.addAction(self.actionDescarga_Automatica)
        self.menuHerramientas.addAction(self.actionDescargar_Serie_Completa)
        self.menuHerramientas.addAction(self.actionExportar_backup_de_la_bd)
        self.menuHerramientas.addAction(self.actionImportar_backup_de_la_bd)
        self.menuHerramientas.addAction(self.actionAbrir_carpeta_de_datos)
        self.menubar.addAction(self.menuSeries.menuAction())
        self.menubar.addAction(self.menuHerramientas.menuAction())
        self.menubar.addAction(self.menuOpciones.menuAction())
        self.menubar.addAction(self.menuAyuda.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_4.setText(_translate("MainWindow", "Disminuir"))
        self.label_5.setText(_translate("MainWindow", "Aumentar"))
        self.label_2.setText(_translate("MainWindow", "Nombre"))
        self.label.setText(_translate("MainWindow", "  Emision"))
        self.label_3.setText(_translate("MainWindow", "Capitulo"))
        self.label_6.setText(_translate("MainWindow", "Descargado"))
        self.pushButtonAplicar.setText(_translate("MainWindow", "Aplicar"))
        self.pushButtonCerrar.setText(_translate("MainWindow", "Cerrar"))
        self.pushButtonAceptar.setText(_translate("MainWindow", "Aceptar"))
        self.menuOpciones.setTitle(_translate("MainWindow", "&Opciones"))
        self.menuVaciar_log.setTitle(_translate("MainWindow", "Vaciar log"))
        self.menuAyuda.setTitle(_translate("MainWindow", "&Ayuda"))
        self.menuSeries.setTitle(_translate("MainWindow", "&Series"))
        self.menuModificar_Series.setTitle(_translate("MainWindow", "Modificar Series"))
        self.menuHerramientas.setTitle(_translate("MainWindow", "Herramientas"))
        self.actionInsertar.setText(_translate("MainWindow", "Insertar"))
        self.actionTodasA.setText(_translate("MainWindow", "Todas"))
        self.actionSiguiendoA.setText(_translate("MainWindow", "Siguiendo"))
        self.actionEn_EsperaA.setText(_translate("MainWindow", "En Espera"))
        self.actionAcerca_de.setText(_translate("MainWindow", "Acerca de"))
        self.actionSeries_Activas.setText(_translate("MainWindow", "Series Activas"))
        self.actionTodasL.setText(_translate("MainWindow", "Todas"))
        self.actionSiguiendoL.setText(_translate("MainWindow", "Siguiendo"))
        self.actionActivasL.setText(_translate("MainWindow", "Activas"))
        self.actionPreferencias.setText(_translate("MainWindow", "Preferencias"))
        self.actionInsertar_Serie.setText(_translate("MainWindow", "Insertar Serie"))
        self.actionModificacion_masiva.setText(_translate("MainWindow", "Modificacion masiva"))
        self.actionModificacion_individual.setText(_translate("MainWindow", "Modificacion individual"))
        self.actionEn_Proceos.setText(_translate("MainWindow", "En Proceso"))
        self.actionActualizar_bd_de_Imdb.setText(_translate("MainWindow", "Actualizar bd de Imdb"))
        self.actionNewpct1.setText(_translate("MainWindow", "Newpct1"))
        self.actionShowRss.setText(_translate("MainWindow", "ShowRss"))
        self.actionActualizar_Serie.setText(_translate("MainWindow", "Actualizar Serie"))
        self.actionId_de_Opcion.setText(_translate("MainWindow", "Id de Opcion"))
        self.actionRevisar_Estados.setText(_translate("MainWindow", "Revisar Estados"))
        self.actionSalir.setText(_translate("MainWindow", "Salir"))
        self.actionNotificaciones.setText(_translate("MainWindow", "Notificaciones"))
        self.actionLogNewpct1.setText(_translate("MainWindow", "Newpct1"))
        self.actionLogShowrss.setText(_translate("MainWindow", "Showrss"))
        self.actionLogDescargas.setText(_translate("MainWindow", "Descargas"))
        self.actionLogTodos.setText(_translate("MainWindow", "Todos"))
        self.actionDescargar_Serie_Completa.setText(_translate("MainWindow", "Descargar Serie Completa"))
        self.actionExportar_backup_de_la_bd.setText(_translate("MainWindow", "Exportar backup de la bd"))
        self.actionImportar_backup_de_la_bd.setText(_translate("MainWindow", "Importar backup de la bd"))
        self.actionAbrir_carpeta_de_datos.setText(_translate("MainWindow", "Abrir carpeta de datos"))
        self.actionDescarga_Automatica.setText(_translate("MainWindow", "Descarga Automatica"))
        self.actionAsistente_inicial.setText(_translate("MainWindow", "Asistente inicial"))

import app.views.ui.fatcow_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

