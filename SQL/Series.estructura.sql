BEGIN TRANSACTION;
CREATE TABLE "Series" (
	`ID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`Nombre`	TEXT NOT NULL UNIQUE,
	`Temporada`	INTEGER DEFAULT 1,
	`Capitulo`	INTEGER DEFAULT 1,
	`Siguiendo`	TEXT DEFAULT 'Si',
	`VOSE`	TEXT DEFAULT 'No',
	`Acabada`	TEXT DEFAULT 'No',
	`Dia`	TEXT DEFAULT 'None',
	`Estado`	TEXT DEFAULT 'Activa',
	`imdb_id`	TEXT UNIQUE,
	`imdb_Temporada`	TEXT,
	`imdb_Capitulos`	TEXT,
	`imdb_Finaliza`	TEXT,
	`imdb_seguir`	INTEGER DEFAULT 'Si',
	`Capitulo_Descargado`	INTEGER
);
CREATE TABLE "Notificaciones" (
	`ID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`Nombre`	TEXT UNIQUE,
	`API`	TEXT,
	`Activo`	INTEGER DEFAULT 0
);
INSERT INTO `Notificaciones` VALUES (1,'Telegram','','False');
INSERT INTO `Notificaciones` VALUES (2,'Pushbullet','','False');
INSERT INTO `Notificaciones` VALUES (3,'Email','','False');
INSERT INTO `Notificaciones` VALUES (4,'Hangouts','','False');
CREATE TABLE "Id_Url" (
	`Id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`Url`	TEXT UNIQUE,
	`Descripcion`	TEXT
);
CREATE TABLE `ID_Estados` (
	`ID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`Estados`	TEXT UNIQUE
);
CREATE TABLE "Genero" (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`genero`	INTEGER,
	FOREIGN KEY(`id`) REFERENCES ID_Estados(ID)
);
CREATE TABLE "Credenciales" (
	`pass_transmission`	TEXT,
	`user_tviso`	TEXT,
	`pass_tviso`	TEXT,
	`api_telegram`	TEXT
);
CREATE TABLE "Configuraciones" (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`BaseDeDatos`	TEXT DEFAULT 'Series.db',
	`UrlFeedNewpct`	TEXT,
	`UrlFeedShowrss`	TEXT,
	`RutaDescargas`	TEXT,
	`FicheroFeedNewpct`	TEXT DEFAULT 'feedNewpct.log',
	`FicheroFeedShowrss`	TEXT DEFAULT 'feedShowrss.log',
	`FicheroDescargas`	INTEGER DEFAULT 'descargas.log'
);
COMMIT;
