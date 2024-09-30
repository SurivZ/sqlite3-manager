from sqlite3 import connect, Cursor, Connection
from typing import List, Tuple, Dict, Any as any


class Connect:
    """
    Clase para manejar la conexión y operaciones CRUD en una base de datos SQLite3.

    Args:
        path (str): Ruta al archivo de la base de datos SQLite3.
        raise_exceptions (bool): Este parámetro le permite al usuario decidir si quiere que la clase levante o no las excepciones.
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
        """
        Inicializa una nueva instancia de la clase Connect.

        Args:
            - path: Ruta al archivo de la base de datos SQLite3.
            - raise_exceptions: Este parámetro le permite al usuario decidir si quiere que la clase levante o no las excepciones.
        """
        self.path = path
        self.raise_exceptions = raise_exceptions

    def __str__(self) -> str:
        """
        Método que devuelve información relacionada con la conexión a la base de datos.
        """
        return f"Base de datos: {self.path}\nEstado: {('Sin conexión', 'Conexión establecida')[self.__connection_status]}"

    def get_status(self) -> bool:
        """
        Método que devuelve el estado de la conexión a la base de datos.
        """
        return self.__connection_status

    def connect(self) -> bool:
        """
        Establece una conexión con la base de datos SQLite3.

        Returns:
            - True si la conexión es exitosa, False de lo contrario.
        """
        try:
            self.__connection = connect(self.path)
            self.__cursor = self.__connection.cursor()
            self.__connection_status = True
            print('[¡] Conexión exitosa')
            return True
        except Exception as e:
            if self.raise_exceptions:
                raise e
            else:
                print('[!] Error al conectar: ', e)
                return False

    def read_table(self, table_name: str) -> List[Tuple[int | float | str, ...]]:
        """
        Lee todos los registros de una tabla en particular.

        Args:
            - table_name: Nombre de la tabla a leer.

        Returns:
            - Lista de tuplas que representan los registros de la tabla.
        """
        try:
            query = f"SELECT * FROM {table_name}"
            self.__cursor.execute(query)
            rows = self.__cursor.fetchall()
            return rows
        except Exception as e:
            if self.raise_exceptions:
                raise e
            else:
                print('[!] Error al leer la tabla: ', e)
                return []

    def read_table_with_condition(self, table_name: str, condition: Dict[str, any]) -> List[Tuple[int | float | str, ...]]:
        """
        Lee registros de una tabla que cumplen una condición específica.

        Args:
            - table_name: Nombre de la tabla a leer.
            - condition: Diccionario con las condiciones de búsqueda.

        Returns:
            - Lista de tuplas que representan los registros que cumplen la condición.
        """
        try:
            condition_columns = ' AND '.join([f"{column} = ?" for column in condition.keys()])
            query = f"SELECT * FROM {table_name} WHERE {condition_columns}"
            self.__cursor.execute(query, tuple(condition.values()))
            rows = self.__cursor.fetchall()
            return rows
        except Exception as e:
            if self.raise_exceptions:
                raise e
            else:
                print('[!] Error al leer la tabla con la condición: ', e)
                return []

    def insert_into_table(self, table_name: str, data: Dict[str, any]) -> bool:
        """
        Inserta datos en una tabla.

        Args:
            - table_name: Nombre de la tabla donde se insertarán los datos.
            - data: Diccionario con los datos a insertar.

        Returns:
            - True si la operación es exitosa, False de lo contrario.
        """
        try:
            columns = ', '.join(data.keys())
            values = ', '.join(['?' for _ in range(len(data))])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            self.__cursor.execute(query, tuple(data.values()))
            self.__connection.commit()
            print('[¡] Datos insertados exitosamente')
            return True
        except Exception as e:
            if self.raise_exceptions:
                raise e
            else:
                print('[!] Error al insertar datos: ', e)
                return False

    def update_record(self, table_name: str, data: Dict[str, any], condition: Dict[str, any]) -> bool:
        """
        Actualiza registros en una tabla.

        Args:
            - table_name: Nombre de la tabla a actualizar.
            - data: Diccionario con los datos actualizados.
            - condition: Diccionario con la condición para filtrar los registros a actualizar.

        Returns:
            - True si la operación es exitosa, False de lo contrario.
        """
        try:
            set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
            where_clause = ' AND '.join([f"{key} = ?" for key in condition.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            values = tuple(data.values()) + tuple(condition.values())
            self.__cursor.execute(query, values)
            self.__connection.commit()
            print('[¡] Datos actualizados exitosamente')
            return True
        except Exception as e:
            if self.raise_exceptions:
                raise e
            else:
                print('[!] Error al actualizar datos: ', e)
                return False

    def delete_record(self, table_name: str, condition: Dict[str, any]) -> bool:
        """
        Elimina registros de una tabla.

        Args:
            - table_name: Nombre de la tabla de la cual eliminar los registros.
            - condition: Diccionario con el campo y valor a buscar para filtrar los registros a eliminar.

        Returns:
            - True si la operación es exitosa, False de lo contrario.
        """
        try:
            query = f"DELETE FROM {table_name} WHERE "
            conditions = [f"{field} = {value}" for field, value in condition.items()]
            query += " AND ".join(conditions)
            self.__cursor.execute(query)
            self.__connection.commit()
            print('[¡] Datos eliminados exitosamente')
            return True
        except Exception as e:
            if self.raise_exceptions:
                raise e
            else:
                print('[!] Error al eliminar datos: ', e)
                return False

    def create_table(self, table_name: str, columns: dict, apply_constraints: bool = False) -> bool:
        """
        Crea una nueva tabla en la base de datos.

        Args:
            - table_name: Nombre de la tabla a crear.
            - columns: Diccionario donde las claves son los nombres de las columnas y los valores representa información sobre las columnas, como sus tipos de datos (por ejemplo, 'INTEGER', 'TEXT').
            - apply_constraints: Booleano que indica si se deben aplicar restricciones de tipos de datos en las columnas.

        Returns:
            - True si la tabla se crea exitosamente, False de lo contrario.
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
            print(f'[¡] Tabla "{table_name}" creada exitosamente')
            return True
        except Exception as e:
            if self.raise_exceptions:
                raise e
            else:
                print(f'[!] Error al crear la tabla "{table_name}": ', e)
                return False

    def alter_table_add_column(self, table_name: str, column_name: str, column_type: str) -> bool:
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
            print(f'[¡] Columna "{column_name}" añadida exitosamente a la tabla "{table_name}"')
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
            print(f'[¡] Tabla "{table_name}" eliminada exitosamente')
            return True
        except Exception as e:
            if self.raise_exceptions:
                raise e
            else:
                print(f'[!] Error al eliminar la tabla "{table_name}": ', e)
                return False
            
    def execute_custom_query(self, query: str) -> List[Tuple[int | float | str, ...]]:
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
