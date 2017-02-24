
try:  # Ejecucion desde Series.py
    from .settings import modo_debug, ruta_db, nombre_db, directorio_trabajo, directorio_local
    from .connect_sqlite import conectionSQLite, ejecutaScriptSqlite
except:  # Ejecucion local
    from settings import modo_debug, ruta_db, nombre_db, directorio_trabajo, directorio_local
    from connect_sqlite import conectionSQLite, ejecutaScriptSqlite


def datosIniciales():
    with open(r'{}/id.conf'.format(directorio_local), 'r') as f:
        id_fich = f.readline().replace('/n', '')

    query = 'SELECT * FROM Configuraciones, Credenciales WHERE ID LIKE {} LIMIT 1'.format(
        id_fich)
    return conectionSQLite(ruta_db, query, True)[0]

datos = datosIniciales()
print(datos['api_telegram'])
