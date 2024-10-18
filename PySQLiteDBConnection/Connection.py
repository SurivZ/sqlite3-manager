from sqlite3 import connect, Cursor, Connection
from typing import List, Tuple, Dict, Any as any


class Connect:
    """
    Clase para manejar la conexión y operaciones CRUD en una base de datos SQLite3.

    Args:
        path (str): Ruta al archivo de la base de datos SQLite3.
        raise_exceptions (bool): Este parámetro le permite al usuario decidir si quiere que la clase levante o no las excepciones. Predeterminado False.
        __connection (Connection): Conexión a la base de datos.
        __cursor (Cursor): Cursor para ejecutar consultas SQL.
        __connection_status (bool): Variable que muestra el estado de la conexión con la base de datos.
    """
    path: str
    raise_exceptions: bool
    __connection: Connection
    __cursor: Cursor
    __connection_status: bool = False

    def __init__(self, path: str, raise_exceptions: bool = False) -> None:
        """_Método constructor de la clase. Inicializa una nueva instancia de la clase Connect._

        Args:
            path (str): _Ruta al archivo de la base de datos SQLite3._
            raise_exceptions (bool, opcional): _Este parámetro le permite al usuario decidir si quiere que la clase levante o no las excepciones._ Predeterminado False.
        """
        self.path = path
        self.raise_exceptions = raise_exceptions

    def __str__(self) -> str:
        """_Método especial. Devuelve información relacionada con la conexión a la base de datos._

        Returns:
            str: _Devuelve una cadena con la ruta a la base de datos y el estado de la conexión._
        """
        return f"Base de datos: {self.path}\nEstado: {('Sin conexión', 'Conexión establecida')[self.get_status()]}"

    def get_status(self) -> bool:
        """_Método que devuelve el estado de la conexión a la base de datos._
        
        Returns:
            bool: _**True** si está conectado a una base de datos, **False** si no lo está._
        """
        return self.__connection_status

    def connect(self) -> bool:
        """_Método que establece una conexión con la base de datos SQLite3._

        Returns:
            bool: **True** si la conexión es exitosa, **False** de lo contrario.
        """
        try:
            if self.get_status():
                print("[!] Ya estás conectado a una base de datos")
                return False
            
            self.__connection = connect(self.path)
            self.__cursor = self.__connection.cursor()
            self.__connection_status = True
            
            print("[i] Conexión exitosa")
            return True
        except Exception as e:
            if not self.raise_exceptions:
                print(f"[!] Error al conectar: {e}")
                return False
            raise e

    def list_table_names(self) -> list[str] | None:
        """_Método que devuelve un listado con todas las tablas de la base de datos._

        Returns:
            list[str]: _Listado con los nombres de las tablas de la base de datos._
        """
        try:
            if not self.get_status():
                print("[!] Debes conectarte primero a una base de datos.")
                return
            
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            
            self.__cursor.execute(query)
            tables = self.__cursor.fetchall()
            
            if not tables:
                print("[i] No se encontraron tablas en la base de datos.")
                return []
            
            return [str(table[0]) for table in tables]
        except Exception as e:
            if not self.raise_exceptions:
                print(f"[!] Error al listar las tablas: {e}")
                return
            raise e
        
    def get_columns(self, table_name: str) -> list[str] | None:
        """_Método que devuelve un listado con todas las columnas de una tabla._

        Args:
            table_name (str): _Parámetro que representa el nombre de la tabla de la que se quiere listar las columnas._

        Returns:
            list[str]: _Listado con los nombres de las columnas de la tabla._
        """
        try:
            if not self.get_status():
                print("[!] Debes conectarte primero a una base de datos.")
                return
            
            query = f"PRAGMA table_info({table_name});"
            
            self.__cursor.execute(query)
            columns = self.__cursor.fetchall()
            
            if not columns:
                print("[i] No se encontraron columnas en la tabla.")
                return []
        
            return [str(column[1]) for column in columns]
        except Exception as e:
            if not self.raise_exceptions:
                print(f"[!] Error al listar las columnas de la tabla '{table_name}': {e}")
                return
            raise e

    def read_table(self, table_name: str) -> List[Tuple[int | float | str, ...]] | None:
        """_Método que lee todos los registros de una tabla en particular._

        Args:
            table_name (str): _Parámetro que representa el nombre de la tabla a leer._

        Returns:
            List[Tuple]: _Lista de tuplas que representan los registros de la tabla. Cada tupla es un registro de la tabla._
        """
        try:
            if not self.get_status():
                print("[!] Debes conectarte primero a una base de datos.")
                return
            
            query = f"SELECT * FROM {table_name}"
            
            self.__cursor.execute(query)
            rows = self.__cursor.fetchall()
            
            if not rows:
                print("[i] No se encontraron registros en la tabla.")
                return []
            
            return rows
        except Exception as e:
            if not self.raise_exceptions:
                print(f"[!] Error al leer la tabla '{table_name}': {e}")
                return 
            raise e

    def search(self, table_name: str, condition: Dict[str, any]) -> List[Tuple[int | float | str, ...]] | None:
        """_Método que lee registros de una tabla que cumplen una condición específica._

        Args:
            table_name (str): _Parámetro que representa el nombre de la tabla a leer._
            condition (dict): _Parámetro que representa las condiciones de búsqueda por medio de un diccionario en donde las claves son el nombre de la columna y el valor es el valor en dicha columna._

        Returns:
            List[Tuple]: _Lista de tuplas que representan los registros que cumplen la condición. Cada tupla es un registro de la tabla que coincide con los parámetros de búsqueda._
        """
        try:
            if not self.get_status():
                print("[!] Debes conectarte primero a una base de datos.")
                return
            
            conditions = ' AND '.join([f"{column} = ?" for column in condition.keys()])
            query = f"SELECT * FROM {table_name} WHERE {conditions}"
            
            self.__cursor.execute(query, tuple(condition.values()))
            rows = self.__cursor.fetchall()
            
            if not rows:
                print("[i] No se encontraron registros en la tabla que coincidan con los parámetros de búsqueda.")
                return []
            
            return rows
        except Exception as e:
            if not self.raise_exceptions:
                print(f"[!] Error al buscar en la tabla '{table_name}': {e}")
                return 
            raise e

    def insert(self, table_name: str, data: Dict[str, any]) -> bool | None:
        """_Método para insertar datos en una tabla._

        Args:
            table_name (str): _Parámetro que representa el nombre de la tabla donde se insertarán los datos._
            data (dict): _Parámetro que representa la información que será insertada en la base de datos, siendo las claves del diccionario las columnas de la tabla y los valores del diccionario los valores de dichas columnas._

        Returns:
            bool: Devuelve **True** si la operación es exitosa, **False** de lo contrario.
        """
        try:
            if not self.get_status():
                print("[!] Debes conectarte primero a una base de datos")
                return
            
            columns = ', '.join(data.keys())
            values = ', '.join(['?' for _ in range(len(data))])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            
            self.__cursor.execute(query, tuple(data.values()))
            self.__connection.commit()
            
            if not self.search(table_name, data):
                raise Exception
            
            print("[i] Datos insertados exitosamente")
            return True
        except Exception as e:
            if self.raise_exceptions:
                print(f"[!] Error al insertar datos a la tabla '{table_name}': e")
                return False
            raise e

    def update(self, table_name: str, data: Dict[str, any], condition: Dict[str, any]) -> bool | None:
        """_Método para actualizar registros en una tabla._

        Args:
            table_name (str): _Parámetro que representa el nombre de la tabla en la que se realizará la actualización._
            data (dict): _Parámetro que representa los la nueva información que se colocará en los registros que cumplan con los parámetros de búsqueda. Viene en formato diccionario donde las claves representan las columnas y los valores los valores de dichas columnas._
            condition (dict): _Parámetro que representa las condiciones para la actualización de los registros en forma de diccionario, siendo las claves las columnas y sus valores los valores de dichas columnas._

        Returns:
            bool: Devuelve **True** si la operación es exitosa, **False** de lo contrario.
        """
        try:
            if not self.get_status():
                print("[!] Debes conectarte primero a una base de datos")
                return
            
            set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
            where_clause = ' AND '.join([f"{key} = ?" for key in condition.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            values = tuple(data.values()) + tuple(condition.values())
            
            self.__cursor.execute(query, values)
            self.__connection.commit()
            
            if not self.search(table_name, data):
                raise Exception
            
            print("[i] Datos actualizados exitosamente")
            return True
        except Exception as e:
            if not self.raise_exceptions:
                print(f"[!] Error al actualizar datos de la tabla '{table_name}': e")
                return False
            raise e

    def delete(self, table_name: str, condition: Dict[str, any]) -> bool | None:
        """_Método que elimina registros de una tabla._

        Args:
            table_name (str): _Parámetro que representa el nombre de la tabla de la cual eliminar los registros._
            condition (dict): _Parámetro que representa las condiciones para eliminar registros en forma de diccionario, siendo las claves del diccionario las columnas y siendo los valores del diccionario los valores de las respectivas columnas._

        Returns:
            bool: Devuelve **True** si la operación es exitosa, **False** de lo contrario.
        """
        try:
            if not self.get_status():
                print("[!] Debes conectarte primero a una base de datos")
                return
            
            query = f"DELETE FROM {table_name} WHERE "
            conditions = [f"{field} = {value}" for field, value in condition.items()]
            query += " AND ".join(conditions)
            
            self.__cursor.execute(query)
            self.__connection.commit()
            
            if self.search(table_name, condition):
                raise Exception
            
            print("[i] Datos eliminados exitosamente")
            return True
        except Exception as e:
            if not self.raise_exceptions:
                print(f"[!] Error al eliminar datos de la tabla '{table_name}': {e}")
                return False
            raise e

    def create_table(self, table_name: str, columns: dict, apply_constraints: bool = False) -> bool:
        """_Método que crea una nueva tabla en la base de datos._

        Args:
            table_name (str): _Parámetro que representa el nombre de la tabla a crear._
            columns (dict): _Parámetro que  (por ejemplo, 'INTEGER', 'TEXT').
            apply_constraints (bool, opcional): Booleano que indica si se deben aplicar restricciones de tipos de datos en las columnas.

        Returns:
            bool: Devuelve **True** si la tabla se crea exitosamente, **False** de lo contrario.
        """
        try:
            column_defs = []
            for column_name, data_type in columns.items():
                if apply_constraints:
                    _data_type = data_type.split(" ")[0]
                    if _data_type.upper() == "INTEGER":
                        constraint = f"CHECK({column_name} IS NULL OR {column_name} GLOB '[0-9]*')"
                    elif _data_type.upper() == "REAL":
                        constraint = f"CHECK({column_name} IS NULL OR {column_name} LIKE '%[0-9]%')"
                    elif _data_type.upper() == "NUMERIC":
                        constraint = f"CHECK({column_name} IS NULL OR {column_name} GLOB '[0-9]*')"
                    column_defs.append(f"{column_name} {data_type} {constraint}".strip())
                else:
                    column_defs.append(f"{column_name} {data_type}")
            columns_sql = ", ".join(column_defs)
            sql = f"CREATE TABLE {table_name} ({columns_sql})"
            self.__cursor.execute(sql)
            print(f'[i] Tabla "{table_name}" creada exitosamente')
            return True
        except Exception as e:
            if self.raise_exceptions:
                raise e
            else:
                print(f'[!] Error al crear la tabla "{table_name}": ', e)
                return False

    def add_column(self, table_name: str, column_name: str, column_type: str) -> bool:
        """
        Agrega una nueva columna a una tabla existente.

        Args:
            - table_name: Nombre de la tabla a modificar.
            - column_name: Nombre de la nueva columna.
            - column_type: Tipo de dato de la nueva columna (por ejemplo, 'INTEGER', 'TEXT').

        Returns:
            - True si la columna se agrega exitosamente, False de lo contrario.
        """
        try:
            query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            self.__cursor.execute(query)
            self.__connection.commit()
            print(f'[i] Columna "{column_name}" añadida exitosamente a la tabla "{table_name}"')
            return True
        except Exception as e:
            if self.raise_exceptions:
                raise e
            else:
                print(f'[!] Error al agregar la columna "{column_name}": ', e)
                return False

    def drop_table(self, table_name: str) -> bool:
        """
        Elimina una tabla de la base de datos.

        Args:
            - table_name: Nombre de la tabla a eliminar.

        Returns:
            - True si la tabla se elimina exitosamente, False de lo contrario.
        """
        try:
            query = f"DROP TABLE IF EXISTS {table_name}"
            self.__cursor.execute(query)
            self.__connection.commit()
            print(f'[i] Tabla "{table_name}" eliminada exitosamente')
            return True
        except Exception as e:
            if self.raise_exceptions:
                raise e
            else:
                print(f'[!] Error al eliminar la tabla "{table_name}": ', e)
                return False
            
    def custom_query(self, query: str) -> List[Tuple[int | float | str, ...]]:
        """
        Ejecuta una consulta personalizada definida por el usuario

        Args:
            - query: La consulta SQL a realizar

        Returns:
            - Lista de tuplas que representan lo que la base de datos devuelve.
        """
        try:
            self.__cursor.execute(query)
            results = self.__cursor.fetchall()
            return results
        except Exception as e:
            if self.raise_exceptions:
                raise e
            else:
                print(f'[!] Error al ejecutar la consulta "{query}": ', e)
                return []

    def close(self) -> None:
        """
        Cierra la conexión con la base de datos.
        """
        if hasattr(self, '_Connect__cursor') and self.__cursor:
            self.__cursor.close()
        if hasattr(self, '_Connect__connection') and self.__connection:
            self.__connection.close()
        self.__connection_status = False
