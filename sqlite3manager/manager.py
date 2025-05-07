from sqlite3 import connect, Cursor, Connection
from typing import Any as any, Callable, TypeVar, cast
from threading import local

FuncType = TypeVar('FuncType', bound=Callable)


def handle_exception(function: FuncType) -> FuncType:
    """
    Decorador para manejar excepciones de los métodos de la clase Connect.

    Args:
        function (FuncType): La función a la que se aplica el decorador.

    Returns:
        FuncType: La función decorada.
    """
    def wrapper(self: 'Connect', *args, **kwargs) -> any:
        try:
            return function(self, *args, **kwargs)
        except Exception as e:
            if self.raise_exceptions:
                raise e
            print(f"[!] Error en {function.__name__}: {e}")
            return None
    return cast(FuncType, wrapper)


def require_connection(function: FuncType) -> FuncType:
    """
    Decorador que verifica si hay una conexión establecida a la base de datos antes de ejecutar el método.

    Args:
        function (FuncType): La función a la que se aplica el decorador.

    Returns:
        FuncType: La función decorada.
    """
    def wrapper(self: 'Connect', *args, **kwargs) -> any:
        if not self.get_status():
            print("[!] Debes conectarte primero a una base de datos.")
            return None
        return function(self, *args, **kwargs)
    return cast(FuncType, wrapper)


class Connect:
    """
    Clase para manejar conexiones y operaciones CRUD en una base de datos SQLite.
    
    Args:
        path (str): Ruta de la base de datos SQLite.
        raise_exceptions (bool): Indica si se deben levantar excepciones en caso de error. Por defecto es False.
    """
    path: str
    raise_exceptions: bool
    _local: local

    def __init__(self, path: str, raise_exceptions: bool = False) -> None:
        """
        Inicializa una instancia de la clase Connect.

        Args:
            path (str): Ruta de la base de datos.
            raise_exceptions (bool): Indica si se deben levantar excepciones en caso de error. Por defecto es False.
        """
        self._local = local()
        self.path = path
        self.raise_exceptions = raise_exceptions

    def __str__(self) -> str:
        """
        Retorna una representación en cadena de la conexión actual.

        Returns:
            str: Información de la base de datos y su estado de conexión.
        
        Example:
            >>> conn = Connect('mi_db.sqlite')
            >>> print(conn)
            Base de datos: mi_db.sqlite
            Estado: Sin conexión
        """
        return f"Base de datos: {self.path}\nEstado: {('Sin conexión', 'Conexión establecida')[self.get_status()]}"
    
    def _get_connection(self) -> Connection:
        """
        Obtiene la conexión a la base de datos. Si no existe, la crea.
        
        Returns:
            Connection: Conexión a la base de datos.    
            
        Example:
            >>> conn = Connect('mi_db.sqlite')
            >>> connection = conn._get_connection()
            >>> print(connection)
            <sqlite3.Connection object at 0x...>
        """
        if not hasattr(self._local, 'connection') or not self._local.connection:
            self._local.connection = connect(self.path)
            self._local.connection_status = True
        return self._local.connection
    
    def _get_cursor(self) -> Cursor:
        """
        Obtiene el cursor de la conexión a la base de datos. Si no existe, lo crea.
        
        Returns:
            Cursor: Cursor de la conexión a la base de datos.
            
        Example:
            >>> conn = Connect('mi_db.sqlite')
            >>> cursor = conn._get_cursor()
            >>> print(cursor)
            <sqlite3.Cursor object at 0x...>
        """
        if not hasattr(self._local, 'cursor') or not self._local.cursor:
            self._local.cursor = self._get_connection().cursor()
        return self._local.cursor

    def get_status(self) -> bool:
        """
        Verifica el estado de la conexión.

        Returns:
            bool: True si hay una conexión establecida, False de lo contrario.

        Example:
            >>> conn.get_status()
            False
        """
        return getattr(self._local, 'connection_status', False)

    @handle_exception
    def connect(self) -> bool:
        """
        Establece una conexión a la base de datos.

        Returns:
            bool: True si la conexión fue exitosa, False si ya había una conexión.

        Example:
            >>> conn.connect()
            [i] Conexión exitosa
            True
        """
        if self.get_status():
            print("[!] Ya estás conectado a una base de datos")
            return False

        self._local.connection = connect(
            self.path,
            check_same_thread=False,
            timeout=10.0,
            isolation_level=None,
        )
        self._local.cursor = self._local.connection.cursor()
        self._local.connection_status = True
        
        print("[i] Conexión exitosa")
        return True

    @require_connection
    @handle_exception
    def list_table_names(self) -> list[str]:
        """
        Lista los nombres de todas las tablas en la base de datos.

        Returns:
            list[str]: Lista de nombres de tablas.

        Example:
            >>> conn.list_table_names()
            ['users', 'products']
        """
        cursor = self._get_cursor()
        
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        cursor.execute(query)
        tables = cursor.fetchall()

        if not tables:
            print("[i] No se encontraron tablas en la base de datos.")
            return []

        return [str(table[0]) for table in tables]

    @require_connection
    @handle_exception
    def get_column_names(self, table_name: str) -> list[str]:
        """
        Obtiene los nombres de las columnas de una tabla específica.

        Args:
            table_name (str): El nombre de la tabla.

        Returns:
            list[str]: Lista de nombres de columnas.

        Example:
            >>> conn.get_column_names('users')
            ['id', 'name', 'email']
        """
        cursor = self._get_cursor()
        
        query = f"PRAGMA table_info({table_name});"
        cursor.execute(query)
        columns = cursor.fetchall()

        if not columns:
            print("[i] No se encontraron columnas en la tabla.")
            return []

        return [str(column[1]) for column in columns]

    @require_connection
    @handle_exception
    def read_table(self, table_name: str) -> list[tuple[int | float | str, ...]]:
        """
        Lee todos los registros de una tabla.

        Args:
            table_name (str): El nombre de la tabla.

        Returns:
            list[tuple]: Lista de filas de la tabla.

        Example:
            >>> conn.read_table('users')
            [(1, 'John', 'john@example.com'), (2, 'Jane', 'jane@example.com')]
        """
        cursor = self._get_cursor()
        
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            print("[i] No se encontraron registros en la tabla.")
            return []

        return rows

    @require_connection
    @handle_exception
    def search(self, table_name: str, condition: dict[str, any]) -> list[tuple[int | float | str, ...]]:
        """
        Busca registros en una tabla que coincidan con una condición.

        Args:
            table_name (str): El nombre de la tabla.
            condition (dict): Condiciones de búsqueda.

        Returns:
            list[tuple]: Lista de registros que cumplen con la condición.

        Example:
            >>> conn.search('users', {'name': 'John'})
            [(1, 'John', 'john@example.com')]
        """
        cursor = self._get_cursor()
        
        conditions = ' AND '.join([f"{column} = ?" for column in condition.keys()])
        query = f"SELECT * FROM {table_name} WHERE {conditions}"

        cursor.execute(query, tuple(condition.values()))
        rows = cursor.fetchall()

        if not rows:
            print("[i] No se encontraron registros en la tabla que coincidan con los parámetros de búsqueda.")
            return []

        return rows

    @require_connection
    @handle_exception
    def insert(self, table_name: str, data: dict[str, any]) -> bool:
        """
        Inserta un registro en una tabla.

        Args:
            table_name (str): El nombre de la tabla.
            data (dict): Diccionario con los datos a insertar.

        Returns:
            bool: True si la inserción fue exitosa.

        Example:
            >>> conn.insert('users', {'name': 'John', 'email': 'john@example.com'})
            [i] Datos insertados exitosamente
            True
        """
        if not data:
            raise ValueError("No hay datos para insertar")
        
        connection = self._get_connection()
        cursor = self._get_cursor()
        
        columns = ', '.join(data.keys())
        values = ', '.join(['?' for _ in range(len(data))])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

        cursor.execute(query, tuple(data.values()))
        connection.commit()

        print("[i] Datos insertados exitosamente")
        return True

    @require_connection
    @handle_exception
    def bulk_insert(self, table_name: str, data_list: list[dict[str, any]]) -> bool:
        """
        Inserta múltiples registros en una tabla.

        Args:
            table_name (str): El nombre de la tabla.
            data_list (list[dict]): Lista de diccionarios con los datos a insertar.

        Returns:
            bool: True si la inserción fue exitosa.

        Example:
            >>> conn.bulk_insert('users', [{'name': 'John', 'email': 'john@example.com'}, {'name': 'Jane', 'email': 'jane@example.com'}])
            [i] Registros insertados exitosamente
            True
        """
        if not data_list:
            raise ValueError("No hay datos para insertar")
        
        connection = self._get_connection()
        cursor = self._get_cursor()

        columns = ', '.join(data_list[0].keys())
        values = ', '.join(['?' for _ in data_list[0].keys()])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

        values_list = [tuple(data.values()) for data in data_list]

        cursor.executemany(query, values_list)
        connection.commit()

        print("[i] Registros insertados exitosamente")
        return True

    @require_connection
    @handle_exception
    def update(self, table_name: str, data: dict[str, any], condition: dict[str, any]) -> bool:
        """
        Actualiza registros en una tabla que coincidan con una condición.

        Args:
            table_name (str): El nombre de la tabla.
            data (dict): Diccionario con los datos a actualizar.
            condition (dict): Condición para seleccionar los registros a actualizar.

        Returns:
            bool: True si la actualización fue exitosa.

        Example:
            >>> conn.update('users', {'email': 'new_email@example.com'}, {'name': 'John'})
            [i] Datos actualizados exitosamente
            True
        """
        connection = self._get_connection()
        cursor = self._get_cursor()
        
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        where_clause = ' AND '.join([f"{key} = ?" for key in condition.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        values = tuple(data.values()) + tuple(condition.values())

        cursor.execute(query, values)
        connection.commit()

        print("[i] Datos actualizados exitosamente")
        return True

    @require_connection
    @handle_exception
    def delete(self, table_name: str, condition: dict[str, any]) -> bool:
        """
        Elimina registros en una tabla que coincidan con una condición.

        Args:
            table_name (str): El nombre de la tabla.
            condition (dict): Condición para seleccionar los registros a eliminar.

        Returns:
            bool: True si la eliminación fue exitosa.

        Example:
            >>> conn.delete('users', {'name': 'John'})
            [i] Datos eliminados exitosamente
            True
        """
        connection = self._get_connection()
        cursor = self._get_cursor()
        
        query = f"DELETE FROM {table_name} WHERE " + " AND ".join([f"{field} = ?" for field in condition.keys()])

        cursor.execute(query, tuple(condition.values()))
        connection.commit()

        print("[i] Datos eliminados exitosamente")
        return True

    @require_connection
    @handle_exception
    def create_table(self, table_name: str, columns: dict[str, any], apply_constraints: bool = False) -> bool:
        """
        Crea una nueva tabla en la base de datos.

        Args:
            table_name (str): El nombre de la tabla.
            columns (dict): Diccionario con el nombre de las columnas y sus tipos.
            apply_constraints (bool): Indica si se deben aplicar restricciones de tipo de datos. Por defecto es False.

        Returns:
            bool: True si la tabla fue creada exitosamente.

        Example:
            >>> conn.create_table('users', {'id': 'INTEGER PRIMARY KEY', 'name': 'TEXT', 'email': 'TEXT'})
            [i] Tabla 'users' creada exitosamente
            True
        """
        cursor = self._get_cursor()
        
        column_defs = []
        for column_name, data_type in columns.items():
            if not apply_constraints:
                column_defs.append(f"{column_name} {data_type}")
                continue
            _data_type = str(data_type.split(" ")[0])
            match _data_type:
                case "INTEGER":
                    constraint = f"CHECK(typeof({column_name}) = 'integer')"
                case "REAL":
                    constraint = f"CHECK(typeof({column_name}) = 'real')"
                case "NUMERIC":
                    constraint = f"CHECK(typeof({column_name}) IN ('integer', 'real'))"
                case _:
                    constraint = ""
            column_defs.append(f"{column_name} {data_type} {constraint}".strip())

        columns_sql = ", ".join(column_defs)
        query = f"CREATE TABLE {table_name} ({columns_sql})"

        cursor.execute(query)

        print(f"[i] Tabla '{table_name}' creada exitosamente")
        return True

    @require_connection
    @handle_exception
    def add_column(self, table_name: str, column_name: str, column_type: str) -> bool:
        """
        Añade una nueva columna a una tabla existente.

        Args:
            table_name (str): El nombre de la tabla.
            column_name (str): El nombre de la nueva columna.
            column_type (str): El tipo de dato de la nueva columna.

        Returns:
            bool: True si la columna fue añadida exitosamente.

        Example:
            >>> conn.add_column('users', 'age', 'INTEGER')
            [i] Columna 'age' añadida exitosamente a la tabla 'users'
            True
        """
        connection = self._get_connection()
        cursor = self._get_cursor()
        
        query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"

        cursor.execute(query)
        connection.commit()

        print(f"[i] Columna '{column_name}' añadida exitosamente a la tabla '{table_name}'")
        return True
    
    @require_connection
    @handle_exception
    def drop_column(self, table_name: str, column_name: str) -> bool:
        """
        Elimina una columna de una tabla.

        Args:
            table_name (str): El nombre de la tabla.
            column_name (str): El nombre de la columna a eliminar.

        Returns:
            bool: True si la columna fue eliminada exitosamente.

        Example:
            >>> conn.drop_column('users', 'age')
            [i] Columna 'age' eliminada exitosamente de la tabla 'users'
            True
        """
        connection = self._get_connection()
        cursor = self._get_cursor()
        
        columns = self.get_column_names(table_name)
        if column_name not in columns:
            raise ValueError(f"La columna '{column_name}' no existe en la tabla '{table_name}'")

        new_columns = [col for col in columns if col != column_name]
        new_columns_sql = ', '.join(new_columns)

        temp_table_name = f"{table_name}_temp"
        create_temp_table_query = f"CREATE TABLE {temp_table_name} AS SELECT {new_columns_sql} FROM {table_name}"
        cursor.execute(create_temp_table_query)

        drop_table_query = f"DROP TABLE {table_name}"
        cursor.execute(drop_table_query)

        rename_table_query = f"ALTER TABLE {temp_table_name} RENAME TO {table_name}"
        cursor.execute(rename_table_query)

        connection.commit()

        print(f"[i] Columna '{column_name}' eliminada exitosamente de la tabla '{table_name}'")
        return True

    @require_connection
    @handle_exception
    def drop_table(self, table_name: str) -> bool:
        """
        Elimina una tabla de la base de datos.

        Args:
            table_name (str): El nombre de la tabla a eliminar.

        Returns:
            bool: True si la tabla fue eliminada exitosamente.

        Example:
            >>> conn.drop_table('users')
            [i] Tabla 'users' eliminada exitosamente
            True
        """
        connection = self._get_connection()
        cursor = self._get_cursor()
        
        query = f"DROP TABLE IF EXISTS {table_name}"

        cursor.execute(query)
        connection.commit()

        print(f"[i] Tabla '{table_name}' eliminada exitosamente")
        return True

    @require_connection
    @handle_exception
    def custom_query(self, query: str) -> list[tuple[int | float | str, ...]]:
        """
        Ejecuta una consulta personalizada en la base de datos.

        Args:
            query (str): Consulta SQL a ejecutar.

        Returns:
            list[tuple]: Resultado de la consulta.

        Example:
            >>> conn.custom_query('SELECT * FROM users WHERE age > 30')
            [(1, 'John', 35), (2, 'Jane', 40)]
        """
        cursor = self._get_cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return results

    def close(self) -> None:
        """
        Cierra la conexión y el cursor de la base de datos.

        Returns:
            None

        Example:
            >>> conn.close()
        """
        if hasattr(self._local, 'cursor') and self._local.cursor:
            self._local.cursor.close()
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
        
        if hasattr(self._local, 'connection_status'):
            del self._local.connection_status
        if hasattr(self._local, 'connection'):
            del self._local.connection
        if hasattr(self._local, 'cursor'):
            del self._local.cursor
        
        print("[i] Conexión cerrada exitosamente")
