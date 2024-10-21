from sqlite3 import connect, Cursor, Connection
from typing import Any as any, Callable, TypeVar, cast

FuncType = TypeVar('FuncType', bound=Callable)


def handle_exception(function: FuncType) -> FuncType:
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
    def wrapper(self: 'Connect', *args, **kwargs) -> any:
        if not self.get_status():
            print("[!] Debes conectarte primero a una base de datos.")
            return None
        return function(self, *args, **kwargs)
    return cast(FuncType, wrapper)


class Connect:
    path: str
    raise_exceptions: bool
    __connection: Connection
    __cursor: Cursor
    __connection_status: bool = False

    def __init__(self, path: str, raise_exceptions: bool = False) -> None:
        self.path = path
        self.raise_exceptions = raise_exceptions

    def __str__(self) -> str:
        return f"Base de datos: {self.path}\nEstado: {('Sin conexión', 'Conexión establecida')[self.get_status()]}"

    def get_status(self) -> bool:
        return self.__connection_status

    @handle_exception
    def connect(self) -> bool:
        if self.get_status():
            print("[!] Ya estás conectado a una base de datos")
            return False

        self.__connection = connect(self.path)
        self.__cursor = self.__connection.cursor()
        self.__connection_status = True

        print("[i] Conexión exitosa")
        return True

    @require_connection
    @handle_exception
    def list_table_names(self) -> list[str]:
        query = "SELECT name FROM sqlite_master WHERE type='table';"

        self.__cursor.execute(query)
        tables = self.__cursor.fetchall()

        if not tables:
            print("[i] No se encontraron tablas en la base de datos.")
            return []

        return [str(table[0]) for table in tables]

    @require_connection
    @handle_exception
    def get_column_names(self, table_name: str) -> list[str]:
        query = f"PRAGMA table_info({table_name});"

        self.__cursor.execute(query)
        columns = self.__cursor.fetchall()

        if not columns:
            print("[i] No se encontraron columnas en la tabla.")
            return []

        return [str(column[1]) for column in columns]

    @require_connection
    @handle_exception
    def read_table(self, table_name: str) -> list[tuple[int | float | str, ...]]:
        query = f"SELECT * FROM {table_name}"

        self.__cursor.execute(query)
        rows = self.__cursor.fetchall()

        if not rows:
            print("[i] No se encontraron registros en la tabla.")
            return []

        return rows

    @require_connection
    @handle_exception
    def search(self, table_name: str, condition: dict[str, any]) -> list[tuple[int | float | str, ...]]:
        conditions = ' AND '.join([f"{column} = ?" for column in condition.keys()])
        query = f"SELECT * FROM {table_name} WHERE {conditions}"

        self.__cursor.execute(query, tuple(condition.values()))
        rows = self.__cursor.fetchall()

        if not rows:
            print("[i] No se encontraron registros en la tabla que coincidan con los parámetros de búsqueda.")
            return []

        return rows

    @require_connection
    @handle_exception
    def insert(self, table_name: str, data: dict[str, any]) -> bool:
        columns = ', '.join(data.keys())
        values = ', '.join(['?' for _ in range(len(data))])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

        self.__cursor.execute(query, tuple(data.values()))
        self.__connection.commit()

        print("[i] Datos insertados exitosamente")
        return True
    
    @require_connection
    @handle_exception
    def bulk_insert(self, table_name: str, data_list: list[dict[str, any]]) -> bool:
        if not data_list:
            raise ValueError("La lista de datos no puede estar vacía")

        columns = ', '.join(data_list[0].keys())
        values = ', '.join(['?' for _ in data_list[0].keys()])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

        values_list = [tuple(data.values()) for data in data_list]

        self.__cursor.executemany(query, values_list)
        self.__connection.commit()

        print("[i] Registros insertados exitosamente")
        return True


    @require_connection
    @handle_exception
    def update(self, table_name: str, data: dict[str, any], condition: dict[str, any]) -> bool:
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        where_clause = ' AND '.join([f"{key} = ?" for key in condition.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        values = tuple(data.values()) + tuple(condition.values())

        self.__cursor.execute(query, values)
        self.__connection.commit()

        print("[i] Datos actualizados exitosamente")
        return True

    @require_connection
    @handle_exception
    def delete(self, table_name: str, condition: dict[str, any]) -> bool:
        query = f"DELETE FROM {table_name} WHERE " + " AND ".join([f"{field} = ?" for field in condition.keys()])

        self.__cursor.execute(query, tuple(condition.values()))
        self.__connection.commit()

        print("[i] Datos eliminados exitosamente")
        return True

    @require_connection
    @handle_exception
    def create_table(self, table_name: str, columns: dict[str, any], apply_constraints: bool = False) -> bool:
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

        self.__cursor.execute(query)

        print(f"[i] Tabla '{table_name}' creada exitosamente")
        return True

    @require_connection
    @handle_exception
    def add_column(self, table_name: str, column_name: str, column_type: str) -> bool:
        query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"

        self.__cursor.execute(query)
        self.__connection.commit()

        print(f"[i] Columna '{column_name}' añadida exitosamente a la tabla '{table_name}'")
        return True
    
    @require_connection
    @handle_exception
    def drop_column(self, table_name: str, column_name: str) -> bool:
        columns = self.get_column_names(table_name)
        if column_name not in columns:
            raise ValueError(f"La columna '{column_name}' no existe en la tabla '{table_name}'")

        new_columns = [col for col in columns if col != column_name]
        new_columns_sql = ', '.join(new_columns)

        temp_table_name = f"{table_name}_temp"
        create_temp_table_query = f"CREATE TABLE {temp_table_name} AS SELECT {new_columns_sql} FROM {table_name}"
        self.__cursor.execute(create_temp_table_query)

        drop_table_query = f"DROP TABLE {table_name}"
        self.__cursor.execute(drop_table_query)

        rename_table_query = f"ALTER TABLE {temp_table_name} RENAME TO {table_name}"
        self.__cursor.execute(rename_table_query)

        self.__connection.commit()

        print(f"[i] Columna '{column_name}' eliminada exitosamente de la tabla '{table_name}'")
        return True

    @require_connection
    @handle_exception
    def drop_table(self, table_name: str) -> bool:
        query = f"DROP TABLE IF EXISTS {table_name}"

        self.__cursor.execute(query)
        self.__connection.commit()

        print(f"[i] Tabla '{table_name}' eliminada exitosamente")
        return True

    @require_connection
    @handle_exception
    def custom_query(self, query: str) -> list[tuple[int | float | str, ...]]:
        self.__cursor.execute(query)
        results = self.__cursor.fetchall()
        return results

    def close(self) -> None:
        if hasattr(self, '_Connect__cursor') and self.__cursor:
            self.__cursor.close()
        if hasattr(self, '_Connect__connection') and self.__connection:
            self.__connection.close()
        self.__connection_status = False
